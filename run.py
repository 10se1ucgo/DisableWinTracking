import ctypes
import logging
import os
import subprocess
import sys
import _winreg
import platform
import win32serviceutil
import wx
import wx.lib.wordwrap
import pywintypes
from wx.lib.itemspicker import ItemsPicker, IP_SORT_CHOICES, IP_SORT_SELECTED, IP_REMOVE_FROM_CHOICES

vernumber = "v2.5.3"  # Version number

# Configure the Logging module
logging.basicConfig(filename='DisableWinTracking.log', level=logging.DEBUG,
                    format='\n%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S', filemode='w')


class RedirectText(object):
    def __init__(self, console):
        self.out = console

    def write(self, string):
        self.out.WriteText(string)


class ConsoleFrame(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, parent=wx.GetApp().TopWindow, title="Console Output", size=[500, 200],
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        panel = wx.Panel(self)  # Frame panel

        # Redirect console output to TextCtrl box
        self.consolebox = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.redirect = RedirectText(self.consolebox)
        sys.stdout = self.redirect

        self.issuebutton = wx.Button(panel, wx.ID_ANY, label="Report an issue", pos=(9, 140))
        self.issuebutton.Bind(wx.EVT_BUTTON, self.submitissue)

        # Final OK button
        self.okbutton = wx.Button(panel, wx.ID_OK, label="OK", pos=(398, 140))
        self.okbutton.Bind(wx.EVT_BUTTON, self.onok)

        consolesizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

        consolesizer.Add(buttonsizer)
        consolesizer.Add(self.consolebox, 1, wx.ALL | wx.EXPAND, 1)

        buttonsizer.Add(self.okbutton)
        buttonsizer.Add(self.issuebutton)

        panel.SetSizerAndFit(consolesizer)

    def onok(self, event):
        sys.exit()

    def submitissue(self, event):
        os.startfile("http://bit.ly/DWTIssue")


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='Disable Windows 10 Tracking', size=[375, 345],
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
        menu = wx.Menu()
        aboutitem = menu.Append(wx.ID_ABOUT, "About", "About the application")
        optionsitem = menu.Append(wx.ID_ANY, "Options", "Settings for the application")

        menubar = wx.MenuBar()
        menubar.Append(menu, "&Menu")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.aboutbox, aboutitem)
        self.Bind(wx.EVT_MENU, self.settingsbox, optionsitem)

        # Service checkbox
        self.servicebox = wx.CheckBox(panel, label="&Services", pos=(10, 10))
        self.servicebox.SetToolTip(wx.ToolTip("Disables or Deletes tracking services. Choose option in Service Method"))
        self.Bind(wx.EVT_CHECKBOX, self.serviceradioboxcheck, self.servicebox)

        # DiagTrack checkbox
        self.diagtrackbox = wx.CheckBox(panel, label="Clear &DiagTrack log", pos=(10, 25))
        self.diagtrackbox.SetToolTip(wx.ToolTip("Clears Diagnostic Tracking log and prevents modification to it. "
                                                "This cannot be undone without doing it manually."))

        # Telemetry checkbox
        self.telemetrybox = wx.CheckBox(panel, label="&Telemetry", pos=(10, 40))
        self.telemetrybox.SetToolTip(
            wx.ToolTip("Sets \'AllowTelemetry\' to 0. On non-Enterprise OS editions, requires HOSTS file modification"))
        self.Bind(wx.EVT_CHECKBOX, self.telemetryhostcheck, self.telemetrybox)

        # HOSTS file checkbox
        self.hostbox = wx.CheckBox(panel, label="&Block tracking domains", pos=(10, 55))
        self.hostbox.SetToolTip(wx.ToolTip("Add known tracking domains to HOSTS file. Required to disable Telemetry"))

        # Extra HOSTS checkbox
        self.extrahostbox = wx.CheckBox(panel, label="Block &even more tracking domains", pos=(10, 70))
        self.extrahostbox.SetToolTip(wx.ToolTip("For the paranoid. Adds extra domains to the HOSTS file. WARNING: Some "
                                                "things like Dr. Watson and Error Reporting may be turned off by this"))

        # IP block checkbox
        self.ipbox = wx.CheckBox(panel, label="Block tracking &IP addresses", pos=(10, 85))
        self.ipbox.SetToolTip(wx.ToolTip("Blocks known tracking IP addresses with Windows Firewall."))

        # Windows Defender/Wifisense
        self.defendwifibox = wx.CheckBox(panel, label="Stop Defender&/Wifisense Data Collection", pos=(10, 100))
        self.defendwifibox.SetToolTip(wx.ToolTip("Modifies registry to stop Windows Defender and WifiSense from "
                                                 "Data Collecting."))

        # OneDrive uninstall checkbox
        self.onedrivedbox = wx.CheckBox(panel, label="Uninstall &OneDrive", pos=(10, 115))
        self.onedrivedbox.SetToolTip(wx.ToolTip("Uninstalls OneDrive from your computer and removes it from Explorer."))

        # App static box
        self.appbox = wx.StaticBox(panel, label="Built-in Apps", pos=(10, 130), size=(351, 160))

        self.builderbox = wx.CheckBox(self.appbox, label="&3D Builder", pos=(10, 15))
        self.calmailbox = wx.CheckBox(self.appbox, label="C&alender && Mail", pos=(10, 30))
        self.camerabox = wx.CheckBox(self.appbox, label="&Camera", pos=(10, 45))
        self.officebox = wx.CheckBox(self.appbox, label="Get &Office App", pos=(10, 60))
        self.skypebox = wx.CheckBox(self.appbox, label="Get S&kype App", pos=(10, 75))
        self.startbox = wx.CheckBox(self.appbox, label="Get S&tarted App", pos=(10, 90))
        self.groovebox = wx.CheckBox(self.appbox, label="&Groove Music", pos=(10, 105))
        self.mapbox = wx.CheckBox(self.appbox, label="&Maps", pos=(120, 15))
        self.mscbox = wx.CheckBox(self.appbox, label="Microso&ft Solitaire Collection", pos=(120, 105))
        self.moneybox = wx.CheckBox(self.appbox, label="Mone&y", pos=(120, 30))
        self.movietvbox = wx.CheckBox(self.appbox, label="Movies && T&V", pos=(120, 45))
        self.newsbox = wx.CheckBox(self.appbox, label="&News", pos=(120, 60))
        self.onenotebox = wx.CheckBox(self.appbox, label="OneNote Ap&p", pos=(120, 75))
        self.peoplebox = wx.CheckBox(self.appbox, label="P&eople", pos=(120, 90))
        self.phonebox = wx.CheckBox(self.appbox, label="Phone Compan&ion", pos=(225, 15))
        self.photosbox = wx.CheckBox(self.appbox, label="P&hotos", pos=(225, 30))
        self.sportsbox = wx.CheckBox(self.appbox, label="&Sports", pos=(225, 45))
        self.voicebox = wx.CheckBox(self.appbox, label="Voice &Recorder", pos=(225, 60))
        self.weatherbox = wx.CheckBox(self.appbox, label="&Weather", pos=(225, 75))
        self.xbonebox = wx.CheckBox(self.appbox, label="&Xbox", pos=(225, 90))

        self.selectapps = wx.CheckBox(self.appbox, label="Select all apps", pos=(246, 0), style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.selectallapps, self.selectapps)

        self.removeappbut = wx.Button(self.appbox, wx.ID_ANY, label="Uninstall selected apps", pos=(10, 125))
        self.removeappbut.SetToolTip(wx.ToolTip("Uninstalls all of the selected apps. Can take a lot of time."))
        self.Bind(wx.EVT_BUTTON, self.uninstapps, self.removeappbut)

        self.reinstappbut = wx.Button(self.appbox, wx.ID_ANY, label="Reinstall original apps", pos=(205, 125))
        self.reinstappbut.SetToolTip(wx.ToolTip("Reinstalls ALL of the default apps. Takes a lot of time."))
        self.Bind(wx.EVT_BUTTON, self.reinstapps, self.reinstappbut)

        # Service radio box
        self.serviceradbox = wx.RadioBox(panel, label="Service Method", pos=(135, 5), choices=("Disable", "Delete"))
        self.serviceradbox.Disable()
        self.serviceradbox.SetItemToolTip(0, "Simply disables the services. This can be undone.")
        self.serviceradbox.SetItemToolTip(1, "Deletes the services completely. This can't be undone.")

        # Go button
        self.gobutton = wx.Button(panel, wx.ID_ANY, label="Go!", pos=(275, 25))
        self.Bind(wx.EVT_BUTTON, self.go, self.gobutton)

        self.goradbox = wx.RadioBox(panel, label="Mode", pos=(284, 50),
                                    choices=("Privacy", "Revert"), style=wx.RA_SPECIFY_ROWS)

        self.goradbox.SetItemToolTip(0, "Using the selected settings, applies privacy.")
        self.goradbox.SetItemToolTip(1, "Reverts everything selected to it's original form (Except the DiagTrack Log "
                                        "and services if you chose the 'Delete' option)")

        self.console = ConsoleFrame()  # Call ConsoleFrame to start redirecting stdout to a TextCtrl

        # Center and show the window
        self.Centre()
        self.Show()

    def serviceradioboxcheck(self, event):
        # Enables serviceradbox if the service box is ticked
        self.serviceradbox.Enable(self.servicebox.IsChecked())

    def telemetryhostcheck(self, event):
        # Automatically checks the domain block when the telemetry box is checked.
        self.hostbox.SetValue(self.telemetrybox.IsChecked())

    def selectallapps(self, event):
        # Iters through all children of the app static box and checks them except for the last 3.
        # (buttons and the select all checkbox)
        for checkbox in list(self.appbox.GetChildren())[:-3]:
            checkbox.SetValue(self.selectapps.IsChecked())

    def aboutbox(self, event):
        # About dialog
        licensetext = "Copyright 2015 10se1ucgo\r\n\r\nLicensed under the Apache License, Version 2.0" \
                      " (the \"License\");\r\nyou may not use this file except in compliance with the License" \
                      ".\r\nYou may obtain a copy of the License at\r\n\r\n" \
                      "    http://www.apache.org/licenses/LICENSE-2.0\r\n\r\nUnless required by applicable law or" \
                      " agreed to in writing, software\r\ndistributed under the License is distributed on an" \
                      " \"AS IS\" BASIS,\r\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied." \
                      "\r\nSee the License for the specific language governing permissions and\r\nlimitations under" \
                      " the License."

        aboutpg = wx.AboutDialogInfo()
        aboutpg.Name = "Disable Windows 10 Tracking"
        aboutpg.Version = vernumber
        aboutpg.Copyright = "(c) 2015 10se1ucgo"
        aboutpg.Description = "A tool to disable nasty tracking in Windows 10"
        aboutpg.WebSite = ("https://github.com/10se1ucgo/DisableWinTracking", "GitHub Project Page")
        aboutpg.License = wx.lib.wordwrap.wordwrap(licensetext, 500, wx.ClientDC(self))
        aboutpg.Developers = ["10se1ucgo and Ruined1 on GitHub"]
        wx.AboutBox(aboutpg)

    def settingsbox(self, event):
        # Settings dialog
        settingsdialog = wx.Dialog(wx.GetApp().TopWindow, wx.ID_ANY, "Settings")

        boxsizer = wx.BoxSizer(wx.VERTICAL)

        normallist = ('a-0001.a-msedge.net', 'a-0002.a-msedge.net', 'a-0003.a-msedge.net', 'a-0004.a-msedge.net',
                      'a-0005.a-msedge.net', 'a-0006.a-msedge.net', 'a-0007.a-msedge.net', 'a-0008.a-msedge.net',
                      'a-0009.a-msedge.net', 'a-msedge.net', 'a.ads1.msn.com', 'a.ads2.msads.net',
                      'a.ads2.msn.com', 'a.rad.msn.com', 'ac3.msn.com', 'ad.doubleclick.net', 'adnexus.net',
                      'adnxs.com', 'ads.msn.com', 'ads1.msads.net', 'ads1.msn.com', 'aidps.atdmt.com',
                      'aka-cdn-ns.adtech.de', 'az361816.vo.msecnd.net', 'az512334.vo.msecnd.net', 'b.ads1.msn.com',
                      'b.ads2.msads.net', 'b.rad.msn.com', 'bs.serving-sys.com', 'c.atdmt.com', 'c.msn.com',
                      'cdn.atdmt.com', 'cds26.ams9.msecn.net', 'choice.microsoft.com',
                      'choice.microsoft.com.nsatc.net', 'compatexchange.cloudapp.net', 'corp.sts.microsoft.com',
                      'corpext.msitadfs.glbdns2.microsoft.com', 'cs1.wpc.v0cdn.net', 'db3aqu.atdmt.com',
                      'df.telemetry.microsoft.com', 'diagnostics.support.microsoft.com', 'ec.atdmt.com',
                      'feedback.microsoft-hohm.com', 'feedback.search.microsoft.com', 'feedback.windows.com',
                      'flex.msn.com', 'g.msn.com', 'h1.msn.com', 'i1.services.social.microsoft.com',
                      'i1.services.social.microsoft.com.nsatc.net', 'lb1.www.ms.akadns.net', 'live.rads.msn.com',
                      'm.adnxs.com', 'msedge.net', 'msftncsi.com', 'msnbot-65-55-108-23.search.msn.com',
                      'msntest.serving-sys.com', 'oca.telemetry.microsoft.com',
                      'oca.telemetry.microsoft.com.nsatc.net', 'pre.footprintpredict.com', 'preview.msn.com',
                      'rad.live.com', 'rad.msn.com', 'redir.metaservices.microsoft.com',
                      'schemas.microsoft.akadns.net ', 'secure.adnxs.com', 'secure.flashtalking.com',
                      'settings-sandbox.data.microsoft.com', 'settings-win.data.microsoft.com',
                      'sls.update.microsoft.com.akadns.net', 'sqm.df.telemetry.microsoft.com',
                      'sqm.telemetry.microsoft.com', 'sqm.telemetry.microsoft.com.nsatc.net', 'static.2mdn.net',
                      'statsfe1.ws.microsoft.com', 'statsfe2.ws.microsoft.com',
                      'telecommand.telemetry.microsoft.com', 'telecommand.telemetry.microsoft.com.nsatc.net',
                      'telemetry.appex.bing.net', 'telemetry.microsoft.com', 'telemetry.urs.microsoft.com',
                      'vortex-bn2.metron.live.com.nsatc.net', 'vortex-cy2.metron.live.com.nsatc.net',
                      'vortex-sandbox.data.microsoft.com', 'vortex-win.data.microsoft.com',
                      'vortex.data.microsoft.com', 'watson.live.com', 'www.msftncsi.com', 'ssw.live.com')

        extralist = ('fe2.update.microsoft.com.akadns.net', 'reports.wes.df.telemetry.microsoft.com',
                     's0.2mdn.net', 'services.wes.df.telemetry.microsoft.com',
                     'statsfe2.update.microsoft.com.akadns.net', 'survey.watson.microsoft.com', 'view.atdmt.com',
                     'watson.microsoft.com', 'watson.ppe.telemetry.microsoft.com',
                     'watson.telemetry.microsoft.com', 'watson.telemetry.microsoft.com.nsatc.net',
                     'wes.df.telemetry.microsoft.com', 'ui.skype.com', 'pricelist.skype.com', 'apps.skype.com',
                     'm.hotmail.com', 's.gateway.messenger.live.com')

        self.normalpicker = ItemsPicker(settingsdialog, id=wx.ID_ANY, choices=[], selectedLabel="Domains to be blocked",
                                        ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES)
        self.normalpicker.SetSelections(normallist)

        self.extrapicker = ItemsPicker(settingsdialog, id=wx.ID_ANY, choices=[],
                                       selectedLabel="Extra domains to be blocked",
                                       ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES)
        self.extrapicker.SetSelections(extralist)

        iplist = ('2.22.61.43', '2.22.61.66', '65.39.117.230', '65.55.108.23', '23.218.212.69',
                  '134.170.30.202', '137.116.81.24', '157.56.106.189', '204.79.197.200', '65.52.108.33')

        self.ippicker = ItemsPicker(settingsdialog, id=wx.ID_ANY, choices=[],
                                    selectedLabel="IP addresses to be blocked",
                                    ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES)

        self.ippicker.SetToolTip(wx.ToolTip("Hello"))

        self.ippicker.SetSelections(iplist)

        boxsizer.Add(self.normalpicker, 0, wx.ALL | wx.TOP, 10)
        boxsizer.Add(self.extrapicker, 0, wx.ALL | wx.CENTER | wx.EXPAND, 10)
        boxsizer.Add(self.ippicker, 0, wx.ALL | wx.BOTTOM | wx.EXPAND, 10)

        settingsdialog.SetSizerAndFit(boxsizer)

        if event is not None:
            settingsdialog.Center()
            settingsdialog.ShowModal()

    def go(self, event):
        self.settingsbox(None)  # Call the settings box to get the settings values
        if self.goradbox.GetSelection() == 1:  # if mode is revert
            mode = "Revert"
            startval = 3
            telemetryval = 1
            undo = True
            defendersenseval = 1
            filesyncval = 0
            installerfunc = "install"
        else:
            mode = "Privacy"
            startval = 4
            telemetryval = 0
            undo = False
            defendersenseval = 0
            filesyncval = 1
            installerfunc = "uninstall"
            self.cluttercontrol()
            if self.diagtrackbox.IsChecked():
                logging.info("DiagTrack box ticked")
                cleardiagtracklog()
            if self.servicebox.IsChecked():
                if self.serviceradbox.Selection == 0:
                    logging.info("Service disable option ticked")
                    disableservice(service='dmwappushsvc')
                    disableservice(service='Diagnostics Tracking Service')
                elif self.serviceradbox.Selection == 1:
                    logging.info("Service delete option ticked")
                    deleteservice(service='dmwappushsvc')
                    deleteservice(service='Diagnostics Tracking Service')

        logging.info("DisableWinTracking Version: {0}".format(vernumber))
        logging.info("Mode: {0}".format(mode))
        if self.servicebox.IsChecked():
            modifyserviceregs(startval=startval)
        if self.telemetrybox.IsChecked():
            logging.info("Telemetry box ticked")
            modifytelemetryregs(telemetryval=telemetryval)
        if self.hostbox.IsChecked():
            self.settingsbox(None)
            logging.info("Host box ticked")
            modifyhostfile(undo=undo, domainlist=self.normalpicker.GetSelections(), name="Domain block")
        if self.extrahostbox.IsChecked():
            logging.info("Extra host box ticked")
            modifyhostfile(undo=undo, domainlist=self.extrapicker.GetSelections(), name="Extra domain block")
        if self.ipbox.IsChecked():
            logging.info("IP block box ticked")
            blockips(iplist=self.ippicker.GetSelections(), undo=undo)
        if self.defendwifibox.IsChecked():
            logging.info("Defender/Wifisense box ticked")
            stopdefendwifi(defendersenseval=defendersenseval)
        if self.onedrivedbox.IsChecked():
            logging.info("OneDrive box ticked")
            modifyonedrive(installerfunc=installerfunc, filesyncval=filesyncval)
        self.console.Show()  # Show console output window after the code is run
        self.console.Center()  # Center console window
        print "Done. It's recommended that you reboot as soon as possible for the full effect."
        print "If you feel something didn't work properly, please press the 'Report an issue' " \
              "button and follow the directions"

    def uninstapps(self, event):
        uninstalllist = []
        logging.info("DisableWinTracking Version: {0}".format(vernumber))

        if self.builderbox.IsChecked():
            uninstalllist.append('3dbuilder')
        if self.calmailbox.IsChecked():
            uninstalllist.append('windowscommunicationsapps')
        if self.camerabox.IsChecked():
            uninstalllist.append('windowscamera')
        if self.officebox.IsChecked():
            uninstalllist.append('officehub')
        if self.skypebox.IsChecked():
            uninstalllist.append('skypeapp')
        if self.startbox.IsChecked():
            uninstalllist.append('getstarted')
        if self.groovebox.IsChecked():
            uninstalllist.append('zunemusic')
        if self.mapbox.IsChecked():
            uninstalllist.append('windowsmaps')
        if self.mscbox.IsChecked():
            uninstalllist.append('solitairecollection')
        if self.moneybox.IsChecked():
            uninstalllist.append('bingfinance')
        if self.movietvbox.IsChecked():
            uninstalllist.append('zunevideo')
        if self.newsbox.IsChecked():
            uninstalllist.append('bingnews')
        if self.onenotebox.IsChecked():
            uninstalllist.append('onenote')
        if self.peoplebox.IsChecked():
            uninstalllist.append('people')
        if self.phonebox.IsChecked():
            uninstalllist.append('windowsphone')
        if self.photosbox.IsChecked():
            uninstalllist.append('photos')
        if self.sportsbox.IsChecked():
            uninstalllist.append('bingsports')
        if self.voicebox.IsChecked():
            uninstalllist.append('soundrecorder')
        if self.weatherbox.IsChecked():
            uninstalllist.append('bingweather')
        if self.xbonebox.IsChecked():
            uninstalllist.append('xboxapp')

        if uninstalllist:  # Check  if at least one app is selected
            apppackage(reinstall=False, applist=uninstalllist)
            self.console.Show()  # Show console output window after the code is run
            self.console.Center()  # Center console window

    def reinstapps(self, event):
        apppackage(reinstall=True, applist=['thisshouldntevenbepassed'])

    def cluttercontrol(self):
        logging.info("Performing clutter control")
        if self.hostbox.IsChecked():
            modifyhostfile(undo=True, domainlist=self.normalpicker.GetSelections(), name="Clutter control")
        if self.extrahostbox.IsChecked():
            modifyhostfile(undo=True, domainlist=self.extrapicker.GetSelections(), name="Extra domain clutter control")
        if self.ipbox.IsChecked():
            blockips(undo=True)
        self.console.consolebox.Clear()


