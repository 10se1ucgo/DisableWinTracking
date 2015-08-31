import ctypes
import logging
import os
import subprocess
import sys
import _winreg

import win32serviceutil
import wx
import wx.lib.wordwrap
import pywintypes



# Configure the Logging module
logging.basicConfig(filename='DisableWinTracking.log', level=logging.DEBUG,
                    format='\n%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')


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

        # Windows Defender/Wifisense
        self.defendwifibox = wx.CheckBox(panel, label="Stop Defender/Wifisense Data Collection", pos=(10, 100))
        self.defendwifibox.SetToolTip(wx.ToolTip("Modifies registry to stop Windows Defender and WifiSense from "
                                                 "Data Collecting."))

        # OneDrive uninstall checkbox
        self.onedrivedbox = wx.CheckBox(panel, label="Uninstall OneDrive", pos=(10, 115))
        self.onedrivedbox.SetToolTip(wx.ToolTip("Uninstalls OneDrive from your computer and removes it from Explorer."))

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
                modifyserviceregs(dwordval=0x0000004)
                if self.serviceradbox.Selection == 0:
                    disableservice(service='dmwappushsvc')
                    disableservice(service='Diagnostics Tracking Service')
                elif self.serviceradbox.Selection == 1:
                    deleteservice(service='dmwappushsvc')
                    deleteservice(service='Diagnostics Tracking Service')
            if self.diagtrackbox.IsChecked():
                cleardiagtracklog()
            if self.telemetrybox.IsChecked():
                modifytelemetryregs(telemetryval="0")
            if self.hostbox.IsChecked():
                modifyhosts(extra=False, undo=False)
            if self.extrahostbox.IsChecked():
                modifyhosts(extra=True, undo=False)
            if self.ipbox.IsChecked():
                blockips(undo=False)
            if self.defendwifibox.IsChecked():
                stopdefendwifi(regdwordval=0)
            if self.onedrivedbox.IsChecked():
                modifyonedrive(function="uninstall", filesyncval=1)
        finally:
            # Re-enable buttons
            self.okbutton.Enable()
            self.revertbutton.Enable()
            self.fixbutton.Enable()
            self.console.Show()  # Show console output window after the code is run
            print "Done. It's recommended that you reboot as soon as possible for the full effect."
            print "If any errors were found, please make a GitHub ticket with the contents of DisableWinTracking.log"

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
                modifyserviceregs(dwordval=0x0000003)
            if self.telemetrybox.IsChecked():
                modifytelemetryregs(telemetryval="1")
            if self.hostbox.IsChecked():
                modifyhosts(extra=False, undo=True)
            if self.extrahostbox.IsChecked():
                modifyhosts(extra=True, undo=True)
            if self.ipbox.IsChecked():
                blockips(undo=True)
            if self.defendwifibox.IsChecked():
                stopdefendwifi(regdwordval=1)
            if self.onedrivedbox.IsChecked():
                modifyonedrive(function="install", filesyncval=0)
        finally:
            self.okbutton.Enable()
            self.revertbutton.Enable()
            self.fixbutton.Enable()
            self.console.Show()
            print "Done. It's recommended that you reboot as soon as possible for the full effect."
            print "If any errors were found, please make a GitHub ticket with the contents of DisableWinTracking.log"

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
            print "If any errors were found, please make a GitHub ticket with the contents of DisableWinTracking.log"


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
                print "Hosts mod: Domains succesfully appended."
            except (WindowsError, IOError):
                logging.exception("Hosts mod: Could not append domains")
                print "Hosts mod: Could not append domains"

        elif extra:
            try:
                with open(hostspath, 'ab') as f:
                    f.write('\r\n' + '\r\n'.join(extralistip))
                print "Extra hosts mod: Domains succesfully appended."
            except (WindowsError, IOError):
                logging.exception("Extra hosts mod: Could not append domains.")
                print "Extra hosts mod: Could not append domains."

    elif undo:
        if not extra:
            try:
                with open(hostspath, 'r') as hostfile, open(hostspath + "temp", 'w') as tempfile:
                    for line in hostfile:
                        if not any(domain in line for domain in normallist):
                            tempfile.write(line)

                os.remove(hostspath)
                os.rename(hostspath + "temp", hostspath)
                print "Hosts mod: Domains successfully removed."
            except (WindowsError, IOError):
                logging.exception("Hosts mod: Could not remove domains.")
                print "Hosts mod: Could not remove domains."

        elif extra:
            try:
                with open(hostspath, 'r') as hostfile, open(hostspath + "temp", 'w') as tempfile:
                    for line in hostfile:
                        if not any(domain in line for domain in extralist):
                            tempfile.write(line)

                os.remove(hostspath)
                os.rename(hostspath + "temp", hostspath)
                print "Extra hosts mod: Domains successfully removed."
            except (WindowsError, IOError):
                logging.exception("Extra hosts mod: Could not remove domains.")
                print "Extra hosts mod: Could not remove domains."


