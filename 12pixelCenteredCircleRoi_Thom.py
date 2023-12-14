# VisiView Macro
VV.Acquire.StartSingleShot()
VV.Macro.Control.WaitFor('VV.Acquire.IsRunning','==',False)
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Window.Regions.AddByPositions('Circle',[506,518],[506,518])
VV.Window.Selected.Handle = VV.Window.Active.Handle
VV.Edit.Regions.Save(r'Temp_Regions')