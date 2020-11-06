"""
Plugin for ResolveUrl
Copyright (C) 2020 groggyegg

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
from resolveurl.plugins.lib import helpers, jsunpack
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamSBResolver(ResolveUrl):
    name = "streamsb"
    domains = ['streamsb.net']
    pattern = r'(?://|\.)(streamsb\.net)/(embed-[0-9a-zA-Z-]+.html)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search(r'''<script type='text/javascript'>(.+?)</script>''', html, re.DOTALL)
        if match:
            data = jsunpack.unpack(match.group(1))
            source = re.search(r'sources:\[{file:"([^"]+)"}]', data)
            if source:
                return source.group(1) + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
