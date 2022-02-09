"""
Custom validators for our serializers.
"""


class ValidateRootJSONPlayer():
    """
    Verifies that the player id in the root level of our JSON doesn't
    contradict data that we've already loaded.
    """
    requires_context = True

    def __call__(self, attrs, serializer_field):


        if serializer_field.parent.instance:

            player_set = serializer_field.parent.instance