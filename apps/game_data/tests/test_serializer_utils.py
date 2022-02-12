import json

from django.test import TestCase
from rest_framework import serializers

from apps.game_data.serializers.utils import JSONDashConvertMixin


class SampleObject:

    def __init__(self, field_val):
        self.sample_field = field_val


class SampleSerializer(JSONDashConvertMixin, serializers.Serializer):
    """Dummy serializer for testing."""

    sample_field = serializers.CharField()


class TestDashConvertMixin(TestCase):
    """
    Tests for `JSONDashConvertMixin`.
    """

    def setUp(self) -> None:

        self.json = {"sample-field": "value"}
        self.object = SampleObject("value")

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
            {"sample_field": "value"}
        )
