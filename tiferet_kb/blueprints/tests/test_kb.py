"""tiferet_kb Session Client Tests"""

# *** imports

# ** core
import ast
import inspect
import sys
import types
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.assets.app import APP_CONSTANT_CACHE_PREFIX
from tiferet.contexts.app import AppSessionContext

from tiferet_kb.blueprints.kb import build_kb

# *** constants

# ** constant: repository_ids
REPOSITORY_IDS = (
    'category_service',
    'document_service',
    'template_service',
    'folder_service',
    'tag_service',
)

# *** functions

# ** function: source_text
def source_text() -> str:
    '''
    Return the session-client module source.

    :return: The source of ``tiferet_kb/blueprints/kb.py``.
    :rtype: str
    '''

    # Read the module the FunctionDef test parses.
    return Path(__file__).resolve().parents[1].joinpath('kb.py').read_text()

# ** function: function_def
def function_def() -> ast.FunctionDef:
    '''
    Return the ``build_kb`` function definition.

    :return: The parsed function.
    :rtype: ast.FunctionDef
    '''

    # Find the named function.
    tree = ast.parse(source_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'build_kb':
            return node
    raise AssertionError('build_kb FunctionDef is missing')

# ** function: statements
def statements(fn: ast.FunctionDef) -> list:
    '''
    Return the function body without its docstring.

    :param fn: The parsed function.
    :type fn: ast.FunctionDef
    :return: The executable statements.
    :rtype: list
    '''

    # Drop the docstring expression. Comments are already absent from the AST.
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        return body[1:]
    return body

# ** function: call_name
def call_name(node: ast.AST) -> str:
    '''
    Return the called name.

    :param node: A call node.
    :type node: ast.AST
    :return: The function name.
    :rtype: str
    '''

    # A name or an attribute both have a final id.
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    raise AssertionError('call has no name')

# *** tests

# ** test: function_def_takes_only_the_path
def test_function_def_takes_only_the_path():
    '''The source function takes one annotated path and no mode.'''

    fn = function_def()
    assert [arg.arg for arg in fn.args.args] == ['h5_file']
    annotation = fn.args.args[0].annotation
    assert isinstance(annotation, ast.Name)
    assert annotation.id == 'str'
    assert fn.args.defaults == []
    assert fn.args.vararg is None
    assert fn.args.kwonlyargs == []
    assert fn.args.kwarg is None
    assert not fn.decorator_list

# ** test: body_is_the_seven_compose_statements
def test_body_is_the_seven_compose_statements():
    '''The body is the specified compose sequence and nothing else.'''

    body = statements(function_def())
    assert len(body) == 7
    assert isinstance(body[0], ast.Assign)
    assert call_name(body[0].value) == 'build_cache'
    assert body[0].value.args == []
    assert body[0].value.keywords == []

    cache_set = body[1].value
    assert call_name(cache_set) == 'set'
    assert isinstance(cache_set.args[0], ast.Constant)
    assert cache_set.args[0].value == 'h5_file'
    assert isinstance(cache_set.args[1], ast.Name)
    assert cache_set.args[1].id == 'h5_file'
    assert isinstance(cache_set.args[2], ast.Starred)

    session_call = body[2].value
    assert call_name(session_call) == 'get_app_session'
    assert len(session_call.args) == 2
    assert isinstance(session_call.args[0], ast.Constant)
    assert session_call.args[0].value == 'kb'
    assert isinstance(session_call.args[1], ast.Name)
    assert session_call.args[1].id == 'cache'
    assert session_call.keywords == []

    assert call_name(body[3].value) == 'build_app_service_container'
    assert call_name(body[4].value) == 'build_service_resolver'
    add_container = body[5].value
    assert call_name(add_container) == 'add_container'
    assert len(add_container.args) == 1
    assert add_container.keywords == []

    compose = body[6].value
    assert isinstance(body[6], ast.Return)
    assert call_name(compose) == 'compose_session_context'
    assert [arg.id for arg in compose.args] == [
        'AppSessionContext',
        'app_session',
        'cache',
        'resolver',
    ]
    assert [(kw.arg, kw.value.id) for kw in compose.keywords] == [
        ('create_request_handler', 'create_request_context'),
        ('response_handler', 'response_handler'),
    ]

# ** test: source_does_not_call_the_forbidden_builders
def test_source_does_not_call_the_forbidden_builders():
    '''The client does not rebuild the framework cache or invent a resolver.'''

    source = source_text()
    tree = ast.parse(source)
    called = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called.append(call_name(node))
    for banned in (
        'build_app',
        'build_app_session_context',
        'build_admin_service_resolver',
        'build_kb_service_resolver',
        'DIDynamicServiceResolver',
    ):
        assert banned not in called
    assert 'build_app_service_container' in called
    for banned in (
        'CompilerAppSessionContext',
        'class ',
        'mode=',
        'yaml',
        'config.yml',
        'tiferet.blueprints.app',
    ):
        assert banned not in source

# ** test: package_export_is_lazy_and_outside_the_try
def test_package_export_is_lazy_and_outside_the_try():
    '''KB resolves through __getattr__ and does not hide a missing client.'''

    import tiferet_kb
    import tiferet_kb.blueprints as blueprints

    assert tiferet_kb.__version__ == '1.0.0b4'
    assert 'KB' not in tiferet_kb.__dict__
    assert tiferet_kb.KB is build_kb
    assert inspect.isfunction(tiferet_kb.KB)
    assert not inspect.isclass(tiferet_kb.KB)
    from tiferet_kb import KB
    assert KB is build_kb

    assert blueprints.__all__ == ['build_cache']
    assert not hasattr(blueprints, 'KB')
    assert not hasattr(blueprints, 'build_kb')
    assert not hasattr(tiferet_kb, 'build_cache')
    assert not hasattr(tiferet_kb, 'build_kb')
    assert not Path(__file__).resolve().parents[3].joinpath('tiferet_kb', 'contexts').exists()

    init_path = Path(__file__).resolve().parents[3].joinpath('tiferet_kb', '__init__.py')
    init_tree = ast.parse(init_path.read_text())
    try_sources = [
        ast.get_source_segment(init_path.read_text(), node)
        for node in ast.walk(init_tree)
        if isinstance(node, ast.Try)
    ]
    assert try_sources
    for try_source in try_sources:
        assert 'KB' not in try_source
        assert 'build_kb' not in try_source
    getattr_fn = next(
        node for node in init_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == '__getattr__'
    )
    getattr_source = ast.get_source_segment(init_path.read_text(), getattr_fn)
    assert 'build_kb' in getattr_source
    assert 'try' not in getattr_source
    assigned = {
        target.id
        for node in ast.walk(init_tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert 'build_cache' not in assigned
    assert 'build_kb' not in assigned
    assert 'KB' not in assigned

    classes = []
    for path in Path(__file__).resolve().parents[3].joinpath('tiferet_kb').rglob('*.py'):
        module = ast.parse(path.read_text())
        for node in ast.walk(module):
            if isinstance(node, ast.ClassDef):
                classes.append(node)
    for node in classes:
        for base in node.bases:
            rendered = ast.unparse(base)
            assert rendered != 'AppSessionContext'
            assert not rendered.endswith('.AppSessionContext')

# ** test: missing_client_import_is_not_swallowed
def test_missing_client_import_is_not_swallowed(monkeypatch):
    '''A broken client import raises from KB and leaves the version readable.'''

    import tiferet_kb

    assert tiferet_kb.__version__ == '1.0.0b4'
    missing = types.ModuleType('tiferet_kb.blueprints.kb')
    monkeypatch.setitem(sys.modules, 'tiferet_kb.blueprints.kb', missing)
    monkeypatch.delitem(tiferet_kb.__dict__, 'KB', raising=False)
    with pytest.raises(ImportError):
        tiferet_kb.__getattr__('KB')

# ** test: build_kb_rejects_a_missing_or_extra_argument
def test_build_kb_rejects_a_missing_or_extra_argument():
    '''The path is required, and mode is not accepted.'''

    with pytest.raises(TypeError):
        build_kb()
    with pytest.raises(TypeError):
        build_kb('kb.h5', mode='r')

# ** test: session_writes_the_path_and_keeps_mode_default
def test_session_writes_the_path_and_keeps_mode_default(tmp_path):
    '''The five repositories receive the caller path and the constructor default.'''

    path = str(tmp_path / 'kb.h5')
    session = build_kb(path)
    assert isinstance(session, AppSessionContext)
    assert session.domain.id == 'kb'
    assert session.domain.services == []
    assert session.domain.constants == {}
    assert session.cache.get('h5_file', *APP_CONSTANT_CACHE_PREFIX) == path
    for service_id in REPOSITORY_IDS:
        for flags in ((), ('app',)):
            repo = session.get_dependency(service_id, *flags)
            assert repo.h5_file == path
            assert repo.mode == 'a'

# ** test: run_persists_without_opening_consumer_yaml
def test_run_persists_without_opening_consumer_yaml(tmp_path, monkeypatch):
    '''An unflagged run persists a category and does not load consumer YAML.'''

    monkeypatch.chdir(tmp_path)
    path = str(tmp_path / 'kb.h5')
    session = build_kb(path)
    di_service = session.get_dependency('di_service')

    def fail_list_all():
        raise RuntimeError('consumer lookup')

    monkeypatch.setattr(di_service, 'list_all', fail_list_all)
    created = session.run(
        'category.add',
        data={'id': 'guides', 'name': 'Guides'},
    )
    assert created.id == 'guides'
    loaded = build_kb(path).run('category.get', data={'id': 'guides'})
    assert loaded.id == 'guides'
    assert not (tmp_path / 'config.yml').exists()
