import ctypes
import os
import subprocess
import sys
import _winreg

import win32serviceutil
import wx
import wx.lib.wordwrap
import pywintypes


class RedirectText(object):
    def __init__(self, console):
        self.out = console

    def write(self, string):
        self.out.WriteText(string)


class ConsoleFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title="Console Output", size=[500, 200],
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        panel = wx.Panel(self)  # Frame panel

        # Redirect console output to TextCtrl box
        self.consolebox = wx.TextCtrl(panel, wx.ID_ANY, size=(475, 125), style=wx.TE_MULTILINE | wx.TE_READONLY,
                                      pos=(10, 10))

        self.redirect = RedirectText(self.consolebox)
        sys.stdout = self.redirect

        # Final OK button
        self.okbutton = wx.Button(panel, wx.ID_ANY, "OK", pos=(398, 140))
        self.okbutton.Bind(wx.EVT_BUTTON, self.onok)

        self.Center()  # Center window

    def onok(self, event):
        self.consolebox.Clear()
        self.Hide()


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='Disable Windows 10 Tracking', size=[375, 190],
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        panel = wx.Panel(self)  # Frame panel

        # Test for elevation
        if ctypes.windll.shell32.IsUserAnAdmin() != 1:
            warn = wx.MessageDialog(parent=None,
                                    message="Program requires elevation, please run it as an administrator",
                                    caption="ERROR", style=wx.OK | wx.ICON_WARNING)
            warn.ShowModal()
            sys.exit()

        # Get icon
        shell32file = os.path.join(os.environ['SYSTEMROOT'], 'System32\\shell32.dll')
        self.SetIcon(wx.Icon(shell32file + ";315", wx.BITMAP_TYPE_ICO))

        # Info bar w/ about menu
        infomenu = wx.Menu()
        aboutitem = infomenu.Append(wx.ID_ABOUT, "About", "About the application")

        menubar = wx.MenuBar()
        menubar.Append(infomenu, "&Info")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.about, aboutitem)

        # Service checkbox
        self.servicebox = wx.CheckBox(panel, label="Services", pos=(10, 10))
        self.servicebox.SetToolTip(wx.ToolTip("Disables or Deletes tracking services. Choose option in Service Method"))
        self.Bind(wx.EVT_CHECKBOX, self.serviceradioboxcheck, self.servicebox)

        # DiagTrack checkbox
        self.diagtrackbox = wx.CheckBox(panel, label="Clear DiagTrack log", pos=(10, 25))
        self.diagtrackbox.SetToolTip(wx.ToolTip("Clears Diagnostic Tracking log and prevents modification to it. "
                                                "This cannot be undone without doing it manually."))

        # Telemetry checkbox
        self.telemetrybox = wx.CheckBox(panel, label="Telemetry", pos=(10, 40))
        self.telemetrybox.SetToolTip(
            wx.ToolTip("Sets \'AllowTelemetry\' to 0. On non-Enterprise OS editions, requires HOSTS file modification"))
        self.Bind(wx.EVT_CHECKBOX, self.telemetryhostcheck, self.telemetrybox)

        # HOSTS file checkbox
        self.hostbox = wx.CheckBox(panel, label="Block tracking domains", pos=(10, 55))
        self.hostbox.SetToolTip(wx.ToolTip("Add known tracking domains to HOSTS file. Required to disable Telemetry"))

        # Extra HOSTS checkbox
        self.extrahostbox = wx.CheckBox(panel, label="Block even more tracking domains", pos=(10, 70))
        self.extrahostbox.SetToolTip(wx.ToolTip("For the paranoid. Adds extra domains to the HOSTS file. WARNING: Some "
                                                "things like Dr. Watson and Error Reporting may be turned off by this"))

        # IP block checkbox
        self.ipbox = wx.CheckBox(panel, label="Block tracking IP addresses", pos=(10, 85))
        self.ipbox.SetToolTip(wx.ToolTip("Blocks known tracking IP addresses with Windows Firewall."))

        # OneDrive uninstall checkbox
        self.onedrivedbox = wx.CheckBox(panel, label="Uninstall OneDrive", pos=(10, 115))
        self.onedrivedbox.SetToolTip(wx.ToolTip("Uninstalls OneDrive from your computer and removes OneDrive from explorer."))

        # Service radio box
        self.serviceradbox = wx.RadioBox(panel, label="Service Method", pos=(135, 5), choices=["Disable", "Delete"])
        self.serviceradbox.Disable()

        # OK button
        self.okbutton = wx.Button(panel, wx.ID_OK, label="Get privacy!", pos=(275, 25))
        self.okbutton.SetToolTip(wx.ToolTip("Give me my privacy, damn it!"))
        self.Bind(wx.EVT_BUTTON, self.goprivate, self.okbutton)

        # Revert button
        self.revertbutton = wx.Button(panel, wx.ID_ANY, label="Revert", pos=(275, 50))
        self.revertbutton.SetToolTip(wx.ToolTip("I wanna go back! :("))
        self.Bind(wx.EVT_BUTTON, self.revert, self.revertbutton)

        self.fixbutton = wx.Button(panel, wx.ID_ANY, label="Fix Skype/Mail", pos=(266, 75))
        self.fixbutton.SetToolTip(wx.ToolTip("Press this if you're having issues with Skype or the Mail app"))
        self.Bind(wx.EVT_BUTTON, self.fix, self.fixbutton)

        self.console = ConsoleFrame()  # Call ConsoleFrame to start redirecting stdout to a TextCtrl

        # Center and show the window
        self.Centre()
        self.Show()

    def serviceradioboxcheck(self, event):
        self.serviceradbox.Enable(self.servicebox.IsChecked())

    def telemetryhostcheck(self, event):
        self.hostbox.SetValue(self.telemetrybox.IsChecked())

    def about(self, event):
        licensetext = "Copyright 2015 10se1ucgo\r\n\r\nLicensed under the Apache License, Version 2.0" \
                      " (the \"License\");\r\nyou may not use this file except in compliance with the License" \
                      ".\r\nYou may obtain a copy of the License at\r\n\r\n" \
                      "    http://www.apache.org/licenses/LICENSE-2.0\r\n\r\nUnless required by applicable law or" \
                      " agreed to in writing, software\r\ndistributed under the License is distributed on an" \
                      " \"AS IS\" BASIS,\r\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied." \
                      "\r\nSee the License for the specific language governing permissions and\r\nlimitations under" \
                      " the License."

        aboutpg = wx.AboutDialogInfo()
        aboutpg.Name = "Windows 10 Tracking Disable Tool"
        aboutpg.Version = "v2.3"
        aboutpg.Copyright = "(c) 2015 10se1ucgo"
        aboutpg.Description = "A tool to disable nasty tracking in Windows 10"
        aboutpg.WebSite = ("https://github.com/10se1ucgo/DisableWinTracking", "GitHub Project Page")
        aboutpg.License = wx.lib.wordwrap.wordwrap(licensetext, 500, wx.ClientDC(self))
        wx.AboutBox(aboutpg)

    def goprivate(self, event):
        # Disable buttons
        self.okbutton.Disable()
        self.revertbutton.Disable()
        self.fixbutton.Enable()
        self.cluttercontrol()  # If we don't do this, the hosts file and firewall will become a mess after some time.
        try:
            if self.servicebox.IsChecked():
                modifyserviceregs(0x0000004)
                if self.serviceradbox.Selection == 0:
                    disableservice('dmwappushsvc')
                    disableservice('Diagnostics Tracking Service')
                elif self.serviceradbox.Selection == 1:
                    deleteservice('dmwappushsvc')
                    deleteservice('Diagnostics Tracking Service')
            if self.diagtrackbox.IsChecked():
                cleardiagtracklog()
            if self.telemetrybox.IsChecked():
                modifytelemetryregs("0")
            if self.hostbox.IsChecked():
                modifyhosts(extra=False, undo=False)
            if self.extrahostbox.IsChecked():
                modifyhosts(extra=True, undo=False)
            if self.ipbox.IsChecked():
                blockips(undo=False)
            if self.onedrivedbox.IsChecked():
                modifyonedrive("uninstall")
        finally:
            # Re-enable buttons
            self.okbutton.Enable()
            self.revertbutton.Enable()
            self.fixbutton.Enable()
            self.console.Show()  # Show console output window after the code is run
            print "Done. It's recommended that you reboot as soon as possible for the full effect."

    def cluttercontrol(self):
        if self.hostbox.IsChecked():
            modifyhosts(extra=False, undo=True)
        if self.extrahostbox.IsChecked():
            modifyhosts(extra=True, undo=True)
        if self.ipbox.IsChecked():
            blockips(undo=True)
        self.console.consolebox.Clear()

    def revert(self, event):
        # Disable buttons
        self.okbutton.Disable()
        self.revertbutton.Disable()
        self.fixbutton.Disable()
        try:
            if self.servicebox.IsChecked():
                modifyserviceregs(0x0000003)
            if self.telemetrybox.IsChecked():
                modifytelemetryregs("1")
            if self.hostbox.IsChecked():
                modifyhosts(extra=False, undo=True)
            if self.extrahostbox.IsChecked():
                modifyhosts(extra=True, undo=True)
            if self.ipbox.IsChecked():
                blockips(undo=True)
            if self.onedrivedbox.IsChecked():
                modifyonedrive("install")
        finally:
            self.okbutton.Enable()
            self.revertbutton.Enable()
            self.fixbutton.Enable()
            self.console.Show()
            print "Done. It's recommended that you reboot as soon as possible for the full effect."

    def fix(self, event):
        self.okbutton.Disable()
        self.revertbutton.Disable()
        self.fixbutton.Disable()
        try:
            skypemailfix()
        finally:
            self.okbutton.Enable()
            self.revertbutton.Enable()
            self.fixbutton.Enable()
            self.console.Show()
            print "Done. It's recommended that you reboot as soon as possible for the fix to work."

