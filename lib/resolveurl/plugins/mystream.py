"""
    plugin for ResolveURL
    Copyright (C) 2019 gujal

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
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class MystreamResolver(ResolveUrl):
    name = "mystream"
    domains = ['mystream.la', 'mystream.to', 'mstream.xyz', 'mstream.cloud']
    pattern = r'(?://|\.)(my?stream\.(?:la|to|cloud|xyz))/(?:external|watch/)?([0-9a-zA-Z_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if "unable to find the video" in html:
            raise ResolverError('The requested video was not found or may have been removed.')

        match = re.search(r'og:image".+?"(.+)/', html)
        if match:
            stream_url = '{0}.mp4'.format(match.group(1))
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://embed.mystream.to/{media_id}')
