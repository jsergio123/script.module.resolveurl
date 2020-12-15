"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
import base64
from resolveurl.plugins.lib import helpers
from resolveurl.plugins.lib import jsunpack
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamvidResolver(ResolveUrl):
    name = "streamvid"
    domains = ["streamvid.co"]
    pattern = r'(?://|\.)(streamvid\.co)/player/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content

        r = re.findall(r'JuicyCodes\.Run\("([^)]+)"\)', html)

        if r:
            jc = r[-1].replace('"+"', '')
            jc = base64.b64decode(jc.encode('ascii'))
            jc = jsunpack.unpack(jc.decode('ascii'))
            sources = helpers.scrape_sources(jc)
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/player/{media_id}/')
