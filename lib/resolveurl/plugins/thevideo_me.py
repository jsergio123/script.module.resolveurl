import re
import urllib
import urllib2
from resolveurl import common
from lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
import resolveurl
import xbmc


class TheVideoMeResolver(ResolveUrl):
    name = "thevideo.me"
    domains = ["thevideo.me"]
    pattern = '(?://|\.)(thevideo\.(?:me|tv|io))/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        web_url_new = response.get_url()
        resolved = resolveurl.resolve(web_url_new)
        #xbmc.log(resolved)
        return(resolved)


    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://thevideo.me/embed-{media_id}')
