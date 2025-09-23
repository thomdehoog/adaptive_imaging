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
imaging_laser  = 'Ablation-Brightfield-ForCalibration'

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
	VV.Edit.Regions.Save(r'Temp_Regions')
	VV.Edit.Regions.Load(r'Temp_Regions')

#Get coordinates of pixels to frap
pixels = getPixelForAblation(sparsity_in_roi)
			
#Refocus the stage to cut in a different Z-position if needs
if(change_zposition_for_ablation != 0):
	VV.Focus.ZPosition = VV.Focus.ZPosition + change_zposition_for_ablation
	VV.Macro.Control.WaitFor('VV.Focus.IsMoving', '==', False)
	
#Record time before ablation
t_before_ablation = timer()

#Start Frap			
exposure_time = []			
start_ablation = timer()
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
		exposure_time.append(('Cycle '+str(i+1)+', pixel ' + str(j+1) + ':      ' + str(end_ablation_pixel - start_ablation_pixel) + ' sec'))								
		end_ablation = timer()
			
		exposure_time.append('Ablation exposure:     ' + str(end_ablation - start_ablation) + ' sec')
stop_ablation = timer()			
#Change imaging window back			
VV.Illumination.Active = imaging_laser
VV.Illumination.ActiveShuttersOpen = True
VV.Macro.Control.WaitFor('VV.Illumination.IsChanging', '==', False)
			
#Restore the stage position after Ablation, when ablation was applied in different Z-position
if(change_zposition_for_ablation != 0):
	VV.Focus.ZPosition = VV.Focus.ZPosition - change_zposition_for_ablation
	VV.Macro.Control.WaitFor('VV.Focus.IsMoving', '==', False)
		
			
#Save the coordinates of active region
roi = []
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Window.Regions.Active.IsValid = True
VV.Edit.Regions.Load(r'Temp_Regions')
print('Roi type:              ' + str(VV.Window.Regions.Active.Type))
print('Sparity of pixels:     ' + str(sparsity_in_roi) )
print('Ablation cycles:       ' + str(cycles) )
print('Pixels ablated:        ' + str(len(pixels[0])) )
print('X-coor pixels:         ' + str(pixels[0]) )
print('Y-coor pixels:         ' + str(pixels[1]) )
print('Target ms exposure:    ' + str(VV.Frap.OnTheFlyTimePerPointMS) )
for i in range(len(exposure_time)):
	print(exposure_time[i])
print("")

print('Total ablation time    ' + str(stop_ablation - start_ablation) + ' sec')
