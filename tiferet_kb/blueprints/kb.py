"""tiferet_kb Session Client"""

# *** imports

# ** app
from tiferet.assets.app import APP_CONSTANT_CACHE_PREFIX
from tiferet.blueprints.core import (
    build_app_service_container,
    build_service_resolver,
    compose_session_context,
    create_request_context,
    get_app_session,
    response_handler,
)
from tiferet.contexts.app import AppSessionContext
from tiferet_kb.blueprints.core import build_cache

# *** blueprints

# ** blueprint: build_kb
def build_kb(h5_file: str) -> AppSessionContext:
    '''
    Open one knowledge-base file and return the framework session hub.

    The caller supplies the path. Repository rows stay empty, so that path
    is the constant the five repositories receive. Commands are feature ids
    on the returned hub.

    :param h5_file: The filesystem path of the knowledge-base file.
    :type h5_file: str
    :return: The wired application session hub.
    :rtype: AppSessionContext
    '''

    # Seed the framework cache and the knowledge-base catalogs.
    cache = build_cache()

    # Write the caller path where the container reads constants.
    cache.set('h5_file', h5_file, *APP_CONSTANT_CACHE_PREFIX)

    # Resolve the seeded session. A hit does not open another file.
    app_session = get_app_session('kb', cache)

    # Build the container from the cache. The session adds no overrides.
    app_container = build_app_service_container(cache, app_session)

    # Register that container under the app flag.
    resolver = build_service_resolver(app_container)

    # Register it again with no flags so an unflagged run hits it.
    resolver.add_container(app_container)

    # Return the framework hub. The context type is an argument.
    return compose_session_context(
        AppSessionContext,
        app_session,
        cache,
        resolver,
        create_request_handler=create_request_context,
        response_handler=response_handler,
    )
