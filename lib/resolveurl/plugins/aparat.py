"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal

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
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class AparatResolver(ResolveUrl):
    name = "aparat"
    domains = ['aparat.cam']
    pattern = r'(?://|\.)(aparat\.cam)/(?:embed-)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        url = re.search(r'sources.*?(http[^"]+)',html)
        if url:
            html = self.net.http_GET(url.group(1), headers=headers).content
            html = html.replace('iframes', 'index')
            sources = re.findall('RESOLUTION=\d+x([\d]+).*?CODECS=".*?URI="([^"]+)', html, re.IGNORECASE)
            headers = {'Referer': 'https://aparat.cam/', 'Origin': 'https://aparat.cam', 'User-Agent': common.FF_USER_AGENT, 'Accept': '*/*'}
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)
        else:
            match = re.search(r'&hash=([^&]+)', html)
            if match:
                web_url = 'https://{0}/dl?op=download_orig&id={1}&mode=o&hash={2}'.format(host, media_id, match.group(1))
                html = self.net.http_GET(web_url, headers=headers).content
                r = re.search(r'<a\s*href="([^"]+)[^>]+>Direct', html)
                if r:
                    return r.group(1) + helpers.append_headers({'User-Agent': common.FF_USER_AGENT})
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/embed-{media_id}.html')
