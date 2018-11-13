'''
thevideo resolveurl plugin
Copyright (C) 2014 Eldorado

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
import json
from urllib2 import HTTPError
from lib import helpers
from resolveurl import common
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError


class TheVideoResolver(ResolveUrl):
    name = "thevideo"
    domains = ["vev.io"]
    pattern = '(?://|\.)((?:vev\.io))/(?:embed/)?(\w+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.SMR_USER_AGENT}


    def get_media_url(self, host, media_id):
        try:
            result = self.__check_auth(media_id)
            if not result:
                result = self.__auth_ip(media_id)
        except ResolverError:
            raise

        if result:
            return helpers.pick_source(result)
        else:
            raise ResolverError('No Video Streams')


    def __auth_ip(self, media_id):
        header = i18n('thevideo_auth_header')
        line1 = i18n('auth_required')
        line2 = i18n('visit_link')
        line3 = i18n('click_pair') % ('https://vev.io/pair')
        with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
            return cd.start(self.__check_auth, [media_id])


    def __check_auth(self, media_id):
        common.logger.log('Checking Auth: %s' % (media_id))
        url = 'https://vev.io/api/pair/' + media_id
        try:
            r = self.net.http_GET(url, headers=self.headers)
            if r._response.getcode() == 200:
                js_result = json.loads(r.content, encoding='utf-8')
                #common.logger.log('Auth Result: %s' % (js_result))
                return js_result.get('qualities', {}).items()
        except ValueError:
            raise ResolverError('Unusable Authorization Response')
        except HTTPError as e:
            if e.code == 400:
                pass # Continue. User hasn't paired yet.
            else:
                raise ResolverError('Unexpected HTTP Response')
        return None


    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vev.io/embed/{media_id}')
