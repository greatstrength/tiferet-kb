"""tiferet_kb Cache Seed Blueprint Tests"""

# *** imports

# ** core
import ast
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.assets.app import (
    CORE_DEFAULT_APP_SESSIONS,
    CORE_DEFAULT_CONSTANTS,
    CORE_DEFAULT_SERVICES,
)
from tiferet.assets.error import CORE_DEFAULT_ERRORS
from tiferet.contexts.cache import CacheContext
from tiferet.domain import AppServiceDependency, AppSession, Error, Feature

from tiferet_kb.assets.app import KB_DEFAULT_APP_SESSIONS, KB_DEFAULT_SERVICES
from tiferet_kb.assets.error import KB_DEFAULT_ERRORS
from tiferet_kb.assets.feature import KB_DEFAULT_FEATURES
from tiferet_kb.blueprints import build_cache
from tiferet_kb.blueprints.core import build_cache as core_build_cache

# *** functions

# ** function: source_text
def source_text() -> str:
    '''
    Return the blueprint module source.

    :return: The source of ``tiferet_kb/blueprints/core.py``.
    :rtype: str
    '''

    # Read the module the FunctionDef test parses.
    return Path(__file__).resolve().parents[1].joinpath('core.py').read_text()

# ** function: function_def
def function_def() -> ast.FunctionDef:
    '''
    Return the ``build_cache`` function definition.

    :return: The parsed function.
    :rtype: ast.FunctionDef
    '''

    # Find the named function. Decorators hide its runtime signature.
    tree = ast.parse(source_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'build_cache':
            return node
    raise AssertionError('build_cache FunctionDef is missing')

# *** tests

# ** test: function_def_has_one_cache_argument
def test_function_def_has_one_cache_argument():
    '''The source function takes cache and nothing else.'''

    fn = function_def()
    assert [arg.arg for arg in fn.args.args] == ['cache']
    assert fn.args.vararg is None
    assert fn.args.kwonlyargs == []
    assert fn.args.kwarg is None
    assert len(fn.args.defaults) == 1
    assert isinstance(fn.args.defaults[0], ast.Constant)
    assert fn.args.defaults[0].value is None

# ** test: decorator_stack_is_the_four_catalogs
def test_decorator_stack_is_the_four_catalogs():
    '''The source stack is features, sessions, services, then errors.'''

    names = []
    for decorator in function_def().decorator_list:
        assert isinstance(decorator, ast.Call)
        assert isinstance(decorator.func, ast.Name)
        assert len(decorator.args) == 1
        assert decorator.keywords == []
        assert isinstance(decorator.args[0], ast.Name)
        names.append((decorator.func.id, decorator.args[0].id))
    assert names == [
        ('add_default_features', 'KB_DEFAULT_FEATURES'),
        ('add_default_app_sessions', 'KB_DEFAULT_APP_SESSIONS'),
        ('add_default_app_services', 'KB_DEFAULT_SERVICES'),
        ('add_default_errors', 'KB_DEFAULT_ERRORS'),
    ]

# ** test: body_forwards_cache_to_the_app_wrap
def test_body_forwards_cache_to_the_app_wrap():
    '''The only statement returns the framework app cache with cache forwarded.'''

    statements = [
        node for node in function_def().body
        if not isinstance(node, ast.Expr)
    ]
    assert len(statements) == 1
    call = statements[0].value
    assert isinstance(statements[0], ast.Return)
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == 'build_app_cache'
    assert len(call.args) == 1
    assert isinstance(call.args[0], ast.Name)
    assert call.args[0].id == 'cache'
    assert call.keywords == []

    # The alias is the app wrap, not the core or admin builder.
    source = source_text()
    assert 'from tiferet.blueprints.app import build_cache as build_app_cache' in source

# ** test: source_imports_the_owning_modules
def test_source_imports_the_owning_modules():
    '''Decorators come from their owning modules, and the banned names are absent.'''

    source = source_text()
    for required in (
        'tiferet.contexts.feature',
        'tiferet.contexts.app',
        'tiferet.contexts.error',
        'tiferet.blueprints.app',
    ):
        assert required in source
    assert 'from tiferet.contexts import' not in source
    for banned in (
        'add_default_catalog',
        'model=',
        'id_field=',
        'h5_file',
        'KB_DEFAULT_CONSTANTS',
        'KB_DEFAULT_COMMANDS',
        'tiferet.domain',
        'tiferet_kb.domain',
        'tiferet.blueprints.core',
        'tiferet.blueprints.admin',
    ):
        assert banned not in source

# ** test: package_exports_build_cache_only
def test_package_exports_build_cache_only():
    '''The blueprint package exports build_cache and does not export the client.'''

    import tiferet_kb.blueprints as blueprints

    assert blueprints.__all__ == ['build_cache']
    assert blueprints.build_cache is build_cache is core_build_cache
    assert not hasattr(blueprints, 'App')
    assert not hasattr(blueprints, 'KB')
    assert not hasattr(blueprints, 'build_kb')
    init_source = Path(__file__).resolve().parents[3].joinpath(
        'tiferet_kb',
        '__init__.py',
    ).read_text()
    assert 'build_cache' not in init_source

# ** test: build_cache_returns_a_context_and_rejects_a_path
def test_build_cache_returns_a_context_and_rejects_a_path():
    '''A call with no arguments returns a cache. A path keyword is a type error.'''

    assert isinstance(build_cache(), CacheContext)
    with pytest.raises(TypeError):
        build_cache(h5_file='kb.h5')

# ** test: seeded_keys_are_the_live_union
def test_seeded_keys_are_the_live_union():
    '''Catalog keys are the live framework union plus the knowledge-base dicts.'''

    cache = build_cache()
    errors = cache.get_by_prefix('app', 'errors')
    services = cache.get_by_prefix('app', 'services')
    features = cache.get_by_prefix('app', 'features')
    sessions = cache.get_by_prefix('app', 'sessions')
    constants = cache.get_by_prefix('app', 'constants')

    assert set(errors) == set(CORE_DEFAULT_ERRORS) | set(KB_DEFAULT_ERRORS)
    assert len(errors) == len(CORE_DEFAULT_ERRORS) + len(KB_DEFAULT_ERRORS)
    assert set(services) == set(CORE_DEFAULT_SERVICES) | set(KB_DEFAULT_SERVICES)
    assert len(services) == len(CORE_DEFAULT_SERVICES) + len(KB_DEFAULT_SERVICES)
    assert set(features) == set(KB_DEFAULT_FEATURES)
    assert set(sessions) == set(CORE_DEFAULT_APP_SESSIONS) | set(KB_DEFAULT_APP_SESSIONS)
    assert len(sessions) == len(CORE_DEFAULT_APP_SESSIONS) + len(KB_DEFAULT_APP_SESSIONS)
    assert set(constants) == set(CORE_DEFAULT_CONSTANTS)
    assert cache.get('default', 'logging') is not None

# ** test: seeded_values_keep_their_ids
def test_seeded_values_keep_their_ids():
    '''Each seeded row keeps the id the decorator injected from its dict key.'''

    cache = build_cache()
    for key, value in cache.get_by_prefix('app', 'errors').items():
        assert isinstance(value, Error)
        assert value.id == key
    for key, value in cache.get_by_prefix('app', 'services').items():
        assert isinstance(value, AppServiceDependency)
        assert value.service_id == key
    for key, value in cache.get_by_prefix('app', 'features').items():
        assert isinstance(value, Feature)
        assert value.id == key
    session = cache.get('kb', 'app', 'sessions')
    assert isinstance(session, AppSession)
    assert session.id == 'kb'
    assert 'admin' in cache.get_by_prefix('app', 'sessions')
    assert 'admin_cli' in cache.get_by_prefix('app', 'sessions')

# ** test: root_dict_does_not_override_a_prefix
def test_root_dict_does_not_override_a_prefix():
    '''A root key does not replace a session or an error of the same name.'''

    cache = build_cache({'marker': 1, 'kb': 'root', 'APP_ERROR': 'root'})
    assert cache.get('marker') == 1
    assert cache.get('kb') == 'root'
    assert cache.get('APP_ERROR') == 'root'
    assert cache.get('kb', 'app', 'sessions').id == 'kb'
    assert cache.get('APP_ERROR', 'app', 'errors').id == 'APP_ERROR'