def modifyhosts(extra, undo):
    nullip = "0.0.0.0 "  # IP to route domains to

    # List of tracking domains.
    normallist = ['a-0001.a-msedge.net', 'a-0002.a-msedge.net', 'a-0003.a-msedge.net',
                  'a-0004.a-msedge.net', 'a-0005.a-msedge.net', 'a-0006.a-msedge.net', 'a-0007.a-msedge.net',
                  'a-0008.a-msedge.net', 'a-0009.a-msedge.net', 'a-msedge.net', 'a.ads1.msn.com', 'a.ads2.msads.net',
                  'a.ads2.msn.com', 'a.rad.msn.com', 'ac3.msn.com', 'ad.doubleclick.net', 'adnexus.net', 'adnxs.com',
                  'ads.msn.com', 'ads1.msads.net', 'ads1.msn.com', 'aidps.atdmt.com', 'aka-cdn-ns.adtech.de',
                  'az361816.vo.msecnd.net', 'az512334.vo.msecnd.net', 'b.ads1.msn.com',
                  'b.ads2.msads.net', 'b.rad.msn.com', 'bs.serving-sys.com', 'c.atdmt.com', 'c.msn.com',
                  'cdn.atdmt.com', 'cds26.ams9.msecn.net', 'choice.microsoft.com', 'choice.microsoft.com.nsatc.net',
                  'compatexchange.cloudapp.net', 'corp.sts.microsoft.com', 'corpext.msitadfs.glbdns2.microsoft.com',
                  'cs1.wpc.v0cdn.net', 'db3aqu.atdmt.com', 'df.telemetry.microsoft.com',
                  'diagnostics.support.microsoft.com', 'ec.atdmt.com', 'feedback.microsoft-hohm.com',
                  'feedback.search.microsoft.com', 'feedback.windows.com', 'flex.msn.com', 'g.msn.com', 'h1.msn.com',
                  'i1.services.social.microsoft.com', 'i1.services.social.microsoft.com.nsatc.net',
                  'lb1.www.ms.akadns.net', 'live.rads.msn.com', 'm.adnxs.com', 'msedge.net',
                  'msftncsi.com', 'msnbot-65-55-108-23.search.msn.com', 'msntest.serving-sys.com',
                  'oca.telemetry.microsoft.com', 'oca.telemetry.microsoft.com.nsatc.net', 'pre.footprintpredict.com',
                  'preview.msn.com', 'rad.live.com', 'rad.msn.com', 'redir.metaservices.microsoft.com',
                  'schemas.microsoft.akadns.net ', 'secure.adnxs.com', 'secure.flashtalking.com',
                  'settings-sandbox.data.microsoft.com', 'settings-win.data.microsoft.com',
                  'sls.update.microsoft.com.akadns.net', 'sqm.df.telemetry.microsoft.com',
                  'sqm.telemetry.microsoft.com', 'sqm.telemetry.microsoft.com.nsatc.net', 'static.2mdn.net',
                  'statsfe1.ws.microsoft.com', 'statsfe2.ws.microsoft.com', 'telecommand.telemetry.microsoft.com',
                  'telecommand.telemetry.microsoft.com.nsatc.net', 'telemetry.appex.bing.net',
                  'telemetry.microsoft.com', 'telemetry.urs.microsoft.com',
                  'vortex-bn2.metron.live.com.nsatc.net', 'vortex-cy2.metron.live.com.nsatc.net',
                  'vortex-sandbox.data.microsoft.com', 'vortex-win.data.microsoft.com', 'vortex.data.microsoft.com',
                  'watson.live.com', 'www.msftncsi.com', 'ssw.live.com']

    extralist = ['fe2.update.microsoft.com.akadns.net', 'reports.wes.df.telemetry.microsoft.com', 's0.2mdn.net',
                 'services.wes.df.telemetry.microsoft.com', 'statsfe2.update.microsoft.com.akadns.net',
                 'survey.watson.microsoft.com', 'view.atdmt.com', 'watson.microsoft.com',
                 'watson.ppe.telemetry.microsoft.com', 'watson.telemetry.microsoft.com',
                 'watson.telemetry.microsoft.com.nsatc.net', 'wes.df.telemetry.microsoft.com', 'ui.skype.com',
                 'pricelist.skype.com', 'apps.skype.com', 'm.hotmail.com', 's.gateway.messenger.live.com']

    # Domains with 0.0.0.0 added to the beginning of each.
    normallistip = [nullip + x for x in normallist]
    extralistip = [nullip + x for x in extralist]

    hostspath = os.path.join(os.environ['SYSTEMROOT'], 'System32\\drivers\\etc\\hosts')

    if not undo:
        if not extra:
            try:
                with open(hostspath, 'ab') as f:
                    f.write('\r\n' + '\r\n'.join(normallistip))
                print "Domains successfully appended to HOSTS file."
            except (WindowsError, IOError):
                print "Could not access HOSTS file. Is the program not elevated?"

        elif extra:
            try:
                with open(hostspath, 'ab') as f:
                    f.write('\r\n' + '\r\n'.join(extralistip))
                print "Extra domains successfully appended to HOSTS file."
            except (WindowsError, IOError):
                print "Could not access HOSTS file. Is the program not elevated?"

    elif undo:
        if not extra:
            try:
                with open(hostspath, 'r') as hostfile, open(hostspath + "temp", 'w') as tempfile:
                    for line in hostfile:
                        if not any(domain in line for domain in normallist):
                            tempfile.write(line)

                os.remove(hostspath)
                os.rename(hostspath + "temp", hostspath)
                print "Domains successfully removed from HOSTS file."
            except (WindowsError, IOError):
                print "Could not access HOSTS file. Is the program not elevated?"

        elif extra:
            try:
                with open(hostspath, 'r') as hostfile, open(hostspath + "temp", 'w') as tempfile:
                    for line in hostfile:
                        if not any(domain in line for domain in extralist):
                            tempfile.write(line)

                os.remove(hostspath)
                os.rename(hostspath + "temp", hostspath)
                print "Extra domains successfully removed from HOSTS file."
            except (WindowsError, IOError):
                print "Could not access HOSTS file. Is the program not elevated?"


