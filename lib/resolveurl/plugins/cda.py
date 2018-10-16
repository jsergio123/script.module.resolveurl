"""
    resolveurl XBMC Addon
    Copyright (C) 2015 tknorris

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
from lib import jsunpack
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
import string,requests
from string import maketrans

class CdaResolver(ResolveUrl):
    name = "cda"
    domains = ['cda.pl', 'www.cda.pl', 'ebd.cda.pl']
    pattern = '(?:\/\/|\.)(cda\.pl)\/(?:.\d+x\d+|video)\/(.*)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        intab = "abcdefghijklmnopqrstuvwxyz"
        outtab = "nopqrstuvwxyzabcdefghijklm"
        trantab = maketrans(intab, outtab)
        web_url = str(self.get_url(host, media_id)).split("?")
        web_url = web_url[0]
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        result = requests.get(web_url, headers=headers).content
        if "?wersja=1080p" in result:
            result = requests.get(web_url + "?wersja=1080p", headers=headers).content
            direct = re.findall("""file":"(.*)","file_cast""", result)[0].replace("\\/","/")
            if str(direct).startswith("uggc"):
                direct = direct.translate(trantab)
            return direct
            raise ResolverError('Video Link Not Found')
        if "?wersja=720p" in result:
            result = requests.get(web_url + "?wersja=720p", headers=headers).content
            direct = re.findall("""file":"(.*)","file_cast""", result)[0].replace("\\/","/")
            if str(direct).startswith("uggc"):
                direct = direct.translate(trantab)
            return direct
            raise ResolverError('Video Link Not Found')
        if "?wersja=480p" in result:
            result = requests.get(web_url + "?wersja=480p", headers=headers).content
            direct = re.findall("""file":"(.*)","file_cast""", result)[0].replace("\\/","/")
            if str(direct).startswith("uggc"):
                direct = direct.translate(trantab)
            return direct
            raise ResolverError('Video Link Not Found')
        if "?wersja=360p" in result:
            result = requests.get(web_url + "?wersja=360p", headers=headers).content
            direct = re.findall("""file":"(.*)","file_cast""", result)[0].replace("\\/","/")
            if str(direct).startswith("uggc"):
                direct = direct.translate(trantab)
            return direct
            raise ResolverError('Video Link Not Found')
        result = requests.get(web_url, headers=headers).content
        direct = re.findall("""file":"(.*)","file_cast""", result)[0].replace("\\/","/")
        if str(direct).startswith("uggc"):
            direct = direct.translate(trantab)
        return direct
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return 'http://ebd.cda.pl/647x500/%s' % media_id
