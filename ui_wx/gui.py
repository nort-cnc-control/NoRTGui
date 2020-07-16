import ui_wx.window
import wx

class Interface(object):


    def __init__(self):
        self.app = wx.App()
        self.window = ui_wx.window.CNCWindow(None)
        self.window.Show(True)

        self.newfile  = self.window.newfile
        self.loadfile = self.window.loadfile
        self.savefile = self.window.savefile

        self.stop_clicked        = self.window.stop_clicked
        self.start_clicked       = self.window.start_clicked
        self.continue_clicked    = self.window.continue_clicked
        self.pause_clicked       = self.window.pause_clicked

        self.home_clicked        = self.window.home_clicked
        self.probe_clicked       = self.window.probe_clicked

        self.command_entered     = self.window.command_entered

        self.SelectActiveLine    = self.window.SelectActiveLine
        self.SelectStartLine     = self.window.SelectStartLine
        self.SelectStopLine      = self.window.SelectStopLine

        self.DisplayGCode        = self.window.DisplayGCode
        self.GetGCode            = self.window.GetGCode

        self.SetCoordinates      = self.window.SetCoordinates

        self.SetMovementStatus   = self.window.SetMovementStatus
        self.SetMovementCommand  = self.window.SetMovementCommand
        self.SetMovementFeed     = self.window.SetMovementFeed

        self.SetSpindelStatus    = self.window.SetSpindelStatus
        self.SetSpindelSpeed     = self.window.SetSpindelSpeed
        self.SetSpindelDirection = self.window.SetSpindelDirection

        self.command_entered     += self.__on_command_entered

    def __on_command_entered(self, cmd):
        self.window.AddCommandLog(cmd)

    def ShowOk(self, text):
        wx.MessageBox(text, 'Message', wx.OK | wx.ICON_INFORMATION)

    def Switch2InitialMode(self):
        self.window.start_btn.Enable()
        self.window.continue_btn.Disable()
        self.window.pause_btn.Disable()
        self.window.home_btn.Enable()
        self.window.probe_btn.Enable()
        self.window.command.Enable()
        self.window.command.SetFocus()
        self.window.code.Enable()

    def Switch2PausedMode(self):
        self.window.start_btn.Disable()
        self.window.continue_btn.Enable()
        self.window.pause_btn.Disable()
        self.window.home_btn.Disable()
        self.window.probe_btn.Enable()
        self.window.command.Enable()
        self.window.command.SetFocus()
        self.window.code.Enable()

    def Switch2RunningMode(self):
        self.window.start_btn.Disable()
        self.window.continue_btn.Disable()
        self.window.pause_btn.Disable()
        self.window.home_btn.Disable()
        self.window.probe_btn.Disable()
        self.window.command.Disable()
        self.window.code.Disable()

    def run(self):
        self.app.MainLoop()
