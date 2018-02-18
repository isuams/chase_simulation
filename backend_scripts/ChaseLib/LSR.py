"""
LSR-specific helper functions

...
"""

# Go from lsr `type` to gr_icon (also used to just keep our LSRs of interest)
def type_to_icon(type_str):
    type_dict = {'C': 1, 'H': 2, 'T': 3, 'D': 4}
    if type_str in type_dict:
        return type_dict[type_str]
    else:
        return None