def blockips(undo):
    iplist = ['2.22.61.43', '2.22.61.66', '65.39.117.230', '65.55.108.23', '23.218.212.69',
              '134.170.30.202', '137.116.81.24', '157.56.106.189', '204.79.197.200']

    if not undo:
        try:
            for ip in iplist:
                subprocess.call("netsh advfirewall firewall add rule name=""TrackingIP{0}"" dir=out"
                                " protocol=any remoteip=""{0}"" profile=any action=block".format(ip), shell=True)
            print "IPs succesfully blocked."
        except (WindowsError, IOError):
            print "One or more IPs were unable to be blocked."

    elif undo:
        try:
            for ip in iplist:
                subprocess.call("netsh advfirewall firewall delete rule name=""TrackingIP{0}""".format(ip), shell=True)
            print "IPs succesfully removed."
        except (WindowsError, IOError):
            print "One or more IPs were unable to be removed."


def cleardiagtracklog():
    logfile = os.path.join(os.environ['SYSTEMDRIVE'], '\\ProgramData\\Microsoft\\Diagnosis\\ETLLogs\\AutoLogger\\'
                                                      'AutoLogger-Diagtrack-Listener.etl')

    disableservice('Diagnostics Tracking Service')

    try:
        open(logfile, 'w').close()  # Clear the AutoLogger file
        subprocess.call("echo y|cacls {0} /d SYSTEM".format(logfile), shell=True)  # Prevent modification to file
        print "DiagTrack log succesfully cleared and locked."
    except (WindowsError, IOError):
        print "Unable to clear DiagTrack log. Deleted, or is the program not elevated?"