def osis64bit():
    # Detect if OS is 64bit
    if platform.machine().endswith('64'):
        return True
    else:
        return False


def blockips(iplist, undo):
    if not undo:
        try:
            for ip in iplist:
                subprocess.call("netsh advfirewall firewall add rule name=""TrackingIP{0}"" dir=out"
                                " protocol=any remoteip=""{0}"" profile=any action=block".format(ip), shell=True)
                print "IP Blocking: {0} successfully blocked.".format(ip)
        except (WindowsError, IOError):
            logging.exception("IP Blocking: One or more were unable to be blocked.")
            print "IP Blocking: One or more were unable to be blocked."

    elif undo:
        try:
            for ip in iplist:
                subprocess.call("netsh advfirewall firewall delete rule name=""TrackingIP{0}""".format(ip), shell=True)
                print "IP Blocking: {0} successfully unblocked.".format(ip)
        except (WindowsError, IOError):
            logging.exception("IP Blocking: One or more were unable to be unblocked.")
            print "IP Blocking: One or more were unable to be unblocked."


def cleardiagtracklog():
    logfile = os.path.join(os.environ['SYSTEMDRIVE'], '\\ProgramData\\Microsoft\\Diagnosis\\ETLLogs\\AutoLogger\\'
                                                      'AutoLogger-Diagtrack-Listener.etl')

    disableservice('Diagnostics Tracking Service')

    try:
        subprocess.call("takeown /f {0} && icacls {0} /grant administrators:F".format(logfile), shell=True)
        open(logfile, 'w').close()  # Clear the AutoLogger file
        subprocess.call("echo y|cacls {0} /d SYSTEM".format(logfile), shell=True)  # Prevent modification to file
        print "DiagTrack Log: successfully cleared and locked."
    except (WindowsError, IOError):
        logging.exception("DiagTrack Log: Unable to clear/lock.")
        print "DiagTrack Log: Unable to clear/lock"


