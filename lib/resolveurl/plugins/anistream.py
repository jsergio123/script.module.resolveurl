"""
ani-stream resolveurl plugin
Copyright (C) 2016 quartoxuna

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
from __resolve_generic__ import ResolveGeneric
from lib import helpers


class AniStreamResolver(ResolveGeneric):
    name = "ani-stream"
    domains = ["ani-stream.com"]
    pattern = '(?://|\.)(ani-stream\.com)/(?:embed-)?([0-9a-zA-Z-]+)'

    def get_media_url(self, host, media_id):
        patterns = ['''(?P<url>http[^,]+\.(?:mp4))''']
        return helpers.get_media_url(self.get_url(host, media_id), patterns=patterns).replace(' ', '%20')

    def test(self):
        yield self.test_url("http://www.ani-stream.com/embed-s67cccev9lgm.html", minsize=215000000)
