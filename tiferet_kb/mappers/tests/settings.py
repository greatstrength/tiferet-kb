"""tiferet_kb Mapper Test Settings"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import NodeObject

# *** classes

# ** class: MapperAssertions
class MapperAssertions:
    '''
    Internal mixin providing shared assertion helpers for mapper tests.
    '''

    # * attribute: equality_fields
    equality_fields: list[str] = []

    # * attribute: field_normalizers
    field_normalizers: dict[str, callable] = {}

    # * method: assert_model_matches
    def assert_model_matches(
        self,
        model,
        sample: dict,
        equality_fields: list[str] = None,
        field_normalizers: dict = None,
    ):
        '''
        Compare model attributes against a sample data dict using configured fields and normalizers.

        :param model: The model instance to check.
        :param sample: The expected values dict.
        :type sample: dict
        :param equality_fields: Fields to compare (defaults to self.equality_fields).
        :type equality_fields: list[str]
        :param field_normalizers: Per-field normalizers (defaults to self.field_normalizers).
        :type field_normalizers: dict
        '''

        # Use defaults from the class if not provided.
        equality_fields = equality_fields or self.equality_fields
        field_normalizers = field_normalizers or self.field_normalizers

        # Compare each field.
        for field in equality_fields:
            if field not in sample:
                continue

            expected = sample[field]
            actual = getattr(model, field, None)

            normalizer = field_normalizers.get(field)
            if normalizer:
                expected = normalizer(expected)
                actual = normalizer(actual)

            assert actual == expected, (
                f"Mismatch on field '{field}':\n"
                f"  expected: {expected!r}\n"
                f"  actual:   {actual!r}"
            )


# ** class: AggregateTestBase
class AggregateTestBase(MapperAssertions):
    '''
    Base class for testing Aggregate components.

    Subclasses define:
    - aggregate_cls          — the Aggregate class under test
    - sample_data            — aggregate-format sample data
    - equality_fields        — fields to compare
    - field_normalizers      — optional per-field normalizers
    - set_attribute_params   — tuples of (attr, value, expect_error_code | None)
    '''

    # * attribute: aggregate_cls
    aggregate_cls: type[Aggregate] = None

    # * attribute: sample_data
    sample_data: dict = {}

    # * attribute: set_attribute_params
    set_attribute_params: list[tuple[str, any, str | None]] = []

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> Aggregate:
        '''
        Create an aggregate from data. Override for custom constructor signatures.

        :param data: The data to create from (defaults to self.sample_data).
        :type data: dict
        :return: A new aggregate instance.
        :rtype: Aggregate
        '''

        # Create an aggregate using the standard Pydantic constructor.
        return self.aggregate_cls(**(data or self.sample_data))

    # * fixture: aggregate
    @pytest.fixture
    def aggregate(self):
        '''
        Fixture providing an aggregate instance from sample_data.
        '''

        # Skip if no aggregate class is defined.
        if not self.aggregate_cls:
            pytest.skip("aggregate_cls not defined")

        # Create and return the aggregate.
        return self.make_aggregate()

    # * method: test_new
    def test_new(self, aggregate):
        '''
        Verify aggregate instantiation and field values match sample_data.
        '''

        # Assert the aggregate is the correct type.
        assert isinstance(aggregate, self.aggregate_cls)

        # Assert the aggregate fields match the sample data.
        self.assert_model_matches(aggregate, self.sample_data)

    # * method: test_set_attribute
    def test_set_attribute(self, aggregate, attr, value, expect_error_code):
        '''
        Parametrized test for set_attribute (valid and invalid).
        Parametrization is handled by conftest.pytest_generate_tests.
        '''

        # If an error is expected, verify the correct error code is raised.
        if expect_error_code:
            with pytest.raises(TiferetError) as exc_info:
                aggregate.set_attribute(attr, value)
            assert exc_info.value.error_code == expect_error_code

        # Otherwise verify the attribute was updated.
        else:
            aggregate.set_attribute(attr, value)
            assert getattr(aggregate, attr) == value


# ** class: NodeObjectTestBase
class NodeObjectTestBase(MapperAssertions):
    '''
    Base class for testing NodeObject components (HDF5 attribute mappers).

    Subclasses define:
    - node_cls               — the NodeObject class under test
    - aggregate_cls          — the target Aggregate class
    - sample_data            — node-object-format sample data
    - aggregate_sample_data  — aggregate-format expected data
    - equality_fields        — fields to compare on mapped results
    - field_normalizers      — optional per-field normalizers
    - attrs_exclude_fields   — fields expected to be excluded from to_attrs()
    '''

    # * attribute: node_cls
    node_cls: type[NodeObject] = None

    # * attribute: aggregate_cls
    aggregate_cls: type[Aggregate] = None

    # * attribute: sample_data
    sample_data: dict = {}

    # * attribute: aggregate_sample_data
    aggregate_sample_data: dict = {}

    # * attribute: attrs_exclude_fields
    attrs_exclude_fields: list[str] = []

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> Aggregate:
        '''
        Create an aggregate for from_model / round_trip tests.
        Override for custom constructor signatures.

        :param data: The data to create from (defaults to self.aggregate_sample_data).
        :type data: dict
        :return: A new aggregate instance.
        :rtype: Aggregate
        '''

        # Create an aggregate using the standard Pydantic constructor.
        return self.aggregate_cls(**(data or self.aggregate_sample_data))

    # * fixture: aggregate
    @pytest.fixture
    def aggregate(self):
        '''
        Fixture providing an aggregate instance from aggregate_sample_data.
        '''

        # Skip if no aggregate class is defined.
        if not self.aggregate_cls:
            pytest.skip("aggregate_cls not defined")

        # Create and return the aggregate.
        return self.make_aggregate()

    # * method: test_map
    def test_map(self):
        '''
        Verify NodeObject construction -> map() produces a valid aggregate.
        '''

        # Skip if no node class is defined.
        if not self.node_cls:
            pytest.skip("node_cls not defined")

        # Create a node object from sample data and map to aggregate.
        node_obj = self.node_cls.model_validate(self.sample_data)
        mapped = node_obj.map()

        # Assert the mapped aggregate is the correct type and matches expected data.
        assert isinstance(mapped, self.aggregate_cls)
        self.assert_model_matches(mapped, self.aggregate_sample_data)

    # * method: test_from_model
    def test_from_model(self, aggregate):
        '''
        Verify aggregate -> NodeObject conversion.
        '''

        # Skip if no node class is defined.
        if not self.node_cls:
            pytest.skip("node_cls not defined")

        # Convert the aggregate to a node object using the classmethod.
        node_obj = self.node_cls.from_model(aggregate)

        # Assert the result is the correct type.
        assert isinstance(node_obj, self.node_cls)

    # * method: test_to_attrs_excludes_fields
    def test_to_attrs_excludes_fields(self):
        '''
        Verify that to_attrs() excludes the configured fields.
        '''

        # Skip if no exclusions are configured.
        if not self.attrs_exclude_fields:
            pytest.skip("attrs_exclude_fields not defined")

        # Create a node object and serialize to attrs.
        node_obj = self.node_cls.model_validate(self.sample_data)
        attrs = node_obj.to_attrs()

        # Assert each excluded field is absent from the attrs dict.
        for field in self.attrs_exclude_fields:
            assert field not in attrs, (
                f"Field '{field}' should be excluded from to_attrs() "
                f"but was found in: {list(attrs.keys())}"
            )

    # * method: test_round_trip
    def test_round_trip(self, aggregate):
        '''
        Verify aggregate -> NodeObject -> aggregate round-trip.
        '''

        # Skip if no node class is defined.
        if not self.node_cls:
            pytest.skip("node_cls not defined")

        # Convert aggregate to node object and back.
        node_obj = self.node_cls.from_model(aggregate)
        round_tripped = node_obj.map()

        # Assert the round-tripped aggregate matches expected data.
        assert isinstance(round_tripped, self.aggregate_cls)
        self.assert_model_matches(round_tripped, self.aggregate_sample_data)
