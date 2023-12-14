# VisiView Macro
#Check if the right region of interest is valid
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Window.Regions.Active.IsValid = True
VV.Edit.Regions.ClearAll()
VV.Edit.Regions.Load(r'C:\ProgramData\Visitron Systems\VisiView\PythonMacros\Thom Lasercutting\roi_used_for_dorsal_closure_visiview.rgn')
VV.Edit.Regions.Save(r'Temp_Regions')
VV.Edit.Regions.Load(r'Temp_Regions')