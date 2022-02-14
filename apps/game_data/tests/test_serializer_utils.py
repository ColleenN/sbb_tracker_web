from django.test import TestCase
from rest_framework import serializers

from apps.game_data.serializers.utils import (
    IDKeyListSerializer,
    JSONDashConvertMixin
)


from rest_framework.fields import empty

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
