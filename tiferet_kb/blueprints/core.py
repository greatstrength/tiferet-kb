"""tiferet_kb Cache Seed Blueprint"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from tiferet.blueprints.app import build_cache as build_app_cache
from tiferet.contexts.app import (
    add_default_app_services,
    add_default_app_sessions,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import add_default_errors
from tiferet.contexts.feature import add_default_features
from tiferet_kb.assets.app import (
    KB_DEFAULT_APP_SESSIONS,
    KB_DEFAULT_SERVICES,
)
from tiferet_kb.assets.error import KB_DEFAULT_ERRORS
from tiferet_kb.assets.feature import KB_DEFAULT_FEATURES

# *** blueprints

# ** blueprint: build_cache
@add_default_features(KB_DEFAULT_FEATURES)
@add_default_app_sessions(KB_DEFAULT_APP_SESSIONS)
@add_default_app_services(KB_DEFAULT_SERVICES)
@add_default_errors(KB_DEFAULT_ERRORS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Seed the knowledge-base catalogs onto the framework application cache.

    The wrap supplies the framework catalogs. This function layers the four
    knowledge-base catalogs after that wrap returns. It does not open a file.

    :param cache: An optional dict for the root namespace.
    :type cache: Dict[str, Any]
    :return: The cache context seeded with both catalogs.
    :rtype: CacheContext
    '''

    # Forward the optional root dict to the framework cache.
    return build_app_cache(cache)
