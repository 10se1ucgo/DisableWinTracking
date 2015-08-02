# DisableWinTracking
[GIF of GUI](http://i.imgur.com/AV8btDc.gifv)  
A tool that I created to use some of the known methods of disabling tracking in Windows 10.

## Dependencies
* wxPython
* PyWin32
* Windows 10 (Duh)

## Methods Used
#### Telemetry
Set the "AllowTelemetry" string in "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection" to 0

#### DiagTrack Log
Clears log and disables writing to the log located in "C:\ProgramData\Microsoft\Diagnosis\ETLLogs\AutoLogger"

#### Services
* Delete: Remove both services
* Disable: Set the "Start" registry key for both services to 4 (Disabled) Located at "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\"

#### HOSTS
Append known tracking domains to the HOSTS file located in "C:\Windows\System32\drivers\etc"



## How to use
You can either  
A. Install Python and the 2 dependencies and run the script from an elevated (admin) command prompt and select which options you'd like  
B. Run the binary uploaded to the Release tab as an Administrator and select which options you'd like  

## Delete Services vs Disable Services?
Selecting the "Delete" choice will completely delete the tracking services. This is the recommended choice.  
Selecting "Disable" however will simply stop the services from being able to run.
#  
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

