from split_settings.tools import include, optional

include('base_settings.py', optional('.local_settings.py'))