def blockips(undo):
    iplist = ['2.22.61.43', '2.22.61.66', '65.39.117.230', '65.55.108.23', '23.218.212.69',
              '134.170.30.202', '137.116.81.24', '157.56.106.189', '204.79.197.200']

    if not undo:
        try:
            for ip in iplist:
                subprocess.call("netsh advfirewall firewall add rule name=""TrackingIP{0}"" dir=out"
                                " protocol=any remoteip=""{0}"" profile=any action=block".format(ip), shell=True)
            print "IP Blocking: Succesfully blocked."
        except (WindowsError, IOError):
            logging.exception("IP Blocking: One or more were unable to be blocked.")
            print "IP Blocking: One or more were unable to be blocked."

    elif undo:
        try:
            for ip in iplist:
                subprocess.call("netsh advfirewall firewall delete rule name=""TrackingIP{0}""".format(ip), shell=True)
            print "IP Blocking: Succesfully unblocked."
        except (WindowsError, IOError):
            logging.exception("IP Blocking: One or more were unable to be unblocked.")
            print "IP Blocking: One or more were unable to be unblocked."


def cleardiagtracklog():
    logfile = os.path.join(os.environ['SYSTEMDRIVE'], '\\ProgramData\\Microsoft\\Diagnosis\\ETLLogs\\AutoLogger\\'
                                                      'AutoLogger-Diagtrack-Listener.etl')

    disableservice('Diagnostics Tracking Service')

    try:
        open(logfile, 'w').close()  # Clear the AutoLogger file
        subprocess.call("echo y|cacls {0} /d SYSTEM".format(logfile), shell=True)  # Prevent modification to file
        print "DiagTrack Log: Succesfully cleared and locked."
    except (WindowsError, IOError):
        logging.exception("DiagTrack Log: Unable to clear/lock")
        print "DiagTrack Log: Unable to clear/lock"


def deleteservice(service):
    try:
        win32serviceutil.RemoveService(service)  # Delete service
        print "Services: {0} successfully deleted.".format(service)
    except pywintypes.error:
        logging.exception("Services: {0} unable to be deleted.".format(service))
        print "Services: {0} unable to be deleted.".format(service)


def disableservice(service):
    try:
        win32serviceutil.StopService(service)  # Delete service
        print "Services: {0} successfully stopped.".format(service)
    except pywintypes.error:
        logging.exception("Services: {0} unable to be stopped.".format(service))
        print "Services: {0} unable to be stopped.".format(service)


def modifytelemetryregs(telemetryval):
    # Telemetry regkey paths
    telemetrypathsdict = {'32bit': r'SOFTWARE\Policies\Microsoft\Windows\DataCollection',
                          '64bit': r'SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\DataCollection'}

    for bit, telemetrypath in telemetrypathsdict.viewitems():
        try:
            telemetrykey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, telemetrypath, 0, _winreg.KEY_ALL_ACCESS)
            _winreg.SetValueEx(telemetrykey, "AllowTelemetry", 0, _winreg.REG_SZ, telemetryval)  # Disable Telemetry
            _winreg.CloseKey(telemetrykey)
            print "Telemetry: {0} key succesfully modified.".format(bit)
        except (WindowsError, IOError):
            logging.exception("Telemetry: Unable to modify {0} key.".format(bit))
            print "Telemetry: Unable to modify {0} key.".format(bit)


def modifyserviceregs(dwordval):
    # Service regkey paths
    servicepathsdict = {'dmwappushsvc': 'SYSTEM\\CurrentControlSet\\Services\\dmwappushsvc',
                        'DiagTrack': 'SYSTEM\\CurrentControlSet\\Services\\DiagTrack'}

    for servicename, servicepath in servicepathsdict.viewitems():
        try:
            servicekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, servicepath, 0, _winreg.KEY_ALL_ACCESS)
            _winreg.SetValueEx(servicepath, "Start", 0, _winreg.REG_DWORD, dwordval)
            _winreg.CloseKey(servicekey)
            print "Services: {0} key successfully modified".format(servicename)
        except (WindowsError, IOError):
            logging.exception("Services: Unable to modify {0} key.".format(servicename))
            print "Services: Unable to modify {0} key.".format(servicename)