def deleteservice(service):
    try:
        win32serviceutil.RemoveService(service)  # Delete service
        print "%s successfully deleted." % service
    except pywintypes.error:
        print "%s unable to be deleted. Deleted already, or is the program not elevated?" % service


def disableservice(service):
    try:
        win32serviceutil.StopService(service)  # Delete service
        print "%s successfully stopped." % service
    except pywintypes.error:
        print "%s unable to be stopped. Deleted, or is the program not elevated?" % service


def modifytelemetryregs(value):
    telemetrypath = r'SOFTWARE\Policies\Microsoft\Windows\DataCollection'  # Path to Telemetry key
    telemetrypath2 = r'SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\DataCollection'  # 2nd path

    try:
        telemetrykey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, telemetrypath, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(telemetrykey, "AllowTelemetry", 0, _winreg.REG_SZ, value)  # Disable Telemetry
        _winreg.CloseKey(telemetrykey)
        print "Telemetry key succesfully modified."
    except (WindowsError, IOError):
        print "Unable to modify Telemetry key. Deleted, or is the program not elevated? Trying another method"

    try:
        telemetrykey2 = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, telemetrypath2, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(telemetrykey2, "AllowTelemetry", 0, _winreg.REG_SZ, value)  # Disable Telemetry
        _winreg.CloseKey(telemetrykey2)
        print "2nd Telemetry key succesfully modified."
    except (WindowsError, IOError):
        print "Unable to modify 2nd Telemetry key. Deleted, or is the program not elevated?"


