"""tiferet_kb Tag H5 Repository Integration Tests"""

# *** imports

# ** core
import os
from pathlib import Path

# ** infra
import pytest
from tiferet_h5.repos import NodeRepository, TableRepository
from tiferet_h5.utils import H5Client

# ** app
from ...mappers.tag import TagAggregate
from .. import tag as tag_module
from ..tag import DOCUMENT_TAGS_TABLE, DocumentTagTableRepository, TagH5Repository

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''
    Provide a temporary HDF5 file path.
    '''
    return str(tmp_path / 'test_kb.h5')

# ** fixture: tag_repo
@pytest.fixture
def tag_repo(h5_file: str) -> TagH5Repository:
    '''
    Provide a TagH5Repository backed by a temporary HDF5 file.
    '''
    return TagH5Repository(h5_file=h5_file)

# *** tests

# ** test_int: save_get_list
def test_int_save_get_list(tag_repo: TagH5Repository):
    '''
    Saving a tag makes it retrievable, including an omitted color.
    '''

    # Save two tags. One omits color. Names may match.
    tag_repo.save(TagAggregate(id='My-Tag', name='Release'))
    tag_repo.save(TagAggregate(id='ship', name='Release', color='blue'))

    # Assert the omitted color reads back as None and the id is unchanged.
    plain = tag_repo.get('My-Tag')
    assert plain is not None
    assert plain.id == 'My-Tag'
    assert plain.name == 'Release'
    assert plain.color is None

    # Assert both tags are listed.
    ids = {tag.id for tag in tag_repo.list()}
    assert ids == {'My-Tag', 'ship'}

# ** test_int: color_clear_persists
def test_int_color_clear_persists(tag_repo: TagH5Repository):
    '''
    Saving a cleared color does not leave the previous color in place.
    '''

    # Save a colored tag, clear it, and save again.
    tag = TagAggregate(id='release', name='Release', color='#3B82F6')
    tag_repo.save(tag)
    tag.set_color(None)
    tag_repo.save(tag)

    # Assert the read color is absent.
    assert tag_repo.get('release').color is None

# ** test_int: association_is_one_row
def test_int_association_is_one_row(tag_repo: TagH5Repository):
    '''
    Repeating tag_document yields one association. Two tags and two documents compose.
    '''

    # Tag one document twice, and cross a second pair.
    tag_repo.tag_document('doc-1', 'release')
    tag_repo.tag_document('doc-1', 'release')
    tag_repo.tag_document('doc-1', 'ship')
    tag_repo.tag_document('doc-2', 'release')

    # Assert membership in both directions, without a duplicate carrier.
    assert tag_repo.list_document_ids('release') == ['doc-1', 'doc-2']
    assert tag_repo.list_document_ids('ship') == ['doc-1']
    pair = '(document_id == b"doc-1") & (tag_id == b"release")'
    assert len(tag_repo.associations.list(pair)) == 1

# ** test_int: untag_and_clear_are_idempotent
def test_int_untag_and_clear_are_idempotent(tag_repo: TagH5Repository):
    '''
    Untag and clear succeed when the association is already absent.
    '''

    # Untag a pair that was never written. The file must not be required.
    tag_repo.untag_document('doc-1', 'release')
    tag_repo.clear_document('doc-1')

    # Tag, untag twice, and clear a document that no longer carries the tag.
    tag_repo.tag_document('doc-1', 'release')
    tag_repo.untag_document('doc-1', 'release')
    tag_repo.untag_document('doc-1', 'release')
    tag_repo.clear_document('doc-1')
    assert tag_repo.list_document_ids('release') == []

# ** test_int: delete_label_uses_remove_node_not_direct_call
def test_int_delete_label_uses_remove_node_not_direct_call(tag_repo: TagH5Repository, h5_file: str):
    '''
    Label deletion removes the group and does not call h5file.remove_node itself.
    '''

    # The repository source must not reach past the concentrated removal.
    source = Path(tag_module.__file__).read_text()
    assert '.h5file.remove_node' not in source

    # Save and delete the label.
    tag_repo.save(TagAggregate(id='release', name='Release'))
    tag_repo.delete('release')
    tag_repo.delete('release')
    assert tag_repo.exists('release') is False

    # The group is gone.
    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists('/kb/tags/release')

# ** test_int: missing_file_reads_do_not_create
def test_int_missing_file_reads_do_not_create(tag_repo: TagH5Repository, h5_file: str):
    '''
    Reads and idempotent association cleanup on a missing file do not create it.
    '''

    # Read and clean up before any write.
    assert tag_repo.get('nope') is None
    assert tag_repo.exists('nope') is False
    assert tag_repo.list() == []
    assert tag_repo.list_document_ids('nope') == []
    assert tag_repo.list_tags_for_document('doc-1') == []
    tag_repo.delete('nope')
    tag_repo.untag_document('doc-1', 'nope')
    tag_repo.clear_document('doc-1')

    # The file was not created.
    assert not os.path.exists(h5_file)

# ** test_int: composes_node_repository
def test_int_composes_node_repository():
    '''
    The tag repository extends the node repo and holds the table repo as a collaborator.
    '''

    # Assert the mixin split that avoids the save/get/exists collision.
    assert issubclass(TagH5Repository, NodeRepository)
    assert not issubclass(TagH5Repository, TableRepository)
    assert DocumentTagTableRepository.table_path == DOCUMENT_TAGS_TABLE
