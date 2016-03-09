Currently being re-written, [see issue #153](https://github.com/10se1ucgo/DisableWinTracking/issues/153)

~~No longer being developed, [see issue #147](https://github.com/10se1ucgo/DisableWinTracking/issues/147).~~

~~This may no longer thoroughly disable all tracking, as some services have been added or have had their names changed. [See Issue #124.](https://github.com/10se1ucgo/DisableWinTracking/issues/124)~~

# DisableWinTracking

![Main frame image](http://i.imgur.com/4iDf3Gb.png)

A tool that I created to use some of the known methods of disabling tracking in Windows 10.

## DOWNLOAD!!

[DOWNLOAD EXE HERE!!](https://github.com/10se1ucgo/DisableWinTracking/releases/)

## How to Use

You can either:

A. [Run the binary uploaded to the Release tab as an Administrator and select which options you'd like](https://github.com/10se1ucgo/DisableWinTracking/releases/)

B. Install Python and the dependencies listed below and run the script from an elevated (`admin`) command prompt and select which options you'd like  

## Dependencies
This is only to run the script from source, [download the exe here](https://github.com/10se1ucgo/DisableWinTracking/releases/)
* [Python 2.7](https://www.python.org/download/releases/2.7/) (or 3 with 2to3.py or something)
* [wxPython](http://wxpython.org/download.php)
* [PyWin32](http://sourceforge.net/projects/pywin32/files/pywin32/)
* Windows 10 (Duh)

## Methods Used

#### Telemetry

Set the `AllowTelemetry` string in `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection` to `0`

#### DiagTrack Log

Clears and disables writing to the log located in `C:\ProgramData\Microsoft\Diagnosis\ETLLogs\AutoLogger`

#### Services

You can delete or disable the 2 services below:
* `DiagTrack` Diagnostics Tracking Service
* `dmwappushsvc` WAP Push Message Routing Service

Action:
* Delete: Remove both services
* Disable: Set the `Start` registry key for both services to `4` (Disabled) Located at `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\`

#### HOSTS

Append known tracking domains to the `HOSTS` file located in `C:\Windows\System32\drivers\etc`  
To add these domains to the `HOSTS` file using another tool, it is available in raw form at https://gist.github.com/10se1ucgo/fcb774d781a66ea9d31f

#### IP Blocking

Blocks known tracking IPs with the Windows Firewall. The rules are named TrackingIPX, replacing X with the IP numbers.

#### Windows Defender / WifiSense

Set disabled value to keys in registry for things such as:
- Windows Defender
    - Automatic Sample Submission
    - Delivery Optimization Download Mode
- WifiSense
    - Credential Share
    - Open-ness

#### OneDrive

Runs `C:\Windows\SysWOW64\OneDriveSetup.exe /uninstall` (64 bit) or  
`C:\Windows\System32\OneDriveSetup.exe /uninstall` (32 bit)

Also disables registry entries that keep the OneDrive Icon pinned to your Windows Explorer list:
![OneDrive Example Image](http://i.imgur.com/26yfnGD.png)

## Delete Services vs Disable Services?

Selecting "Disable" will simply stop the services from being able to run.
Selecting the "Delete" choice will completely delete the tracking services.

## License

Copyright 2015 10se1ucgo

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
