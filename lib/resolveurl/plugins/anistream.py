"""
    Plugin for ResolveUrl
    Copyright (C) 2020 Anis

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

from resolveurl.plugins.lib import helpers
import re
import base64
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class AniStreamResolver(ResolveUrl):
    name = "ani-stream"
    domains = ["ani-stream.com"]
    pattern = r'(?://|\.)(ani-stream\.com)/(?:embed-)?([0-9a-zA-Z-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search(r'base64,([^"]+)', html)
        if r:
            html = base64.b64decode(r.group(1)).decode('utf-8')
            sources = helpers.scrape_sources(html)
            if sources:
                return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/embed-{media_id}.html')
