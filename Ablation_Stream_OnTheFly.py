### Written by Thom de Hoog
### Last edit: 2023-01-30

#Most usefull variables to change for timelapse
VV.Acquire.TimeLapse.TimePoints = 150
VV.Acquire.ExposureTimeMillisecs = 100
timepoint_before_ablation = 50

#Most usefull variable to change for frap
change_zposition_for_ablation = 0
sparsity_in_roi = 10
cycles = 1
imaging_laser  = 'Ablation-sdcGFP'
ablation_laser = 'Ablation355'

#Settings
import sys
sys.path.append(r'C:\ProgramData\Visitron Systems\VisiView\PythonMacros\Thom Lasercutting')
vvimport('AblationOnTheFly_Functions')
VV.Macro.PrintWindow.IsVisible = True
VV.Macro.PrintWindow.Clear()
basename = VV.Acquire.Sequence.NextBaseName

#Set important settings for the timeseries
VV.Acquire.Stage.Series = False
VV.Acquire.Z.Series = False
VV.Acquire.WaveLength.Series = False
VV.Acquire.TimeLapse.Series = True
VV.Acquire.TimeLapse.TimeIntervalInMillisecs = 0;
VV.Acquire.TimeLapse.Stream.Request = True
VV.HWAutoFocus.Continuous = False
VV.Acquire.EMCCDGain = 300

#Check if the right region of interest is valid
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Window.Regions.Active.IsValid = True
if(VV.Window.Regions.Count == 0):
	sys.exit("No region of interest loaded")
else:
	VV.Edit.Regions.ClearAll()
	VV.Edit.Regions.Load(r'C:\ProgramData\Visitron Systems\VisiView\PythonMacros\Thom Lasercutting\roi_used_for_dorsal_closure_visiview.rgn')
	VV.Edit.Regions.Save(r'Temp_Regions')
	VV.Edit.Regions.Load(r'Temp_Regions')

#Get coordinates of pixels to frap
pixels = getPixelForAblation(sparsity_in_roi)

#Close the windows
VV.Window.CloseAll(True);

#Start the time series
save_timer = []
t0 = timer()
VV.Acquire.Sequence.Start()

#Make sure the right laser for imaging is selected
VV.Illumination.Active = imaging_laser
VV.Illumination.ActiveShuttersOpen = True

#Apply the Frap and Register the elapsed time
tp = 0
first_time_loop = True
time_per_timepoint = []
save_timer.append("Before Ablation ("+imaging_laser+")")
while VV.Acquire.Sequence.IsRunning:
	
	#Load the region of interest as soon as possible
	try:
		if(roi_loaded == False):
			VV.Window.Selected.Handle = VV.Window.Active.Handle
			VV.Edit.Regions.Load(r'Temp_Regions')
			VV.Window.Regions.Active.IsValid = True
			roi_loaded = True			
			
	except:
		roi_loaded = False
	
	#Check the current time point
	if VV.Acquire.TimeLapse.FinishedTimePoints > tp:
		
		#Record the time for this timepoint
		t1 = timer()		
	
		#Process time info for this timepoint
		timepoint = 'Time_start_timepoint_' + str(VV.Acquire.TimeLapse.FinishedTimePoints+1) + ':  \t' + str(timedelta(seconds=t1-t0)) + 'sec'
		print(timepoint)
		save_timer.append(timepoint)
		
		#make sure this statement happens only one time per timepoint
		tp = VV.Acquire.TimeLapse.FinishedTimePoints		

		#If the current time point is 2 start the frap sequence
		if 	VV.Acquire.TimeLapse.FinishedTimePoints == (timepoint_before_ablation-2):
		
			#The loop is faster then the FinishedTimePoint variable changes
			if first_time_loop == True:
			
				#Record time before ablation
				delay = VV.Acquire.ExposureTimeMillisecs - ((VV.Frap.OnTheFlyTimePerPointMS/2)+ 10)
				VV.Macro.Control.Delay(delay,'ms');
			
				start_ablation = timer()
			
				#Refocus the stage to cut in a different Z-position if needs
				if(change_zposition_for_ablation != 0):
					VV.Focus.ZPosition = VV.Focus.ZPosition + change_zposition_for_ablation
					VV.Macro.Control.WaitFor('VV.Focus.IsMoving', '==', False)
			
				#Start Frap			
				exposure_time = []			
				for i in range(0, cycles):
					for j in range(0, len(pixels[0])):
					
						#Record start time current pixel
						start_ablation_pixel = timer()
					
						VV.Frap.StartOnFly(pixels[0][j], pixels[1][j])
				
						#Wait until ablation is don
						while VV.Frap.IsRunning:
							wait = True
					
						#Record end time current pixel					
						end_ablation_pixel = timer()
					
						#Format output					
						exposure_time.append(('Ablation exposure cycle '+str(i+1)+', pixel ' + str(j+1) + ':\t' + str(end_ablation_pixel - start_ablation_pixel) + 'sec (' + str(timedelta(seconds=start_ablation_pixel-t0)) + ' - ' + str(timedelta(seconds=end_ablation_pixel-t0)) + 'sec)'))
								
				#Restore the stage position after Frap, when ablation was applied in different Z-position
				if(change_zposition_for_ablation != 0):
					VV.Focus.ZPosition = VV.Focus.ZPosition - change_zposition_for_ablation
					VV.Macro.Control.WaitFor('VV.Focus.IsMoving', '==', False)
				
				#Record time after ablation	
				end_ablation = timer()
				exposure_time.append('Total ablation exposure:\t\t' + str(end_ablation - start_ablation) + 'sec (' + str(timedelta(seconds=start_ablation-t0)) + ' - ' + str(timedelta(seconds=end_ablation-t0)) + 'sec)')
			
				#Format output
				print("")
				before = 'Time_Start_ablation:    \t' + str(timedelta(seconds=start_ablation-t0)) + ' sec';
				after = 'Time_End_ablation:     \t' + str(timedelta(seconds=end_ablation-t0)) + ' sec';
				print("")
				print(before)
				print(after)
				print("")
				save_timer.append("")
				save_timer.append("Ablating ("+ablation_laser+")")
				save_timer.append(before)
				save_timer.append(after)
				save_timer.append("")
				save_timer.append("After Ablation ("+imaging_laser+")")
			
				#Make sure the if statement is only true once
				first_time_loop = False


