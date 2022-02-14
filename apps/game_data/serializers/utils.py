"""
Serializer-related utility code not linked to a specific serializer.
"""
from collections.abc import Mapping

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings
from rest_framework.utils import html


class JSONDashConvertMixin:
    """
    Mixin for serializers that are ingesting/outputting JSON that
    uses dashes in keynames. Will map these names that use underscores
    ie some-id will become some_id.
    """

    def to_internal_value(self, data):
        """Swap out dashes in incoming data."""
        new_dict = {}
        for field_name in data:
            if '-' in field_name:
                new_name = field_name.replace('-', '_')
            else:
                new_name = field_name
            new_dict[new_name] = data[field_name]

        return super().to_internal_value(new_dict)

    def to_representation(self, instance):
        """Back-convert underscores in outgoing data."""
        initial_repr = super().to_representation(instance)
        new_dict = {}
        for field_name in initial_repr:
            if '_' in field_name:
                new_name = field_name.replace('_', '-')
            else:
                new_name = field_name
            new_dict[new_name] = initial_repr[field_name]
        return new_dict


class IDKeyListSerializer(serializers.ListSerializer):
    """
    For cleanly handling JSON where object IDs are used as keys in what is
    otherwise a 'flat' object listing.

    ID key will be fed to child class via context in all child operations.
    """

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            return self.to_representation(self.initial_data)
        return {}

    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if html.is_html_input(data):
            data = html.parse_html_list(data, default={})

        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        if not self.allow_empty and len(data) == 0:
            message = self.error_messages['empty']
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='empty')

        if self.max_length is not None and len(data) > self.max_length:
            message = self.error_messages['max_length'].format(
                max_length=self.max_length)
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='max_length')

        if self.min_length is not None and len(data) < self.min_length:
            message = self.error_messages['min_length'].format(
                min_length=self.min_length)
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='min_length')

        ret = []
        errors = []

        for key in data:
            self.child.context['key'] = data[key]
            try:
                validated = self.child.run_validation(data[key])
            except ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret.append(validated)
                errors.append({})

        if any(errors):
            raise ValidationError(errors)

        return ret