def stopdefendwifi(regdwordval):
  
    # Windows Defender and WifiSense keys
    stopdefendwifidict = {'Delivery Optimization Download': [r'SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config', 'DODownloadMode'],
                        'WifiSense Credential Share': [r'SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\features', 'WiFiSenseCredShared'],
                        'WifiSense Open-ness': [r'SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\features', 'WiFiSenseOpen'],
                        'Windows Defender Spynet': [r'SOFTWARE\Microsoft\Windows Defender\Spynet', 'SpyNetReporting'],
                        'Windows Defender Sample Submission': [r'SOFTWARE\Microsoft\Windows Defender\Spynet', 'SubmitSamplesConsent']}

    for title, registry in stopdefendwifidict.viewitems():
      # Disable Windows Defender and WifiSense Privacy-Destroying Datamining attempts
      try:
          wdwfsregkey = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, registry[0], 0, _winreg.KEY_ALL_ACCESS)
          _winreg.SetValueEx(wdwfsregkey, registry[1], 0, _winreg.REG_DWORD, regdwordval)
          _winreg.CloseKey(wdwfsregkey)
          if regval == 0:
            print "Defender/WifiSense: {0} key successfully disabled.".format(title)
          else:
            print "Defender/WifiSense: {0} key successfully enabled.".format(title)
      except (WindowsError, IOError):
          logging.exception("Unable to modify {0} key.".format(title))
          print "Unable to modify {0} key.".format(title)

def modifyonedrive(function, filesyncval):
    filesyncpath = r'SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\OneDrive'  # OneDrive regkey path
    # OneDrive shellext regkey paths
    listpinpathsdict = {'32bit': r'CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}',
                        '64bit': r'Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}'}

    try:
        # Disable FileSync
        filesynckey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, filesyncpath, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(filesynckey, "DisableFileSyncNGSC", 0, _winreg.REG_DWORD, filesyncval)
        _winreg.CloseKey(filesynckey)
        print "OneDrive: FileSync key succesfully modified.".format(filesyncpath)
    except (WindowsError, IOError):
        logging.exception("OneDrive: Unable to modify FileSync key.")
        print "OneDrive: Unable to modify FileSync key."

    for bit, listpinpath in listpinpathsdict.viewitems():
        # Disable Explorer List-Pin
        try:
            listpinregkey = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, listpinpath, 0, _winreg.KEY_ALL_ACCESS)
            _winreg.SetValueEx(listpinregkey, "System.IsPinnedToNameSpaceTree", 0, _winreg.REG_DWORD, filesyncval)
            _winreg.CloseKey(listpinregkey)
            print "OneDrive: {0} Windows Explorer pin successfully removed.".format(bit)
        except (WindowsError, IOError):
            logging.exception("OneDrive: Unable to modify {0} Windows Explorer pin key.".format(bit))
            print "OneDrive: Unable to modify {0} Windows Explorer pin key.".format(bit)

    onedrivesetup = os.path.join(os.environ['SYSTEMROOT'], "SysWOW64/OneDriveSetup.exe")
    if os.path.isfile(onedrivesetup):
        try:
            subprocess.call("{0} /{1}".format(onedrivesetup, function), shell=True)
            print "OneDrive: Succesfully {0}ed.".format(function)
        except (WindowsError, IOError):
            logging.exception("OneDrive: Unable to {0}.".format(function))
            print "OneDrive: Unable to {0}.".format(function)
    else:
        onedrivesetup = os.path.join(os.environ['SYSTEMROOT'], "System32/OneDriveSetup.exe")
        try:
            subprocess.call("{0} /{1}".format(onedrivesetup, function), shell=True)
            print "OneDrive: Succesfully {0}ed.".format(function)
        except (WindowsError, IOError):
            logging.exception("OneDrive: Unable to {0}.".format(function))
            print "OneDrive: Unable to {0}.".format(function)


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
        print "Skype/Mail Fix: Domains successfully removed from HOSTS file."
    except (WindowsError, IOError):
        logging.exception("Skype/Mail Fix: Could not remove domains from HOSTS file.")
        print "Skype/Mail Fix: Could not remove domains from HOSTS file."

if __name__ == '__main__':
    wxwindow = wx.App(False)
    frame = MainFrame()  # Create Window
    wxwindow.MainLoop()
