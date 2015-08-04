# Sorry if it looks messy

import sys
import subprocess
import _winreg
import ctypes

import wx
import win32serviceutil
import pywintypes


class WinFrame(wx.Frame):
    def __init__(self, parent, title):
        super(WinFrame, self).__init__(parent, title=title, size=[375, 215],
                                       style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        wxpanel = wx.Panel(self)

        self.debug = wx.TextCtrl(wxpanel, wx.ID_ANY, size=(349, 92),
                                 style=wx.TE_MULTILINE | wx.TE_READONLY, pos=(10, 84))

        self.redir = RedirectText(self.debug)
        sys.stdout = self.redir

        if ctypes.windll.shell32.IsUserAnAdmin() != 1:
            self.warn = wx.MessageDialog(parent=wxpanel,
                                         message="Program requires elevation, please run it as an administrator",
                                         caption="ERROR", style=wx.OK | wx.ICON_WARNING)
            self.warn.ShowModal()
            self.warn.Destroy()
            sys.exit()

        self.icon = wx.Icon(r"c:\windows\system32\shell32.dll;315", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        self.telebox = wx.CheckBox(wxpanel, label="Disable Telemetry", pos=(10, 15))
        self.telebox.Set3StateValue(0)

        self.diagbox = wx.CheckBox(wxpanel, label="Clear DiagTrack log", pos=(10, 45))
        self.diagbox.Set3StateValue(0)

        self.hostbox = wx.CheckBox(wxpanel, label="Block tracking servers with HOSTS file", pos=(10, 60))
        self.hostbox.Set3StateValue(0)

        self.servicebox = wx.CheckBox(wxpanel, label="Services", pos=(10, 30))
        self.servicebox.Set3StateValue(0)
        self.servicebox.Bind(wx.EVT_CHECKBOX, self.serviceradcheck)

        self.servicerad = wx.RadioBox(wxpanel, label="Service Method", pos=(135, 10), choices=["Disable", "Delete"])
        self.servicerad.Disable()

        self.okbutton = wx.Button(wxpanel, -1, "Go Private!", (275, 25))
        self.Bind(wx.EVT_BUTTON, self.onok, self.okbutton)
        self.Centre()
        self.Show()

    def serviceradcheck(self, event):
        self.servicerad.Enable(self.servicebox.IsChecked())  # If Service box is ticked enable Service radio box

    def onok(self, event):
        if self.telebox.IsChecked():
            self.telekeypath = r'SOFTWARE\Policies\Microsoft\Windows\DataCollection'  # Path to Telemetry key

            try:
                self.telekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.telekeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.telekey, "AllowTelemetry", 0, _winreg.REG_SZ, "0")  # Disable Telemetry
                _winreg.CloseKey(self.telekey)
                print "Telemetry key succesfully modified."
            except WindowsError:
                print "Unable to modify Telemetry key. Deleted, or is the program not elevated?"

        if self.diagbox.IsChecked():
            try:
                open('C:\ProgramData\Microsoft\Diagnosis\ETLLogs\AutoLogger\AutoLogger-Diagtrack-Listener.etl',
                     'w').close()  # Clear the AutoLogger file
                subprocess.Popen(
                    "echo y|cacls C:\ProgramData\Microsoft\Diagnosis\ETLLogs\AutoLogger\AutoLogger-Diagtrack-Listener.etl /d SYSTEM",
                    shell=True)  # Prevent modification to file
                print "DiagTrack log succesfully cleared and locked."
            except IOError:
                print "Unable to clear DiagTrack log. Deleted, or is the program not elevated?"

        if self.hostbox.IsChecked():
            self.MSHosts = "\r\n0.0.0.0 vortex.data.microsoft.com\r\n0.0.0.0 vortex-win.data.microsoft.com\r\n" \
                           "0.0.0.0 telecommand.telemetry.microsoft.com\r\n0.0.0.0 telecommand.telemetry.microsoft.com.nsatc.net\r\n" \
                           "0.0.0.0 oca.telemetry.microsoft.com\r\n0.0.0.0 oca.telemetry.microsoft.com.nsatc.net\r\n" \
                           "0.0.0.0 sqm.telemetry.microsoft.com\r\n0.0.0.0 sqm.telemetry.microsoft.com.nsatc.net\r\n" \
                           "0.0.0.0 watson.telemetry.microsoft.com\r\n0.0.0.0 watson.telemetry.microsoft.com.nsatc.net\r\n" \
                           "0.0.0.0 redir.metaservices.microsoft.com\r\n0.0.0.0 choice.microsoft.com\r\n" \
                           "0.0.0.0 choice.microsoft.com.nsatc.net\r\n0.0.0.0 df.telemetry.microsoft.com\r\n" \
                           "0.0.0.0 reports.wes.df.telemetry.microsoft.com\r\n0.0.0.0 wes.df.telemetry.microsoft.com\r\n" \
                           "0.0.0.0 services.wes.df.telemetry.microsoft.com\r\n0.0.0.0 sqm.df.telemetry.microsoft.com\r\n" \
                           "0.0.0.0 telemetry.microsoft.com\r\n0.0.0.0 watson.ppe.telemetry.microsoft.com\r\n" \
                           "0.0.0.0 telemetry.appex.bing.net\r\n0.0.0.0 telemetry.urs.microsoft.com\r\n" \
                           "0.0.0.0 telemetry.appex.bing.net:443\r\n0.0.0.0 settings-sandbox.data.microsoft.com\r\n" \
                           "0.0.0.0 vortex-sandbox.data.microsoft.com\r\n0.0.0.0 survey.watson.microsoft.com\r\n" \
                           "0.0.0.0 watson.live.com\r\n0.0.0.0 watson.microsoft.com\r\n0.0.0.0 statsfe2.ws.microsoft.com\r\n" \
                           "0.0.0.0 corpext.msitadfs.glbdns2.microsoft.com\r\n0.0.0.0 compatexchange.cloudapp.net\r\n" \
                           "0.0.0.0 cs1.wpc.v0cdn.net\r\n0.0.0.0 a-0001.a-msedge.net\r\n" \
                           "0.0.0.0 statsfe2.update.microsoft.com.akadns.net\r\n0.0.0.0 sls.update.microsoft.com.akadns.net\r\n" \
                           "0.0.0.0 fe2.update.microsoft.com.akadns.net\r\n0.0.0.0 65.55.108.23 \r\n0.0.0.0 65.39.117.230\r\n" \
                           "0.0.0.0 23.218.212.69 \r\n0.0.0.0 134.170.30.202\r\n0.0.0.0 137.116.81.24\r\n" \
                           "0.0.0.0 diagnostics.support.microsoft.com\r\n0.0.0.0 corp.sts.microsoft.com\r\n" \
                           "0.0.0.0 statsfe1.ws.microsoft.com\r\n0.0.0.0 pre.footprintpredict.com\r\n0.0.0.0 204.79.197.200\r\n" \
                           "0.0.0.0 23.218.212.69\r\n0.0.0.0 i1.services.social.microsoft.com\r\n" \
                           "0.0.0.0 i1.services.social.microsoft.com.nsatc.net\r\n0.0.0.0 feedback.windows.com\r\n" \
                           "0.0.0.0 feedback.microsoft-hohm.com\r\n0.0.0.0 feedback.search.microsoft.com"  # Known MS Tracking domains
            try:
                with open('C:\Windows\System32\drivers\etc\hosts', 'ab') as f:
                    f.write(self.MSHosts)
                print "Domains successfully appended to HOSTS file."
            except WindowsError:
                print "Could not access HOSTS file. Is the program not elevated?"

        if self.servicerad.Selection == 1 and self.servicebox.IsChecked():
            try:
                win32serviceutil.RemoveService('dmwappushsvc')  # Delete dmwappushsvc
                print "dmwappushsvc successfully deleted."
            except pywintypes.error:
                print "dmwappushsvc unable to be deleted. Deleted already, or is the program not elevated?"

            try:
                win32serviceutil.RemoveService('Diagnostics Tracking Service')  # Delete the DiagnosticsTracking Service
                print "Diagnostics Tracking Service successfully deleted."
            except pywintypes.error:
                print "Diagnostics Tracking Service unable to be deleted. Deleted already, or is the program not elevated?"

        elif self.servicerad.Selection == 0 and self.servicebox.IsChecked():
            self.diagkeypath = r'SYSTEM\CurrentControlSet\Services\DiagTrack'
            self.dmwakeypath = r'SYSTEM\CurrentControlSet\Services\dmwappushsvc'

            try:
                self.diagkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.diagkeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.diagkey, "Start", 0, _winreg.REG_DWORD, 0x0000004)
                _winreg.CloseKey(self.diagkey)
            except WindowsError:
                print "Unable to modify DiagTrack key. Deleted, or is the program not elevated?"

            try:
                self.dmwakey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.dmwakeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.dmwakey, "Start", 0, _winreg.REG_DWORD, 0x0000004)
                _winreg.CloseKey(self.dmwakey)
                print "dmwappushsvc key successfully modified"
            except WindowsError:
                print "Unable to modify dmwappushsvc key. Deleted, or is the program not elevated?"

            try:
                win32serviceutil.StopService('Diagnostics Tracking Service')  # Disable Diagnostics Tracking Service
                print "Diagnostics Tracking Service successfully stopped"
            except pywintypes.error:
                print "Diagnostics Tracking Service unable to be stopped. Deleted, or is the program not elevated?"

            try:
                win32serviceutil.StopService('dmwappushsvc')  # Disable dmwappushsvc
                print "dmwappushsvc successfully stopped"
            except pywintypes.error:
                print "dmwappushsvc unable to be stopped. Deleted, or is the program not elevated?"

        print "Done. You can close this window after reading the log."


class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        self.out.WriteText(string)


if __name__ == '__main__':
    wxwindow = wx.App(False)
    WinFrame(None, title='Disable Windows 10 Tracking')  # Create Window
    wxwindow.MainLoop()
