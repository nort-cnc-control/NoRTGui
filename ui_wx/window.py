import common.event as event

import wx
import wx.stc
import wx.richtext
import wx.grid

class CNCWindow(wx.Frame):

        def __kd(self, arg):
            keycode = arg.GetKeyCode()
            if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
                cmd = self.command.GetValue()
                self.command_entered(cmd.strip())
                self.command.SetValue("")
                self.SetManualInputFocus()
            arg.Skip()

        def OnNew(self, e):
            self.newfile()

        def OnOpen(self, e):
            with wx.FileDialog(self, "Open G-Code", wildcard="GCODE files (*.gcode)|*.gcode|All files|*", \
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as ofd:
                if ofd.ShowModal() == wx.ID_CANCEL:
                    return
                file = ofd.Paths[0]
                self.loadfile(file)

        def OnSave(self, e):
            with wx.FileDialog(self, "Save G-Code", wildcard="GCODE files (*.gcode)|*.gcode|All files|*", \
                       style=wx.FD_SAVE) as ofd:
                if ofd.ShowModal() == wx.ID_CANCEL:
                    return
                file = ofd.Paths[0]
                self.savefile(file, self.code.GetValue())

        def OnQuit(self, e):
            self.Close()

        def OnStartHere(self, event):
            pass
        
        def OnEndHere(self, event):
            pass

        def OnShowPopup(self, event):
            pos = event.GetPosition()
            pos = self.code.ScreenToClient(pos)
            self.code.PopupMenu(self.gcodemenu, pos)

        def __init__(self, parent):
            self.newfile = event.EventEmitter()
            self.loadfile = event.EventEmitter()
            self.savefile = event.EventEmitter()

            self.stop_clicked = event.EventEmitter()
            self.start_clicked = event.EventEmitter()
            self.continue_clicked = event.EventEmitter()
            self.pause_clicked = event.EventEmitter()
            self.home_clicked = event.EventEmitter()
            self.probe_clicked = event.EventEmitter()

            self.command_entered = event.EventEmitter()
            self.line_clicked = event.EventEmitter()

            wx.Frame.__init__(self, parent, title="CNC Control", size=(800,600))
            
            #region menu
            menubar = wx.MenuBar()
            fileMenu = wx.Menu()
            newItem  = fileMenu.Append(wx.ID_NEW,  'New',  'New G-Code')
            openItem = fileMenu.Append(wx.ID_OPEN, 'Open', 'Open G-Code')
            saveItem = fileMenu.Append(wx.ID_SAVE, 'Save', 'Save G-Code')
            quitItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
            menubar.Append(fileMenu, '&File')
            self.SetMenuBar(menubar)
            self.Bind(wx.EVT_MENU, self.OnNew, newItem)
            self.Bind(wx.EVT_MENU, self.OnOpen, openItem)
            self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
            self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)
            #endregion menu

            # root:
            panel_root = wx.Panel(self)
            vbox_root = wx.BoxSizer(wx.VERTICAL)
            panel_root.SetSizer(vbox_root)

            # main: left - control: code & manual, right - status
            panel_main = wx.Panel(panel_root)
            vbox_root.Add(panel_main,flag=wx.EXPAND,proportion=1)

            hbox_main = wx.BoxSizer(wx.HORIZONTAL)
            panel_main.SetSizer(hbox_main)

            # control: top - gcode: program & manual input, bottom - buttons
            panel_control = wx.Panel(panel_root)
            hbox_main.Add(panel_control,flag=wx.EXPAND,proportion=1)
            
            vbox_control = wx.BoxSizer(wx.VERTICAL)
            panel_control.SetSizer(vbox_control)
            
            # gcode: left - program, right - manual input
            panel_gcode = wx.Panel(panel_control)
            vbox_control.Add(panel_gcode,flag=wx.EXPAND,proportion=1)

            hbox_gcode = wx.BoxSizer(wx.HORIZONTAL)
            panel_gcode.SetSizer(hbox_gcode)

            # program: styledtext
            self.indicator_error = 8
            self.indicator_active = 9
            self.indicator_start = 10
            self.indicator_finish = 11

            self.code = wx.stc.StyledTextCtrl(panel_gcode, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
            self.codefont = wx.Font(13, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Monospace')
            
#            self.code.IndicatorSetStyle(self.indicator_error, wx.stc.STC_INDIC_SQUIGGLE)
#            self.code.IndicatorSetForeground(self.indicator_error, wx.Colour(255, 0, 0))

#            self.code.IndicatorSetStyle(self.indicator_start, wx.stc.STC_INDIC_SQUIGGLE)
#            self.code.IndicatorSetForeground(self.indicator_start, wx.Colour(255, 255, 0))

            hbox_gcode.Add(self.code,flag=wx.EXPAND,proportion=1)

            self.gcodemenu = wx.Menu()
            itemstart = self.gcodemenu.Append(-1, "Start here")
            self.Bind(wx.EVT_MENU, self.OnStartHere, itemstart)
            itemend = self.gcodemenu.Append(-1, "End here")
            self.Bind(wx.EVT_MENU, self.OnEndHere, itemend)
            
            self.code.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        
            # manual input: top - log, bottom : input
            panel_manual = wx.Panel(panel_gcode)
            panel_manual.SetMinSize((250,-1))
            hbox_gcode.Add(panel_manual,proportion=0,flag=wx.EXPAND)
            
            vbox_manual = wx.BoxSizer(wx.VERTICAL)
            panel_manual.SetSizer(vbox_manual)

            # log: text control, readonly
            self.commandlog = wx.TextCtrl(panel_manual, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.TE_RICH)
            vbox_manual.Add(self.commandlog,flag=wx.EXPAND,proportion=1)

            # input: text input
            self.command = wx.TextCtrl(panel_manual)
            self.command.Bind(wx.EVT_KEY_DOWN, self.__kd)
            vbox_manual.Add(self.command, flag=wx.EXPAND)

            # space
            hbox_main.Add((5, -1))

            #status: region
            panel_status = wx.Panel(panel_root)
            hbox_main.Add(panel_status,proportion=0)

            vbox_status = wx.BoxSizer(wx.VERTICAL)
            panel_status.SetSizer(vbox_status)
            
            # coordinates block
            panel_coordinates = wx.Panel(panel_status)
            vbox_status.Add(panel_coordinates)

            vbox_coordinates = wx.BoxSizer(wx.VERTICAL)
            panel_coordinates.SetSizer(vbox_coordinates)

            # coordinates caption
            lb = wx.StaticText(panel_coordinates, label="Coordinates")
            vbox_coordinates.Add(lb, flag=wx.ALIGN_LEFT)

            # coordinates
            self.crds = wx.grid.Grid(panel_coordinates)
            vbox_coordinates.Add(self.crds)
            self.crds.CreateGrid(3, 3)
            for i in range(3):
                for j in range(3):
                    self.crds.SetReadOnly(i, j, True)

            self.crds.SetColLabelValue(0, "Hardware")
            self.crds.SetColLabelValue(1, "Global")
            self.crds.SetColLabelValue(2, "Local")

            self.crds.SetRowLabelValue(0, "X")
            self.crds.SetRowLabelValue(1, "Y")
            self.crds.SetRowLabelValue(2, "Z")

            self.crds.DisableRowResize(0)
            self.crds.DisableRowResize(1)
            self.crds.DisableRowResize(2)
            
            self.crds.DisableColResize(0)
            self.crds.DisableColResize(1)
            self.crds.DisableColResize(2)

            vbox_status.Add((-1, 20))

            # movement block
            panel_movement = wx.Panel(panel_status)
            vbox_status.Add(panel_movement)

            vbox_movement = wx.BoxSizer(wx.VERTICAL)
            panel_movement.SetSizer(vbox_movement)

            # movement caption
            lb = wx.StaticText(panel_movement, label="Movement")
            vbox_movement.Add(lb, flag=wx.ALIGN_LEFT)

            # movement
            self.movement = wx.grid.Grid(panel_movement)
            vbox_movement.Add(self.movement)
            self.movement.CreateGrid(3, 1)
            self.movement.HideColLabels()
            for i in range(3):
                for j in range(1):
                    self.movement.SetReadOnly(i, j, True)
            
            self.movement.SetRowLabelValue(0, "Status")
            self.movement.SetRowLabelValue(1, "Command")
            self.movement.SetRowLabelValue(2, "Feed")

            self.movement.DisableRowResize(0)
            self.movement.DisableRowResize(1)
            self.movement.DisableRowResize(2)
            
            self.movement.DisableColResize(0)

            vbox_status.Add((-1, 20))

            # spindel block
            panel_spindel = wx.Panel(panel_status)
            vbox_status.Add(panel_spindel)

            vbox_spindel = wx.BoxSizer(wx.VERTICAL)
            panel_spindel.SetSizer(vbox_spindel)

            # spindel caption
            lb = wx.StaticText(panel_spindel, label="Spindel")
            vbox_spindel.Add(lb, flag=wx.ALIGN_LEFT)

            # spindel
            self.spindel = wx.grid.Grid(panel_spindel)
            vbox_spindel.Add(self.spindel)
            self.spindel.CreateGrid(3, 1)
            self.spindel.HideColLabels()
            for i in range(3):
                for j in range(1):
                    self.spindel.SetReadOnly(i, j, True)
            
            self.spindel.SetRowLabelValue(0, "Status")
            self.spindel.SetRowLabelValue(1, "Direction")
            self.spindel.SetRowLabelValue(2, "Speed")

            self.spindel.DisableRowResize(0)
            self.spindel.DisableRowResize(1)
            self.spindel.DisableRowResize(2)
            
            self.spindel.DisableColResize(0)

            # space
            hbox_main.Add((5, -1))

            # space
            vbox_root.Add((-1,5))
            # buttons:
            panel_buttons = wx.Panel(panel_root)
            vbox_root.Add(panel_buttons,proportion=0)

            hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
            panel_buttons.SetSizer(hbox_buttons)

            self.stop_btn = wx.Button(panel_buttons, label='STOP')
            self.stop_btn.SetBackgroundColour(wx.Colour(255, 0, 0))
            self.stop_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            self.stop_btn.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD))
    
            hbox_buttons.Add(self.stop_btn, flag=wx.EXPAND)
            self.stop_btn.Bind(wx.EVT_BUTTON, lambda e : self.stop_clicked())

            hbox_buttons.Add((20, -1))

            self.start_btn = wx.Button(panel_buttons, label='Start')
            hbox_buttons.Add(self.start_btn, flag=wx.EXPAND)
            self.start_btn.Bind(wx.EVT_BUTTON, lambda e : self.start_clicked())

            hbox_buttons.Add((5, -1))

            self.continue_btn = wx.Button(panel_buttons, label='Continue')
            hbox_buttons.Add(self.continue_btn, flag=wx.EXPAND)
            self.continue_btn.Bind(wx.EVT_BUTTON, lambda e : self.continue_clicked())

            hbox_buttons.Add((5, -1))

            self.pause_btn = wx.Button(panel_buttons, label='Pause')
            hbox_buttons.Add(self.pause_btn, flag=wx.EXPAND)
            self.pause_btn.Bind(wx.EVT_BUTTON, lambda e : self.pause_clicked())

            hbox_buttons.Add((20, -1))
            
            self.home_btn = wx.Button(panel_buttons, label='Home XYZ')
            hbox_buttons.Add(self.home_btn, flag=wx.EXPAND)
            self.home_btn.Bind(wx.EVT_BUTTON, lambda e : self.home_clicked())

            hbox_buttons.Add((5, -1))

            self.probe_btn = wx.Button(panel_buttons, label='Probe Z')
            hbox_buttons.Add(self.probe_btn, flag=wx.EXPAND)
            self.probe_btn.Bind(wx.EVT_BUTTON, lambda e : self.probe_clicked())


        def SetCoordinates(self, hw, glob, loc, cs):
            self.crds.SetColLabelValue(2, "Local (%s)" % cs)
            for i in range(3):
                self.crds.SetCellValue(i, 0, "%0.4f" % hw[i])
                self.crds.SetCellValue(i, 1, "%0.4f" % glob[i])
                self.crds.SetCellValue(i, 2, "%0.4f" % loc[i])

        def SetMovementStatus(self, status):
            self.movement.SetCellValue(0, 0, str(status))
        
        def SetMovementCommand(self, command):
            self.movement.SetCellValue(1, 0, command)

        def SetMovementFeed(self, feed):
            self.movement.SetCellValue(2, 0, str(feed))

        def SetSpindelStatus(self, status):
            self.spindel.SetCellValue(0, 0, str(status))
        
        def SetSpindelDirection(self, direction):
            self.spindel.SetCellValue(1, 0, direction)

        def SetSpindelSpeed(self, speed):
            self.spindel.SetCellValue(2, 0, str(speed))

        def DisplayGCode(self, gcode):
            self.code.SetValue(gcode)

        def GetGCode(self):
            return self.code.GetValue()

        def AddCommandLog(self, cmd):
            oldval = self.commandlog.GetValue()
            if oldval == "":
                self.commandlog.SetValue(cmd)
            else:
                self.commandlog.SetValue(oldval + "\n" + cmd)

        def ClearCommandLog(self):
            self.commandlog.SetValue("")

        def SetManualInputFocus(self):
            self.command.SetFocus()

        def SelectActiveLine(self, id):
            pass

        def SelectStartLine(self, id):
            pass

        def SelectStopLine(self, id):
            pass
