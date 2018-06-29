'''
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
import re, urllib, json
from lib import helpers
from lib import unwise
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class WaawResolver(ResolveUrl):
    name = "waaw"
    domains = ["waaw.tv", "hqq.watch", "netu.tv", "hqq.tv"]
    pattern = "(?://|\.)((?:waaw|netu|hqq)\.(?:tv|watch))/(?:watch_video\.php\?v|.+?vid)=([a-zA-Z0-9]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': 'https://waaw.tv/watch_video.php?v=%s&post=1' % media_id}
        html = self.net.http_GET(web_url, headers=headers).content

        if html:
            try:
                data_unwise = unwise.unwise_process(html)
                try:
                    at = re.search('&at=(.*?)&', data_unwise, re.I).groups()[0]
                except:
                    at = ""
                try:
                    http_referer = re.search('&http_referer=(.*?)&', data_unwise, re.I).groups()[0]
                except:
                    http_referer = ""
                player_url = "http://hqq.watch/sec/player/embed_player.php?iss=&vid=%s&at=%s&autoplayed=yes&referer=on&http_referer=%s&pass=&embed_from=&need_captcha=0&hash_from=&secured=0" % (
                media_id, at, http_referer)
                headers.update({'Referer': web_url})
                data_player = self.net.http_GET(player_url, headers=headers).content
                data_unescape = re.findall('document.write\(unescape\("([^"]+)"', data_player)
                data = ""
                for d in data_unescape:
                    data += urllib.unquote(d)

                data_unwise_player = ""
                wise = ""
                wise = re.search('''<script type=["']text/javascript["']>\s*;?(eval.*?)</script>''', data_player,
                                 re.DOTALL | re.I)
                if wise:
                    data_unwise_player = unwise.unwise_process(data_player)

                try:
                    vars_data = re.search('/player/get_md5.php",\s*\{(.*?)\}', data, re.DOTALL | re.I).groups()[0]
                except:
                    vars_data = ""
                matches = re.findall('\s*([^:]+):\s*([^,]*)[,"]', vars_data)
                params = {}
                for key, value in matches:
                    if key == "adb":
                        params[key] = "0/"
                    elif '"' in value:
                        params[key] = value.replace('"', '')
                    else:
                        try:
                            value_var = re.search('var\s*%s\s*=\s*"([^"]+)"' % value, data, re.I).groups()[0]
                        except:
                            value_var = ""
                        if not value_var and data_unwise_player:
                            try:
                                value_var = \
                                re.search('var\s*%s\s*=\s*"([^"]+)"' % value, data_unwise_player, re.I).groups()[0]
                            except:
                                value_var = ""
                        params[key] = value_var

                params = urllib.urlencode(params)
                headers.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': player_url})
                data = ""
                data = self.net.http_GET("http://hqq.watch/player/get_md5.php?" + params, headers=headers).content
                url_data = json.loads(data)
                media_url = "https:" + self.tb(url_data["obf_link"].replace("#", "")) + ".mp4.m3u8"

                if media_url:
                    del headers['X-Requested-With']
                    headers.update({'Origin': 'https://hqq.watch'})
                    return media_url + helpers.append_headers(headers)

            except Exception as e:
                raise ResolverError(e)

        raise ResolverError('Video not found')

    def tb(self, b_m3u8_2):
        j = 0
        s2 = ""
        while j < len(b_m3u8_2):
            s2 += "\\u0" + b_m3u8_2[j:(j + 3)]
            j += 3

        return s2.decode('unicode-escape').encode('ASCII', 'ignore')
		
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id,
                                     template='http://hqq.watch/player/embed_player.php?vid={media_id}&autoplay=no')