def deleteservice(service):
    try:
        win32serviceutil.RemoveService(service)  # Delete service
        print "Services: {0} successfully deleted.".format(service)
    except pywintypes.error as e:
        errors = (1060, 1062)
        if not any(error == e[0] for error in errors):
            logging.exception("Services: {0} unable to be deleted.".format(service))
            print "Services: {0} unable to be deleted.".format(service)


def disableservice(service):
    try:
        win32serviceutil.StopService(service)  # Disable service
        print "Services: {0} successfully stopped.".format(service)
    except pywintypes.error as e:
        errors = (1060, 1062)  # 1060: Does not exist. 1062: Not started.
        if not any(error == e[0] for error in errors):
            logging.exception("Services: {0} unable to be stopped.".format(service))
            print "Services: {0} unable to be stopped.".format(service)


def modifytelemetryregs(telemetryval):
    # Telemetry regkey paths
    telemetrydict = {'AllowTelemetry': [_winreg.HKEY_LOCAL_MACHINE,
                                        r'SOFTWARE\Policies\Microsoft\Windows\DataCollection',
                                        "AllowTelemetry", _winreg.REG_DWORD, telemetryval]}

    modifyregistry(regdict=telemetrydict, name="Telemetry")


def modifyserviceregs(startval):
    # Service regkey paths
    servicesdict = {'dmwappushsvc': [_winreg.HKEY_LOCAL_MACHINE,
                                     r'SYSTEM\\CurrentControlSet\\Services\\dmwappushsvc',
                                     'Start', _winreg.REG_DWORD, startval],

                    'DiagTrack': [_winreg.HKEY_LOCAL_MACHINE,
                                  r'SYSTEM\\CurrentControlSet\\Services\\DiagTrack',
                                  'Start', _winreg.REG_DWORD, startval]}

    modifyregistry(regdict=servicesdict, name="Services")


