"""
    Plugin for ResolveURL
    Copyright (C) 2021  script.module.resolveurl

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

import json
import re
from six import iteritems
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class RumbleResolver(ResolveUrl):
    name = 'rumble'
    domains = ['rumble.com']
    pattern = r'(?://|\.)(rumble\.com)/(?:embed/)?(\w+(?:[-\w]+(?:\.html)?))'

    def get_media_url(self, host, media_id):

        web_url = self.get_url(host, media_id)
        res = self.net.http_GET(web_url).content

        if 'Video not found' in res:
            raise ResolverError('Invalid video link')

        try:
            _json = re.search(r'f\["\w+?"\]=({.+loaded:d\(\)})', res).group(1)
            _json = json.loads(_json.replace(',loaded:d()', ''))
            ua = _json.get('ua')

            streams = []

            for q, s in iteritems(ua.get('mp4')):
                streams.append((q, s['url']))

            return helpers.pick_source(streams[::-1])

        except Exception:

            raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):

        if media_id.endswith('.html'):

            res = self.net.http_GET('https://rumble.com/{0}'.format(media_id)).content
            if '404 Video is not found' in res:
                raise ResolverError('Invalid video link')
            media_id = re.search(r'"video":"(\w+)"', res).group(1)

        return self._default_get_url(host, media_id, template='https://rumble.com/embed/{media_id}/')
