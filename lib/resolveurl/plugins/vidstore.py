# -*- coding: UTF-8 -*-
"""
    Plugin for ResolveURL
    Copyright (C) 2017  zlootec

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


class VidstoreResolver(ResolveUrl):
    name = "vidstore"
    domains = ["vidstore.me"]
    pattern = r'(?://|\.)(vidstore\.me)/(.+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        sources = re.findall(r'''<source\s+src\s*=\s*['"]([^'"]+).+?label\s*=\s*['"]([^'"]+)''', html, re.DOTALL)
        if sources:
            sources = [(i[1], i[0]) for i in sources]
            sources = sorted(sources, key=lambda x: x[0], reverse=True)
            source = 'http://www.%s%s' % (host, helpers.pick_source(sources))
            headers['Referer'] = web_url
            source = self.net.http_GET(source, headers=headers).get_url()
            return source + helpers.append_headers(headers)
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/{media_id}')
