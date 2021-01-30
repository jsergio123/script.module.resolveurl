# coding=utf-8

"""
    megaupnet.py : script that gets stream url from megaup.net embed videos
    Copyright (C) 2021 ADDON-LAB, KAR10S

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
"""

import re
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.plugins.lib import helpers


class MegaUp_Net(ResolveUrl):
    name = 'MegaUp'
    domains = ['megaup.net']
    pattern = r"(megaup\.net)\/([a-zA-Z0-9)]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        #import web_pdb;web_pdb.set_trace()
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        headers.update({'Referer': web_url})
        match = re.search(r'FILE NOT FOUND', html)
        if match:
            raise ResolverError('File Not Found or removed')

        pattern = "download-timer.*?btn-default.*?href='(.*?)'"
        url = re.findall(pattern,html,re.MULTILINE)
        if url:
            url = url[0]
        else:
            raise ResolverError('File Not Found or removed')

        pattern_seconds = r"var\s*seconds\s*=\s*(\d*)"
        try:
            seconds = int(re.findall(pattern_seconds, html, re.MULTILINE)[0])
        except:
            seconds = 6
        
        common.kodi.sleep(seconds*1000 + 600)
        urlfromlocationheader = helpers.get_redirect_url(url, headers=headers)
        if urlfromlocationheader:
            return urlfromlocationheader

        raise ResolverError('File Not Found or removed')


    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/{media_id}')
