"""
Serializer-related utility code not linked to a specific serializer.
"""


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
        for field_name in initial_repr:
            if '_' in field_name:
                actual = field_name.replace('_', '-')
                initial_repr[actual] = initial_repr.pop(field_name)
        return initial_repr
