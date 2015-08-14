# Sorry if it looks messy

import sys
import subprocess
import _winreg
import ctypes
import os

import wx
from wx.lib.wordwrap import wordwrap
import win32serviceutil
import pywintypes


class WinFrame(wx.Frame):
    def __init__(self, parent, title):
        super(WinFrame, self).__init__(parent, title=title, size=[375, 250],
                                       style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        wxpanel = wx.Panel(self)

        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        aboutMenuItem = fileMenu.Append(wx.NewId(), "About",
                                        "About the application")
        menuBar.Append(fileMenu, "&Info")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.about, aboutMenuItem)

        self.debug = wx.TextCtrl(wxpanel, wx.ID_ANY, size=(349, 92),
                                 style=wx.TE_MULTILINE | wx.TE_READONLY, pos=(10, 99))

        self.redir = RedirectText(self.debug)
        sys.stdout = self.redir

        if ctypes.windll.shell32.IsUserAnAdmin() != 1:
            self.warn = wx.MessageDialog(parent=wxpanel,
                                         message="Program requires elevation, please run it as an administrator",
                                         caption="ERROR", style=wx.OK | wx.ICON_WARNING)
            self.warn.ShowModal()
            self.warn.Destroy()
            sys.exit()

        self.shell32file = os.path.join(os.environ['SYSTEMROOT'], 'System32\\shell32.dll')
        self.icon = wx.Icon(self.shell32file + ";315", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        self.telebox = wx.CheckBox(wxpanel, label="Telemetry", pos=(10, 15))
        self.telebox.Bind(wx.EVT_CHECKBOX, self.hostcheck)
        self.telebox.SetToolTip(
            wx.ToolTip("Set \'AllowTelemetry\' to 0. On non-Enterprise OS versions, requires HOSTS file modification."))
        self.telebox.Set3StateValue(0)

        self.servicebox = wx.CheckBox(wxpanel, label="Services", pos=(10, 30))
        self.servicebox.SetToolTip(wx.ToolTip("Enable \'Service Method\' box, select an option"))
        self.servicebox.Set3StateValue(0)
        self.servicebox.Bind(wx.EVT_CHECKBOX, self.serviceradcheck)

        self.diagbox = wx.CheckBox(wxpanel, label="Clear DiagTrack log", pos=(10, 45))
        self.diagbox.SetToolTip(wx.ToolTip("Clear DiagTrack log and prevents modification to it."))
        self.diagbox.Set3StateValue(0)

        self.hostbox = wx.CheckBox(wxpanel, label="Block tracking servers with HOSTS file",
                                   pos=(10, 60))
        self.hostbox.SetToolTip(wx.ToolTip("Add known tracking domains to HOSTS file. Required for Telemetry"))
        self.hostbox.Set3StateValue(0)

        self.onedrivebox = wx.CheckBox(wxpanel, label="Remove OneDrive", pos=(10, 75))
        self.onedrivebox.Set3StateValue(0)

        self.servicerad = wx.RadioBox(wxpanel, label="Service Method", pos=(135, 10), choices=["Disable", "Delete"])
        self.servicerad.Disable()

        self.okbutton = wx.Button(wxpanel, -1, "Go Private!", (275, 25))
        self.Bind(wx.EVT_BUTTON, self.onok, self.okbutton)
        self.Centre()
        self.Show()

    def serviceradcheck(self, event):
        self.servicerad.Enable(self.servicebox.IsChecked())  # If Service box is ticked enable Service radio box

    def hostcheck(self, event):
        self.hostbox.Set3StateValue(self.telebox.IsChecked())

    def about(self, event):
        licensetext = "Copyright 2015 10se1ucgo\r\n\r\nLicensed under the Apache License, Version 2.0" \
                      " (the \"License\");\r\nyou may not use this file except in compliance with the License" \
                      ".\r\nYou may obtain a copy of the License at\r\n\r\n" \
                      "    http://www.apache.org/licenses/LICENSE-2.0\r\n\r\nUnless required by applicable law or" \
                      " agreed to in writing, software\r\ndistributed under the License is distributed on an" \
                      " \"AS IS\" BASIS,\r\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied." \
                      "\r\nSee the License for the specific language governing permissions and\r\nlimitations under the License."

        aboutpg = wx.AboutDialogInfo()
        aboutpg.Name = "Windows 10 Tracking Disable Tool"
        aboutpg.Version = "v1.5"
        aboutpg.Copyright = "(c) 2015 10se1ucgo"
        aboutpg.Description = "A tool to disable nasty tracking in Windows 10"
        aboutpg.WebSite = ("https://github.com/10se1ucgo/DisableWinTracking", "GitHub Project Page")
        aboutpg.License = wordwrap(licensetext, 500, wx.ClientDC(self))
        wx.AboutBox(aboutpg)

    def onok(self, event):
        if self.telebox.IsChecked():
            self.telekeypath = r'SOFTWARE\Policies\Microsoft\Windows\DataCollection'  # Path to Telemetry key
            self.telekey2path = r'SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\DataCollection'  # 2nd path

            try:
                self.telekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.telekeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.telekey, "AllowTelemetry", 0, _winreg.REG_SZ, "0")  # Disable Telemetry
                _winreg.CloseKey(self.telekey)
                print "Telemetry key succesfully modified."
            except WindowsError:
                print "Unable to modify Telemetry key. Deleted, or is the program not elevated? Trying another method"

            try:
                self.telekey2 = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.telekey2path, 0,
                                                _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.telekey2, "AllowTelemetry", 0, _winreg.REG_SZ, "0")  # Disable Telemetry
                _winreg.CloseKey(self.telekey2)
                print "2nd Telemetry key succesfully modified."
            except WindowsError:
                print "Unable to modify 2nd Telemetry key. Deleted, or is the program not elevated?"

        if self.diagbox.IsChecked():
            self.logfile = os.path.join(os.environ['SYSTEMDRIVE'],
                                        '\\ProgramData\\Microsoft\\Diagnosis\\ETLLogs\\AutoLogger\\AutoLogger-Diagtrack-Listener.etl')

            try:
                win32serviceutil.StopService('Diagnostics Tracking Service')  # Stop Diagnostics Tracking Service
                print "Stopping DiagTrack service."
            except pywintypes.error:
                print "Couldn't stop DiagTrack service. Deleted, or is the program not elevated?"

            try:
                open(self.logfile).close()  # Clear the AutoLogger file
                subprocess.Popen(
                    ["echo", "y|cacls", self.logfile, "/d", "SYSTEM"],
                    shell=True)  # Prevent modification to file
                print "DiagTrack log succesfully cleared and locked."
            except IOError:
                print "Unable to clear DiagTrack log. Deleted, or is the program not elevated?"

        if self.hostbox.IsChecked():
            self.MSHosts = ['adnxs.com', 'c.msn.com', 'g.msn.com', 'h1.msn.com', 'msedge.net',
                            'ads.msn.com', 'adnexus.net', 'ac3.msn.com', 'c.atdmt.com', 'm.adnxs.com', 'rad.msn.com',
                            'sO.2mdn.net', 'ads1.msn.com', 'ec.atdmt.com', 'flex.msn.com', 'rad.live.com',
                            'ui.skype.com', 'msftncsi.com', 'a-msedge.net', 'a.rad.msn.com', 'b.rad.msn.com',
                            'cdn.atdmt.com', 'm.hotmail.com', 'ads1.msads.net', 'a.ads1.msn.com', 'a.ads2.msn.com',
                            'apps.skype.com', 'b.ads1.msn.com', 'view.atdmt.com', 'watson.live.com',
                            'aidps.atdmt.com', 'preview.msn.com', 'static.2mdn.net', 'a.ads2.msads.net',
                            'b.ads2.msads.net', 'db3aqu.atdmt.com', 'secure.adnxs.com', 'www.msftncsi.com',
                            'cs1.wpc.v0cdn.net', 'live.rads.msn.com', 'ad.doubleclick.net', 'bs.serving-sys.com',
                            'a-0001.a-msedge.net', 'pricelist.skype.com', 'a-0001.a-msedge.net', 'a-0002.a-msedge.net',
                            'a-0003.a-msedge.net', 'a-0004.a-msedge.net', 'a-0005.a-msedge.net', 'a-0006.a-msedge.net',
                            'a-0007.a-msedge.net', 'a-0008.a-msedge.net', 'a-0009.a-msedge.net', 'choice.microsoft.com',
                            'watson.microsoft.com', 'feedback.windows.com', 'aka-cdn-ns.adtech.de',
                            'cds26.ams9.msecn.net', 'lb1.www.ms.akadns.net', 'corp.sts.microsoft.com',
                            'az361816.vo.msecnd.net', 'az512334.vo.msecnd.net', 'telemetry.microsoft.com',
                            'msntest.serving-sys.com', 'secure.flashtalking.com', 'telemetry.appex.bing.net',
                            'pre.footprintpredict.com', 'vortex.data.microsoft.com',
                            'statsfe2.ws.microsoft.com', 'statsfe1.ws.microsoft.com', 'df.telemetry.microsoft.com',
                            'oca.telemetry.microsoft.com', 'sqm.telemetry.microsoft.com', 'telemetry.urs.microsoft.com',
                            'survey.watson.microsoft.com', 'compatexchange.cloudapp.net', 'feedback.microsoft-hohm.com',
                            's.gateway.messenger.live.com', 'vortex-win.data.microsoft.com',
                            'feedback.search.microsoft.com', 'schemas.microsoft.akadns.net ',
                            'watson.telemetry.microsoft.com', 'choice.microsoft.com.nsatc.net',
                            'wes.df.telemetry.microsoft.com', 'sqm.df.telemetry.microsoft.com',
                            'settings-win.data.microsoft.com', 'redir.metaservices.microsoft.com',
                            'i1.services.social.microsoft.com', 'vortex-sandbox.data.microsoft.com',
                            'diagnostics.support.microsoft.com', 'watson.ppe.telemetry.microsoft.com',
                            'msnbot-65-55-108-23.search.msn.com', 'telecommand.telemetry.microsoft.com',
                            'settings-sandbox.data.microsoft.com', 'sls.update.microsoft.com.akadns.net',
                            'fe2.update.microsoft.com.akadns.net', 'vortex-bn2.metron.live.com.nsatc.net',
                            'vortex-cy2.metron.live.com.nsatc.net', 'oca.telemetry.microsoft.com.nsatc.net',
                            'sqm.telemetry.microsoft.com.nsatc.net', 'reports.wes.df.telemetry.microsoft.com',
                            'corpext.msitadfs.glbdns2.microsoft.com', 'services.wes.df.telemetry.microsoft.com',
                            'watson.telemetry.microsoft.com.nsatc.net', 'statsfe2.update.microsoft.com.akadns.net',
                            'i1.services.social.microsoft.com.nsatc.net',
                            'telecommand.telemetry.microsoft.com.nsatc.net']
            self.IP = '0.0.0.0 '
            self.MSHosts2 = [self.IP + x for x in self.MSHosts]
            self.hostslocation = os.path.join(os.environ['SYSTEMROOT'], 'System32\\drivers\\etc\\hosts')

            try:
                with open(self.hostslocation, 'ab') as f:
                    f.write('\n' + '\n'.join(self.MSHosts2))
                print "Domains successfully appended to HOSTS file."
            except WindowsError:
                print "Could not access HOSTS file. Is the program not elevated?"

        if self.onedrivebox.IsChecked():
            self.onedkeypath = r'SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\OneDrive'  # Path to OneDrive key

            try:
                self.onedkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.onedkeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.onedkey, "DisableFileSyncNGSC", 0, _winreg.REG_DWORD, 1)  # Disable Telemetry
                _winreg.CloseKey(self.onedkey)
                print "OneDrive key succesfully modified."
            except WindowsError:
                print "Unable to modify OneDrive key. Deleted, or is the program not elevated?"

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
