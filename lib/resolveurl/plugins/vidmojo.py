"""
Plugin for ResolveUrl
Copyright (C) 2021 gujal

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

from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common


class VidMojoResolver(ResolveUrl):
    name = "vidmojo"
    domains = ['vidmojo.net']
    pattern = r'(?://|\.)(vidmojo\.net)/(?:embed-)?([^\n]+)'

    def get_media_url(self, host, media_id):
        if '|' in media_id:
            media_id, referer = media_id.split('|')
        else:
            referer = None
        web_url = self.get_url(host, media_id)
        referer = web_url if referer is None else referer
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        response = self.net.http_GET(web_url, headers=headers).content
        srcs = helpers.scrape_sources(response, patterns=[r'''file:\s*"(?P<url>[^"]+)'''])
        if srcs:
            headers.update({'Referer': web_url})
            return helpers.pick_source(sorted(srcs, reverse=True)) + helpers.append_headers(headers)

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}')
