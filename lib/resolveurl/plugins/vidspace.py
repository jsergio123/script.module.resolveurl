'''
    Plugin for ResolveURL
    Copyright (C) 2018 gujal

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
'''
import re
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VidspaceResolve(ResolveUrl):
    name = 'vidspace'
    domains = ["vidspace.io"]
    pattern = '(?://|\.)(vidspace\.io)/(?:embed-)?([a-zA-Z0-9]+)'
	
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': 'https://vidspace.io/'}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            _sources = re.search('''sources\s*:\s*\[(.+?)\]''', html)
            if _sources:
                sources = helpers.scrape_sources(_sources.group(1), result_blacklist=[".smil"], patterns=['''["'](?P<url>[^"',\s]+)'''], generic_patterns=False)
                if sources:
                    headers.update({'Referer': web_url})
                    return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
       
        return self._default_get_url(host, media_id, 'https://{host}/embed-{media_id}.html')
