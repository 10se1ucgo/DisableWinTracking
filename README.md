# DisableWinTracking

A tool that I created to use some of the known methods of disabling tracking in Windows 10.

## DOWNLOAD

[DOWNLOAD EXE HERE](https://github.com/10se1ucgo/DisableWinTracking/releases/)

## How to Use

You can either:

A. [Run the binary uploaded to the Release tab as an Administrator and select which options you'd like](https://github.com/10se1ucgo/DisableWinTracking/releases/)

B. Install Python and the dependencies listed below and run the script from an elevated command prompt and select which options you'd like  

## Dependencies
This is only to run the script from source, [download the exe here](https://github.com/10se1ucgo/DisableWinTracking/releases/)
* Tested on Python 3
* [wxPython](http://wxpython.org/download.php) -- GUI (Tested with wxPython=Phoenix)
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

#### IP Blocking

Blocks known tracking IPs with the Windows Firewall. The rules are named TrackingIPX, replacing X with the IP numbers.

#### Windows Defender

Disables the following:
- Automatic Sample Submission
- Delivery Optimization Download Mode
 
#### WifiSense
Disables the following:
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

```
Copyright (C) 10se1ucgo 2016

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
