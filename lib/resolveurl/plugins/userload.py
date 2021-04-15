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

import re
from random import choice
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class UserLoadResolver(ResolveUrl):
    name = "UserLoad"
    domains = ['userload.co']
    pattern = r'(?://|\.)(userload\.co)/f/(\w+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        html = helpers.get_packed_data(html)
        for_r_pattern = re.findall(r'var (\w+)', html)
        r1_pattern = r'{0}\s*=\s*"([^"]+)'.format(for_r_pattern[3])
        r2_pattern = r'{0}\s*=\s*"([^"]+)'.format(for_r_pattern[5])
        r1 = re.search(r1_pattern, html)
        r2 = re.search(r2_pattern, html)
        request_arguments_1 = ('https://{0}/api/dline/'.format(host), 'hawk', 'eye')
        request_arguments_2 = ('https://{0}/api/request/'.format(host), 'morocco', 'mycountry')
        api_url, key1, key2 = choice([request_arguments_1, request_arguments_2])
        if r1 and r2:
            data = {
                key1: r1.group(1),
                key2: r2.group(1)
            }
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://{0}'.format(host),
                'Referer': web_url
            })
            stream_url = self.net.http_POST(api_url, data, headers=headers).content
            headers.pop('X-Requested-With')
            stream_url = helpers.get_redirect_url(stream_url, headers)
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/f/{media_id}/null')
