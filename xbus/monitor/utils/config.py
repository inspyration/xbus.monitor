"""Utilities for the configuration file.
"""


def bool_setting(config, setting):
    """Read a boolean setting from the configuration file; that setting may be
    expressed as a string.
    """

    value = config.get(setting, True)

    if isinstance(value, str):
        if value.lower() in ('false', 'no', 'n', '0'):
            value = False
        else:
            value = True

    return value
