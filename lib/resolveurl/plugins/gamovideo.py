"""
    Plugin for ResolveUrl
    Copyright (C) 2016 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class GamoVideoResolver(ResolveUrl):
    name = 'GamoVideo'
    domains = ['gamovideo.com']
    pattern = r'(?://|\.)(gamovideo\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        r = self.net.http_GET(web_url, headers=headers)
        cookie = ''
        for item in r.get_headers(as_dict=True)['Set-Cookie'].split('GMT,'):
            cookie += item.split('path')[0]
        headers.update({'Cookie': cookie + 'sugamun=1; invn=1; pfm=1'})

        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        source = re.search(r'''file:\s*["'](?P<url>http[^"']+)["']''', html)
        headers.pop('Cookie')
        if source:
            return source.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/{media_id}')
