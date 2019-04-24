
from __resolve_generic__ import ResolveGeneric


class VidFileResolver(ResolveGeneric):
    name = 'idtbox'
    domains = ["idtbox.com"]
    pattern = '(?://|\.)(idtbox\.com)/(?:embed-)?([a-zA-Z0-9]+)'


    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/embed-{media_id}.html')