def stopdefendwifi(defendersenseval):
    # Windows Defender and WifiSense keys
    wdwfsdict = {'Windows Defender Delivery Optimization Download':
                 [_winreg.HKEY_LOCAL_MACHINE,
                  r'SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config',
                  'DODownloadMode', _winreg.REG_DWORD, defendersenseval],

                 'WifiSense Credential Share': [_winreg.HKEY_LOCAL_MACHINE,
                                                r'SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\features',
                                                'WiFiSenseCredShared', _winreg.REG_DWORD, defendersenseval],

                 'WifiSense Open-ness': [_winreg.HKEY_LOCAL_MACHINE,
                                         r'SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\features',
                                         'WiFiSenseOpen', _winreg.REG_DWORD, defendersenseval],

                 'Windows Defender Spynet': [_winreg.HKEY_LOCAL_MACHINE,
                                             r'SOFTWARE\Microsoft\Windows Defender\Spynet',
                                             'SpyNetReporting', _winreg.REG_DWORD, defendersenseval],

                 'Windows Defender Sample Submission': [_winreg.HKEY_LOCAL_MACHINE,
                                                        r'SOFTWARE\Microsoft\Windows Defender\Spynet',
                                                        'SubmitSamplesConsent', _winreg.REG_DWORD, defendersenseval]}

    modifyregistry(wdwfsdict, name="WifiSense/Defender")


