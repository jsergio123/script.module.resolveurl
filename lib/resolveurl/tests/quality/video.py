'''
    Author    : Huseyin BIYIK <husenbiyik at hotmail>
    Year      : 2015
    License   : GPL
    Project   : UMP! (Universal Media Player)

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
'''

import re
import struct
import urlparse
from urllib2 import HTTPError
from resolveurl import common

try:
    import librtmp
except ImportError:
    librtmp = None

try:
    import m3u8
except ImportError:
    m3u8 = None

net = common.Net()


class quality(object):
    def __init__(self):
        self._first8 = None

    @property
    def first8(self):
        if not self._first8:
            self._first8 = net.http_GET(self.url, self.rheaders(0, 7)).content
        return self._first8

    def check(self, url, headers=None):
        urls = url.split("|")
        if len(urls) == 2:
            url, headers = urls
            if isinstance(headers, dict):
                headers.update(dict(urlparse.parse_qsl(headers)))
            else:
                headers = dict(urlparse.parse_qsl(headers))
        self.url = url
        if not headers:
            headers = {}
        self.headers = headers
        tests = [self.test_rtmp,
                 self.test_mp4,
                 self.test_mkv,
                 self.test_flv,
                 self.test_m3u8
                 ]
        for test in tests:
            ret = test()
            if ret is not None:
                return ret

    def rheaders(self, start="0", end=""):
        nheaders = self.headers.copy()
        nheaders["Range"] = "bytes=%s-%s" % (start, end)
        if nheaders.get("domain"):
            nheaders.pop("domain")
        return nheaders

    def filesize(self):
        resp = net.http_HEAD(self.url, self.headers)._response
        return int(resp.info().getheader('Content-Length'))

    def test_mp4(self):
        def find_atom(cur, name):
            while True:
                offset, atom = name_atom(cur)
                if atom == name:
                    return cur, offset
                elif atom is None:
                    return None, None
                else:
                    cur += offset

        def name_atom(cur):
            try:
                data = net.http_GET(self.url, self.rheaders(cur, cur + 7)).content
            except HTTPError, e:
                if e.code == 416:
                    return None, None
                else:
                    raise e
            return struct.unpack(">i4s", data)

        offset, atom = struct.unpack(">i4s", self.first8)
        if atom == "ftyp":
            ret = {"type": "mp4"}
            ret["size"] = self.filesize()
            cur, offset = find_atom(offset, "moov")
            if not cur:
                return ret
            while True:
                cur, offset = find_atom(cur+8, "trak")
                if not cur:
                    return ret
                # it is possible not to meet first trak as video
                cur2, _ = find_atom(cur+8, "tkhd")
                if not cur2:
                    return ret
                whdata = net.http_GET(self.url, self.rheaders(cur2 + 82, cur2 + 89)).content
                w, h = struct.unpack(">II", whdata)
                if abs(w) < 5000 and abs(h) < 5000:
                    ret["width"] = int(w)
                    ret["height"] = int(h)
                    break
            return ret

    def test_flv(self):
        if self.first8[:3] == "FLV":
            ret = {"type": "flv"}
            b1, b2, b3 = struct.unpack("3B", net.http_GET(self.url, self.rheaders(14, 16)).content)
            size = (b1 << 16) + (b2 << 8) + b3
            header = net.http_GET(self.url, self.rheaders(27, 27 + size)).content
            width = re.findall("width.(........)", header)
            height = re.findall("height.(........)", header)
            if len(width) > 0:
                ret["width"] = int(struct.unpack(">d", width[0])[0])
            if len(height) > 0:
                ret["height"] = int(struct.unpack(">d", height[0])[0])
            ret["size"] = self.filesize()
            return ret

    def test_mkv(self):
        if self.first8.encode("hex")[:8] == "1a45dfa3":
            ret = {"type": "mkv"}
            ret["size"] = self.filesize()
            # to do: implement width height detection if needed
            return ret

    def test_m3u8(self):
        if self.first8[:7] == "#EXTM3U":
            if not m3u8:
                raise ImportError
            else:
                ret = {"type": "m3u8"}
                data = net.http_GET(self.url, self.headers).content
                m3u8.loads(data)
            # to do: implement a more detailed detection here if needed
            return ret

    def test_rtmp(self):
        if self.url.startswith("rtmp://") or self.url.startswith("rtmpe://"):
            ret = {"type": "rtmp"}
            if not librtmp:
                raise ImportError
            try:
                rtmp = librtmp.RTMP("rtmp://your.server.net/app/playpath", live=True)
                rtmp.connect()
            except Exception:
                rtmp = librtmp.RTMP("rtmp://your.server.net/app/playpath")
                rtmp.connect
            stream = rtmp.create_stream()
            stream.read(8)
            return ret