#Save the coordinates of active region
roi = []
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Window.Regions.Active.IsValid = True
VV.Edit.Regions.Load(r'Temp_Regions')
roi.append('Roi type:\t\t\t\t' + str(VV.Window.Regions.Active.Type))
roi.append('Roi left coordinate in pixels:\t\t' + str(VV.Window.Regions.Active.Left))
roi.append('Roi top coordinate in pixels:\t\t' + str(VV.Window.Regions.Active.Top))
roi.append('Roi width in pixels:\t\t\t' + str(VV.Window.Regions.Active.Width))
roi.append('Roi height in pixels:\t\t' + str(VV.Window.Regions.Active.Height))
roi.append('Sparity of pixels:\t\t\t' + str(sparsity_in_roi) )
roi.append('Ablation cycles:\t\t\t' + str(cycles) )
roi.append('Number of ablated pixels:\t\t' + str(len(pixels[0])) )
roi.append('X-coordinates of ablated pixels:\t' + str(pixels[0]) )
roi.append('Y-coordinates of ablated pixels:\t' + str(pixels[1]) )
roi.append('Target millisecond exposure:\t\t' + str(VV.Frap.OnTheFlyTimePerPointMS) )
for i in range(len(exposure_time)):
	roi.append(exposure_time[i])
	
with open((VV.Acquire.Sequence.Directory + '\\' + basename + '_roi_coordinates.txt'), 'w') as f:
	for roi_info in roi:
		f.write(roi_info)
		f.write('\n')
f.close()

#Save Roi as a format that is readble by Visiview (.rgn)
regionName = VV.Acquire.Sequence.Directory + '/' + basename +  'roi_for_visiview.rgn'
VV.Edit.Regions.Save(regionName)

#Only move on when image sequence is done
VV.Macro.Control.WaitFor('VV.Acquire.Sequence.IsRunning','==',False)

#Write timestamps to a tex file
with open((VV.Acquire.Sequence.Directory + '\\' + basename + '_timestamps.txt'), 'w') as f:
	for time in save_timer:
		f.write(time)
		f.write('\n')
f.close()

#Start live
VV.Acquire.StartLive()
VV.Macro.Control.WaitFor('VV.Acquire.LiveIsRunning','==', True);
VV.Illumination.Active = imaging_laser
VV.Illumination.ActiveShuttersOpen = True
VV.Macro.Control.WaitFor('VV.Acquire.LiveIsRunning','==', True);

#Load roi
window_ready = False
while window_ready == False:
	try:
		VV.Window.Selected.Handle = VV.Window.Active.Handle
		VV.Edit.Regions.Load(r'Temp_Regions')
		window_ready = True
	except:
		window_ready = False

print(exposure_time)

print(delay)