def modifyonedrive(installerfunc, filesyncval):
    # The two key values are opposites, so we have to flip them.
    if filesyncval == 0:
        pinval = 1
    else:
        pinval = 0

    # OneDrive shellext regkey paths
    ngscdict = {'FileSync': [_winreg.HKEY_LOCAL_MACHINE,
                             r'SOFTWARE\Policies\Microsoft\Windows\OneDrive',
                             'DisableFileSyncNGSC', _winreg.REG_DWORD, filesyncval],

                'ListPin': [_winreg.HKEY_CLASSES_ROOT,
                            r'CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}',
                            'System.IsPinnedToNameSpaceTree', _winreg.REG_DWORD, pinval]}

    modifyregistry(regdict=ngscdict, name="OneDrive")

    if osis64bit():
        onedrivesetup = os.path.join(os.environ['SYSTEMROOT'], "SysWOW64/OneDriveSetup.exe")
    else:
        onedrivesetup = os.path.join(os.environ['SYSTEMROOT'], "System32/OneDriveSetup.exe")

    try:
        subprocess.call("{0} /{1}".format(onedrivesetup, installerfunc), shell=True)
        print "OneDrive: successfully {0}ed.".format(installerfunc)
    except (WindowsError, IOError):
        logging.exception("OneDrive: Unable to {0}.".format(installerfunc))
        print "OneDrive: Unable to {0}.".format(installerfunc)


