"""
    ResolveURL Addon for Kodi
    Copyright (C) 2016 t0mm0, tknorris

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
import functools
from resolveurl.lib import log_utils
import time
import pickle
import hashlib
import os
import shutil
import six
from resolveurl.lib import kodi

logger = log_utils.Logger.get_logger(__name__)

try:
    cache_path = kodi.translate_path(os.path.join(kodi.get_profile(), 'cache'))
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
except Exception as e:
    logger.log('Failed to create cache: %s: %s' % (cache_path, e), log_utils.LOGWARNING)

cache_enabled = kodi.get_setting('use_cache') == 'true'


def reset_cache():
    try:
        shutil.rmtree(cache_path)
        return True
    except Exception as e:
        logger.log('Failed to Reset Cache: %s' % (e), log_utils.LOGWARNING)
        return False


def _get_func(name, args=None, kwargs=None, cache_limit=1):
    if not cache_enabled:
        return False, None
    now = time.time()
    max_age = now - (cache_limit * 60 * 60)
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    full_path = os.path.join(cache_path, _get_filename(name, args, kwargs))
    if os.path.exists(full_path):
        mtime = os.path.getmtime(full_path)
        if mtime >= max_age:
            if six.PY2:
                with open(full_path, 'r') as f:
                    pickled_result = f.read()
            else:
                with open(full_path, 'rb') as f:
                    pickled_result = f.read()
            return True, pickle.loads(pickled_result)

    return False, None


def _save_func(name, args=None, kwargs=None, result=None):
    try:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        pickled_result = pickle.dumps(result)
        full_path = os.path.join(cache_path, _get_filename(name, args, kwargs))
        if six.PY2:
            with open(full_path, 'w') as f:
                f.write(pickled_result)
        else:
            with open(full_path, 'wb') as f:
                f.write(pickled_result)
    except Exception as e:
        logger.log('Failure during cache write: %s' % (e), log_utils.LOGWARNING)


def _get_filename(name, args, kwargs):
    if six.PY2:
        arg_hash = hashlib.md5(name).hexdigest() + hashlib.md5(str(args)).hexdigest() + hashlib.md5(str(kwargs)).hexdigest()
    else:
        arg_hash = hashlib.md5(name.encode('utf8')).hexdigest() + hashlib.md5(str(args).encode('utf8')).hexdigest() + hashlib.md5(str(kwargs).encode('utf8')).hexdigest()
    return arg_hash


def cache_method(cache_limit):
    def wrap(func):
        @functools.wraps(func)
        def memoizer(*args, **kwargs):
            if args:
                klass, real_args = args[0], args[1:]
                full_name = '%s.%s.%s' % (klass.__module__, klass.__class__.__name__, func.__name__)
            else:
                full_name = func.__name__
                real_args = args
            in_cache, result = _get_func(full_name, real_args, kwargs, cache_limit=cache_limit)
            if in_cache:
                logger.log('Using method cache for: |%s|%s|%s| -> |%d|' % (full_name, args, kwargs, len(pickle.dumps(result))), log_utils.LOGDEBUG)
                return result
            else:
                logger.log('Calling cached method: |%s|%s|%s|' % (full_name, args, kwargs), log_utils.LOGDEBUG)
                result = func(*args, **kwargs)
                _save_func(full_name, real_args, kwargs, result)
                return result
        return memoizer
    return wrap


# do not use this with instance methods the self parameter will cause args to never match
def cache_function(cache_limit):
    def wrap(func):
        @functools.wraps(func)
        def memoizer(*args, **kwargs):
            name = func.__name__
            in_cache, result = _get_func(name, args, kwargs, cache_limit=cache_limit)
            if in_cache:
                logger.log('Using function cache for: |%s|%s|%s| -> |%d|' % (name, args, kwargs, len(pickle.dumps(result))), log_utils.LOGDEBUG)
                return result
            else:
                logger.log('Calling cached function: |%s|%s|%s|' % (name, args, kwargs), log_utils.LOGDEBUG)
                result = func(*args, **kwargs)
                _save_func(name, args, kwargs, result)
                return result
        return memoizer
    return wrap
