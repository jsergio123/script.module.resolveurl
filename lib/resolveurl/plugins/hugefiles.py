"""
Plugin for ResolveURL
Copyright (C) 2013 Vinnydude

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
from six.moves import urllib_request, urllib_parse
from resolveurl.plugins.lib import captcha_lib
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()


class HugefilesResolver(ResolveUrl):
    name = "hugefiles"
    domains = ["hugefiles.net", "hugefiles.cc"]
    pattern = r'(?://|\.)(hugefiles\.(?:net|cc))/([0-9a-zA-Z/]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        logger.log_debug('HugeFiles: get_link: %s' % (web_url))
        html = self.net.http_GET(web_url).content

        r = re.findall('File Not Found', html)
        if r:
            raise ResolverError('File Not Found or removed')

        # Grab data values
        data = helpers.get_hidden(html)
        data.update(captcha_lib.do_captcha(html))
        logger.log_debug('HugeFiles - Requesting POST URL: %s with data: %s' % (web_url, data))
        html = self.net.http_POST(web_url, data).content

        # Re-grab data values
        data = helpers.get_hidden(html)
        data['referer'] = web_url
        headers = {'User-Agent': common.EDGE_USER_AGENT}
        logger.log_debug('HugeFiles - Requesting POST URL: %s with data: %s' % (web_url, data))
        request = urllib_request.Request(web_url, data=urllib_parse.urlencode(data), headers=headers)

        try:
            stream_url = urllib_request.urlopen(request).geturl()
        except:
            return

        logger.log_debug('Hugefiles stream Found: %s' % stream_url)
        return stream_url

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://hugefiles.cc/{media_id}')

    @classmethod
    def isPopup(self):
        return True