def modifyregistry(regdict, name):
    # Modifies registry keys from a dictionary
    # FORMAT: regdict = {"Title": [_winreg.HKEY, r'regkeypath', 'regkey', _winreg.REG_[DWORD/SZ/etc.], keyvalue
    # keyvalue = String, only if REG_SZ.

    if osis64bit():
        accessmask = _winreg.KEY_WOW64_64KEY + _winreg.KEY_ALL_ACCESS
    else:
        accessmask = _winreg.KEY_ALL_ACCESS

    for title, registry in regdict.viewitems():
        try:
            # Using CreateKeyEx, which will open or create a key as necessary
            modreg = _winreg.CreateKeyEx(registry[0], registry[1], 0, accessmask)
            _winreg.SetValueEx(modreg, registry[2], 0, registry[3], registry[4])
            _winreg.CloseKey(modreg)
            print "{1}: {0} key successfully modified.".format(title, name)
        except (WindowsError, IOError):
            logging.exception("Registry: Unable to modify {0} key.".format(title, name))
            print "{1}: Unable to modify {0} key.".format(title, name)


def modifyhostfile(undo, domainlist, name):
    # Modifies the hosts file with a list
    # FORMAT: domainlist = ['www.example.com', 'www.etc.com']
    # undo: Specifies whether or not to remove the lines from the host file or append them
    # name: Name displayed in error/completion message.

    nullip = "0.0.0.0 "  # IP to route domains to

    # Domains with 0.0.0.0 added to the beginning of each.
    nulledlist = [nullip + x for x in domainlist]

    hostspath = os.path.join(os.environ['SYSTEMROOT'], 'System32\\drivers\\etc\\hosts')

    if not undo:
        try:
            with open(hostspath, 'ab') as f:
                f.write('\r\n' + '\r\n'.join(nulledlist))
            print "{0}: Domains successfully appended.".format(name)
        except (WindowsError, IOError):
            logging.exception("{0}: Could not append domains".format(name))
            print "{0}: Could not append domains".format(name)

    elif undo:
        try:
            with open(hostspath, 'r') as hostfile, open(hostspath + "temp", 'w') as tempfile:
                for line in hostfile:
                    if not any(domain in line for domain in domainlist):
                        tempfile.write(line)

            os.remove(hostspath)
            os.rename(hostspath + "temp", hostspath)
            print "{0}: Domains successfully removed.".format(name)
        except (WindowsError, IOError):
            logging.exception("{0}: Could not remove domains.".format(name))
            print "{0}: Could not remove domains.".format(name)


