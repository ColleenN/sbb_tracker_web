from django.test import TestCase
from rest_framework import serializers

from apps.game_data.serializers.utils import (
    ContextDefaulter,
    IDKeyListField,
    IDKeyListSerializer,
    JSONDashConvertMixin
)


class SampleObject:

    def __init__(self, field_val_1, field_val_2):
        self.sample_field_1 = field_val_1
        self.sample_field_2 = field_val_2


class SampleSerializer(JSONDashConvertMixin, serializers.Serializer):
    """Dummy serializer for testing `JSONDashConvertMixin`."""

    sample_field_1 = serializers.CharField()
    sample_field_2 = serializers.CharField()


class TestDashConvertMixin(TestCase):
    """
    Tests for `JSONDashConvertMixin`.
    """

    def setUp(self) -> None:

        self.json = {
            "sample-field-1": "value1",
            "sample-field-2": "value2"
        }
        self.object = SampleObject("value1", "value2")

    def test_representation(self):
        """Test that representation has dash in key name."""
        serializer = SampleSerializer(self.object)
        self.assertEqual(serializer.data, self.json)

    def test_to_internal(self):
        """Verify we're handling incoming JSON with dashes as expected."""
        serializer = SampleSerializer(data=self.json)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {
                "sample_field_1": "value1",
                "sample_field_2": "value2"
            }
        )


class SampleIDKeyChildSerializer(serializers.Serializer):

    sample_field_2 = serializers.CharField()

    class Meta:
        list_serializer_class = IDKeyListSerializer


class TestIDKeyChildSerializer(TestCase):
    """
    Tests for `IDKeyChildSerializer`.
    """

    def setUp(self) -> None:
        """Set up some JSON of the form we're concerned with."""
        self.json = {
            "7": {'sample_field_2': 'value-a'},
            "8": {'sample_field_2': 'value-b'}
        }

    def test_keylist(self):
        """Check that serializer can ingest + transform JSON."""
        serializer = SampleIDKeyChildSerializer(
            data=self.json, many=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            [
                {'sample_field_2': 'value-a'},
                {'sample_field_2': 'value-b'}
            ]
        )
        self.assertEqual(serializer.child.context, {'key': '8'})


class SampleIDKeyListFieldSerializer(serializers.Serializer):

    sample_field = IDKeyListField()


class TestContextDefaulter(TestCase):

    def test_basic_lookup(self):

        class SimpleSerializer(serializers.Serializer):
            sample_field_1 = serializers.CharField(
                default=ContextDefaulter(source='key_1'))
            sample_field_2 = serializers.CharField()

        serializer = SimpleSerializer(
            data={'sample_field_2': 'ValueB'},
            context={'key_1': 'ValueA'}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.data,
            {'sample_field_1': 'ValueA', 'sample_field_2': 'ValueB'}
        )

    def test_nested_lookups(self):

        class SimpleSerializer(serializers.Serializer):
            sample_field_1 = serializers.CharField(
                default=ContextDefaulter(
                    source='key_1.sample_field_2.last_key'))
            sample_field_2 = serializers.CharField(
                default=ContextDefaulter(source='key_2.sample_field_1'))

        obj_1 = SampleObject('Bad Value', {'last_key': 'final_value_1'})
        obj_2 = SampleObject('final_value_2', 'Bad Value')

        serializer = SimpleSerializer(
            context={'key_1': obj_1, 'key_2': lambda: obj_2},
            data={}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.data,
            {
                'sample_field_1': 'final_value_1',
                'sample_field_2': 'final_value_2'
            }
        )


class TestIDKeyListField(TestCase):

    def test_keylist_field(self):

        field_data = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
        }
        data = {'sample_field': field_data}
        serializer = SampleIDKeyListFieldSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.data,
            {'sample_field': ['A', 'B', 'C']}
        )
