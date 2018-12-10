import os
import sys
import traceback
import logging
import importlib
from pprint import pformat
import types
from quality import video

bpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(bpath, ".."))
sys.path.append(os.path.join(bpath, "..", ".."))
import plugins  # @IgnorePep8 @UnresolvedImport
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric, ResolveUrl  # @IgnorePep8

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

quality = video.quality()


def safecall(callback, *args, **kwargs):
    try:
        return callback(*args, **kwargs)
    except Exception, e:
        logging.error(traceback.format_exc(e))


def cname(pc):
    modname = pc.__module__
    if modname.startswith("resolveurl."):
        modname = modname[11:]
    return "%s.%s" % (modname, pc.__name__)


for plugin in plugins.__all__:
    mod = safecall(importlib.import_module, "plugins.%s" % plugin)
    if not mod:
        logging.error("ERROR importing plugin %s" % plugin)
        continue
    logging.debug("Succefully loaded plugin %s " % plugin)

classes = ResolveUrl.__class__.__subclasses__(ResolveUrl) + ResolveUrl.__class__.__subclasses__(ResolveGeneric)

__cache = []

for pc in classes:
    pcname = cname(pc)

    if "FacebookResolver" not in pcname and False:
        continue

    # cache classes adresses to prevent duplicate tests
    if pcname not in __cache:
        __cache.append(pcname)
    else:
        continue

    # test class initialization
    p = safecall(pc)
    if not p:
        logging.error("%s : Cannot initialize class" % pcname)

    # test if return type is correct for test method
    iterurl = safecall(p.test)
    if not iterurl or not isinstance(iterurl, types.GeneratorType):
        logging.error("%s : test method must return a generator" % pcname)
        continue

    # test each test item
    for link in iterurl:
        if not link or not isinstance(link, p.test_url):
            logging.error("%s : %s is not an instance of test_url class" % (pcname, repr(link)))
            continue
        logging.info("%s : testing link %s " % (pcname, link.url))

        # test get_host method
        host_id = safecall(p.get_host_and_id, link.url)
        logging.info("%s : get_host_and_id returned %s" % (pcname, repr(host_id)))
        if not (host_id and len(host_id) == 2):
            logging.error("%s : ERROR on get_host_and_id" % pcname)
            continue

        # test get_url method
        get_url = safecall(p.get_url, *host_id)
        logging.info("%s : get_url returned %s" % (pcname, repr(get_url)))
        if not get_url:
            logging.error("%s : ERROR on get_url" % pcname)
            continue

        # test get_media_url method
        media_url = safecall(p.get_media_url, *host_id)
        logging.info("%s : get_media_url returned %s" % (pcname, repr(media_url)))
        if not media_url:
            logging.error("%s : ERROR on get_media_url" % pcname)
            continue
        # test if the resturned media is playable
        try:
            qresult = quality.check(media_url)
        except Exception, e:
            logging.error(traceback.format_exc(e))
            logging.error("%s : ERROR on quality check" % pcname)
            continue
        logging.info("%s : quality returned :\n %s" % (pcname, pformat(qresult)))

        # test if the returned media size is as expected
        if link.minsize and link.minsize > qresult.get("size", 0):
            logging.error("%s : ERROR %s bytes size is > minsize %s" % (pcname,
                                                                        qresult.get("size", 0),
                                                                        link.minsize))
            continue

        # test if the returned video height is as expected
        if link.minheight and link.minheight > qresult.get("height", 0):
            logging.error("%s : ERROR %spx height is > minheight %s" % (pcname,
                                                                        qresult.get("height", 0),
                                                                        link.minheight))
            continue

        # test if the returned video width is as expected
        if link.minwidth and link.minwidth > qresult.get("width", 0):
            logging.error("%s : ERROR %spx width is > minwidth %s" % (pcname,
                                                                      qresult.get("width", 0),
                                                                      link.minwidth))

        # test if the returned video filetype is as expected
        if link.filetype and not link.filetype > qresult.get("type"):
            logging.error("%s : ERROR %s filetype is not %s" % (pcname,
                                                                qresult.get("type", "unknown"),
                                                                link.filetype))
            continue
