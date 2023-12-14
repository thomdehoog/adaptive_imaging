from timeit import default_timer as timer
from datetime import timedelta

##print(VV.Acquire.Sequence.NextBaseName)
VV.Macro.PrintWindow.IsVisible = True
VV.Macro.PrintWindow.Clear()

##Set important settings for the timeseries
VV.Acquire.Stage.Series = False
VV.Acquire.Z.Series = False
VV.Acquire.WaveLength.Series = False
VV.Acquire.TimeLapse.Series = True
VV.Acquire.TimeLapse.TimePoints = 100
VV.Acquire.ExposureTimeMillisecs = 100
VV.Acquire.EMCCDGain = 300
VV.Frap.TimePerPointMS = 10
VV.Acquire.TimeLapse.Stream.Request = True
VV.Frap.Initialize ()

#Start the time series
save_timer = []
t0 = timer()
VV.Acquire.Sequence.Start()

#Apply the Frap and register the elapsed time
tp = 0
first_time_loop = True
while VV.Acquire.Sequence.IsRunning:

	#Check the current time point
	if VV.Acquire.TimeLapse.FinishedTimePoints > tp:
		
		tp = tp + 1
		t1 = timer()
		timepoint = 'Time_after_timepoint_' + str(tp) + ':\t' + str(timedelta(seconds=t1-t0)) + 'sec'
		print(timepoint)
		save_timer.append(timepoint)	

	#If the current time point is 2 start the frap sequence
	if 	VV.Acquire.TimeLapse.FinishedTimePoints == 2:
		
		#Load region of interest
		VV.Window.Selected.Handle = VV.Window.Active.Handle
		VV.Edit.Regions.Load(r'Temp_Regions')	
		
		#The loop is faster then the FinishedTimePoint variable changes
		if first_time_loop == True:
			t_before_ablation = timer()
			
			VV.Focus.ZPosition = VV.Focus.ZPosition + 10
			#Check if Z is still moving
			VV.Macro.Control.WaitFor('VV.Focus.IsMoving','==',False)
				
			VV.Frap.Start()
			#Check if ablation is still running
			VV.Macro.Control.WaitFor('VV.Frap.IsRunning','==',False)
				
			VV.Focus.ZPosition = VV.Focus.ZPosition - 10
			#Check if Z is still moving
			VV.Macro.Control.WaitFor('VV.Focus.IsMoving','==',False)
				
			t_after_ablation = timer()
			
			before = 'Time_Before_ablation:\t' + str(timedelta(seconds=t_before_ablation-t0)) + 'sec';
			after = 'Time_After_ablation:\t' + str(timedelta(seconds=t_after_ablation-t0)) + 'sec';
			print(before)
			print(after)
			save_timer.append(before)
			save_timer.append(after)
			first_time_loop = False

VV.Macro.Control.WaitFor('VV.Acquire.Sequence.IsRunning','==',False)

#Write timestamps to a tex file
with open((VV.Acquire.Sequence.Directory + '\\' + VV.Acquire.Sequence.BaseName + '_timestamps.txt'), 'w') as f:
	for time in save_timer:
		f.write(time)
		f.write('\n')
f.close()

#Load region of interest in case it got lost
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Edit.Regions.Load(r'Temp_Regions')

#Get region of interest coordinates
roi = []
roi.append('Region_of_interest_type:\t' + str(VV.Window.Regions.Active.Type))
roi.append('Left_coordinate_in_pixels:\t' + str(VV.Window.Regions.Active.Left))
roi.append('Top_coordinate_in_pixels:\t' + str(VV.Window.Regions.Active.Top))
roi.append('Width_in_pixels:\t' + str(VV.Window.Regions.Active.Width))
roi.append('Height_in_pixels:\t' + str(VV.Window.Regions.Active.Height))

#Write region of interest coordinates to a txt file
with open((VV.Acquire.Sequence.Directory + '\\' + VV.Acquire.Sequence.BaseName + '_regionofinterest.txt'), 'w') as f:
	for r in roi:
		f.write(r)
		f.write('\n')
f.close()