def apppackage(reinstall, applist):
    if not reinstall:
        for app in applist:
            try:
                p = subprocess.Popen("powershell \"Get-AppxPackage *{0}*|Remove-AppxPackage\"".format(app), shell=True)
                print "App management: Handled {0} successfully"
            except (WindowsError, IOError):
                print "App management: Could not uninstall {0}".format(app)

        p.communicate()  # Workaround for console window opening prematurely

    if reinstall:
        # We encode in Base64 because the command is complex and I'm too lazy to escape everything.
        # It's uncoded format command: "Get-AppxPackage -AllUsers| Foreach {Add-AppxPackage -DisableDevelopmentMode
        # -Register "$($_.InstallLocation)\AppXManifest.xml"}"
        encodedcommand = "RwBlAHQALQBBAHAAcAB4AFAAYQBjAGsAYQBnAGUAIAAtAEEAbABsAFUAcwBlAHIAcwB8ACAARgBvAHIAZQBhAGMA" \
                         "aAAgAHsAQQBkAGQALQBBAHAAcAB4AFAAYQBjAGsAYQBnAGUAIAAtAEQAaQBzAGEAYgBsAGUARABlAHYAZQBsAG8AcA" \
                         "BtAGUAbgB0AE0AbwBkAGUAIAAtAFIAZQBnAGkAcwB0AGUAcgAgACIAJAAoACQAXwAuAEkAbgBzAHQAYQBsAGwATABvA" \
                         "GMAYQB0AGkAbwBuACkAXABBAHAAcABYAE0AYQBuAGkAZgBlAHMAdAAuAHgAbQBsACIAfQA="
        try:
            subprocess.call("powershell -EncodedCommand {0}".format(encodedcommand), shell=True)
        except (WindowsError, IOError):
            print "App management: Could not re-install all apps"


if __name__ == '__main__':
    wxwindow = wx.App(False)
    frame = MainFrame()  # Create Window
    wxwindow.MainLoop()
