# Copyright (C) 10se1ucgo 2015-2016
#
# This file is part of DisableWinTracking.
#
# DisableWinTracking is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DisableWinTracking is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DisableWinTracking.  If not, see <http://www.gnu.org/licenses/>.

# dwt.py will become cluttered enough :^)
import cgi
import json
import urllib2
import webbrowser
from distutils.version import StrictVersion

import wx
import wx.adv
import wx.lib.scrolledpanel as sp

__version__ = "3.2.1"


def about_dialog(parent):
    license_text = """
    Copyright (C) 10se1ucgo 2015-2016

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>."""

    about_info = wx.adv.AboutDialogInfo()
    about_info.SetName("Disable Windows 10 Tracking")
    about_info.SetVersion("v{v}".format(v=__version__))
    about_info.SetCopyright("Copyright (C) 10se1ucgo 2015-2016")
    about_info.SetDescription("A tool to disable tracking in Windows 10")
    about_info.SetWebSite("https://github.com/10se1ucgo/DisableWinTracking", "GitHub repository")
    about_info.AddDeveloper("10se1ucgo")
    about_info.AddDeveloper("Ruined1")
    about_info.SetLicense(license_text)
    wx.adv.AboutBox(about_info, parent)


class Licenses(wx.Dialog):
    def __init__(self, parent):
        super(Licenses, self).__init__(parent, title="Licenses", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.scrolled_panel = sp.ScrolledPanel(self)

        mono_font = wx.Font()
        mono_font.SetFamily(wx.FONTFAMILY_TELETYPE)

        info = wx.StaticText(self.scrolled_panel, label=("DisableWinTracking uses a number of open source software."
                                                         "The following are the licenses for these software."))

        wxw = wx.StaticText(self.scrolled_panel, label=("DisableWinTracking uses wxWidgets and wxPython. Their license "
                                                        "is below\nMore info at https://www.wxwidgets.org/about/"))
        wxw_license = """
                  wxWindows Library License, Version 3.1
                  ======================================
    Copyright (c) 1998-2005 Julian Smart, Robert Roebling et al
    Everyone is permitted to copy and distribute verbatim copies
    of this license document, but changing it is not allowed.
                         WXWINDOWS LIBRARY LICENSE
       TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
    This library is free software; you can redistribute it and/or modify it
    under the terms of the GNU Library General Public License as published by
    the Free Software Foundation; either version 2 of the License, or (at your
    option) any later version.
    This library is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
    License for more details.
    You should have received a copy of the GNU Library General Public License
    along with this software, usually in a file named COPYING.LIB.  If not,
    write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth
    Floor, Boston, MA 02110-1301 USA.
    EXCEPTION NOTICE
    1. As a special exception, the copyright holders of this library give
    permission for additional uses of the text contained in this release of the
    library as licensed under the wxWindows Library License, applying either
    version 3.1 of the License, or (at your option) any later version of the
    License as published by the copyright holders of version 3.1 of the License
    document.
    2. The exception is that you may use, copy, link, modify and distribute
    under your own terms, binary object code versions of works based on the
    Library.
    3. If you copy code from files distributed under the terms of the GNU
    General Public License or the GNU Library General Public License into a
    copy of this library, as this license permits, the exception does not apply
    to the code that you add in this way.  To avoid misleading anyone as to the
    status of such modified files, you must delete this exception notice from
    such code and/or adjust the licensing conditions notice accordingly.
    4. If you write modifications of your own for this library, it is your
    choice whether to permit this exception to apply to your modifications.  If
    you do not wish that, you must delete the exception notice from such code
    and/or adjust the licensing conditions notice accordingly."""
        wxw_text = wx.StaticText(self.scrolled_panel, label=wxw_license)
        wxw_text.SetFont(mono_font)

        pywin = wx.StaticText(self.scrolled_panel, label="DisableWinTracking uses PyWin32. Its license is below.")
        pywin_license = """
    Unless stated in the specific source file, this work is
    Copyright (c) 1996-2008, Greg Stein and Mark Hammond.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions
    are met:

    Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the distribution.

    Neither names of Greg Stein, Mark Hammond nor the name of contributors may be used
    to endorse or promote products derived from this software without
    specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
    IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
    TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
    PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""
        pywin_text = wx.StaticText(self.scrolled_panel, label=pywin_license)
        pywin_text.SetFont(mono_font)

        self.top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        self.scroll_sizer.Add(info, 0, wx.ALL, 2)
        self.scroll_sizer.Add(wxw, 0, wx.ALL, 2)
        self.scroll_sizer.Add(wxw_text, 0, wx.EXPAND | wx.ALL, 3)
        self.scroll_sizer.Add(pywin, 0, wx.ALL, 2)
        self.scroll_sizer.Add(pywin_text, 0, wx.EXPAND | wx.ALL, 3)
        self.top_sizer.Add(self.scrolled_panel, 1, wx.EXPAND)

        self.SetSizerAndFit(self.top_sizer)
        self.scrolled_panel.SetSizerAndFit(self.scroll_sizer)
        self.scrolled_panel.SetupScrolling()
        self.Show()


def update_check(parent):
    try:
        r = urllib2.urlopen('https://api.github.com/repos/10se1ucgo/DisableWinTracking/releases/latest')
    except urllib2.URLError:
        return
    value, parameters = cgi.parse_header(r.headers.get('Content-Type', ''))
    release = json.loads(r.read().decode(parameters.get('charset', 'utf-8')))
    if release['prerelease']:
        return
    new = release['tag_name']
    
    try:
        if StrictVersion(__version__) < StrictVersion(new.lstrip('v')):
            info = wx.MessageDialog(parent, message="DWT {v} is now available!\nGo to download page?".format(v=new),
                                    caption="DWT Update", style=wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
            if info.ShowModal() == wx.ID_OK:
                webbrowser.open_new_tab(release['html_url'])
            info.Destroy()
    except ValueError:
        return