def modifyserviceregs(dwordval):
    diagtrackpath = r'SYSTEM\CurrentControlSet\Services\DiagTrack'
    dmwapushhpath = r'SYSTEM\CurrentControlSet\Services\dmwappushsvc'

    try:
        diagtrackkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, diagtrackpath, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(diagtrackkey, "Start", 0, _winreg.REG_DWORD, dwordval)
        _winreg.CloseKey(diagtrackkey)
        print "DiagTrack key successfully modified"
    except (WindowsError, IOError):
        print "Unable to modify DiagTrack key. Deleted, or is the program not elevated?"

    try:
        dmwapushkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dmwapushhpath, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(dmwapushkey, "Start", 0, _winreg.REG_DWORD, dwordval)
        _winreg.CloseKey(dmwapushkey)
        print "dmwappushsvc key successfully modified"
    except (WindowsError, IOError):
        print "Unable to modify dmwappushsvc key. Deleted, or is the program not elevated?"


def modifyonedrive(type):
    onedrivepath = r'SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\OneDrive'  # Path to OneDrive key
    odxpath32 = r'HKEY_CLASSES_ROOT\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}' # Path to 32-bit Key
    odxpath64 = r'HKEY_CLASSES_ROOT\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}' # Path to 64-bit Key

    try:
        onedrivekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, onedrivepath, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(onedrivekey, "DisableFileSyncNGSC", 0, _winreg.REG_DWORD, 1)  # Disable Telemetry
        _winreg.CloseKey(onedrivekey)
        print "OneDrive key succesfully modified."
    except (WindowsError, IOError):
        print "Unable to modify OneDrive FileSync key. Deleted, or is the program not elevated?"
        
    try:
        odxkey32 = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, odxkey32, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(odxkey32, "System.IsPinnedToNameSpaceTree", 0, _winreg.REG_DWORD, 0)  # Disable Explorer List-Pin
        _winreg.CloseKey(odxkey32)
        print "OneDrive 32-bit Windows Explorer pin successfully removed."
    except (WindowsError, IOError):
        print "Unable to modify OneDrive 32-bit Windows Explorer pin key. Deleted, or is the program not elevated?"
        
    try:
        odxkey64 = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, odxkey64, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(odxkey64, "System.IsPinnedToNameSpaceTree", 0, _winreg.REG_DWORD, 0)  # Disable Explorer List-Pin
        _winreg.CloseKey(odxkey64)
        print "OneDrive 64-bit Windows Explorer pin successfully removed."
    except (WindowsError, IOError):
        print "Unable to modify OneDrive 64-bit Windows Explorer pin key. If your system is 32-bit, ignore this message. Deleted, or is the program not elevated?"

    onedrivesetup = os.path.join(os.environ['SYSTEMROOT'], "SysWOW64/OneDriveSetup.exe")
    if os.path.isfile(onedrivesetup):
        subprocess.call("{0} /{1}".format(onedrivesetup, type), shell=True)
    else:
        onedrivesetup = os.path.join(os.environ['SYSTEMROOT'], "System32/OneDriveSetup.exe")
        subprocess.call("{0} /{1}".format(onedrivesetup, type), shell=True)


def skypemailfix():
    fixlist = ['ui.skype.com', 'pricelist.skype.com', 'apps.skype.com',
               's.gateway.messenger.live.com', 'm.hotmail.com']

    hostspath = os.path.join(os.environ['SYSTEMROOT'], 'System32\\drivers\\etc\\hosts')

    try:
        with open(hostspath, 'r') as hostfile, open(hostspath + "temp", 'w') as tempfile:
            for line in hostfile:
                if not any(domain in line for domain in fixlist):
                    tempfile.write(line)

        os.remove(hostspath)
        os.rename(hostspath + "temp", hostspath)
        print "Skype and Mail domains successfully removed from HOSTS file."
    except (WindowsError, IOError):
        print "Could not access HOSTS file. Is the program not elevated?"

if __name__ == '__main__':
    wxwindow = wx.App(False)
    frame = MainFrame()  # Create Window
    wxwindow.MainLoop()
