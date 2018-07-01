# -*- coding: utf-8 -*-

"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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

from random import *
import re, math, time, os
from lib import aa_decoder
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()
net = common.Net()

class SpeedVidResolver(ResolveUrl):
    name = "SpeedVid"
    domains = ['speedvid.net']
    pattern = '(?://|\.)(speedvid\.net)/(?:embed-|p-)?([0-9a-zA-Z]+)'
 
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):

        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = net.http_GET(web_url, headers=headers).content
        if html:	
            html = html.encode('utf-8')	
            aa_text = re.findall("""(ﾟωﾟﾉ\s*=\s*/｀ｍ´\s*）\s*ﾉ.+?)</SCRIPT>""", html, re.I)	
            if aa_text:	
                try:	
                    aa_decoded = ''
                    for i in aa_text:
                        try: aa_decoded += str(aa_decoder.AADecoder(re.sub('\(+ﾟДﾟ\)+\s*\[ﾟoﾟ\]\)*\s*\+(.+?)\(+ﾟДﾟ\s*\)+\[ﾟoﾟ\]\)+', r'(ﾟДﾟ)[ﾟoﾟ]+\1(ﾟДﾟ)[ﾟoﾟ])', i)).decode())
                        except: pass	
                    href = re.search("""\.location\s*=\s*['"]\/([^"']+)""", aa_decoded)
                    if href:
                        href = href.group(1)
                        if href.startswith("http"): location = href
                        elif href.startswith("//"): location = "http:%s" % href
                        else: location = "http://www.speedvid.net/%s" % href
                        headers.update({'Referer': web_url, 'Cookie': str((int(math.floor((900-100)*random())+100))*(int(time.time()))*(128/8))})
                        _html = net.http_GET(location, headers=headers).content
                        if _html:
                            _html = _html.encode('utf-8')	
                            _html = _html.replace("\'", '"')
                            sources = helpers.scrape_sources(_html, patterns=['''file\s*:\s*.["'](?P<url>(?=http://s(?:[\d]))[^"']+)'''])
                            if sources:
                                del headers['Cookie']
                                headers.update({'Referer': location})
                                return helpers.pick_source(sources) + helpers.append_headers(headers)
                except Exception as e:
                    raise ResolverError(e)
            raise ResolverError('File not found')							

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://www.{host}/embed-{media_id}.html')
