"""
LSR-specific helper functions

...
"""

# Imports
import pytz
from datetime import datetime, timedelta
from dateutil import parser, tz
from Timing import arc_time_from_cur, cur_time_from_arc

# Go from lsr `type` to gr_icon (also used to just keep our LSRs of interest)
def type_to_icon(type_str):
    type_dict = {'C': 1, 'H': 2, 'T': 3, 'D': 4}
    if type_str in type_dict:
        return type_dict[type_str]
    else:
        return None

# Create a GR Placefile entry for a lsr tuple
def gr_lsr_placefile_row(lsr_tuple, wrap_length):
    return """Object: {lat:.2f}, {lon:.2f}
Icon: 0,0,000,{icon},1,"{text}"
End:""".format(lat=lsr_tuple[2], lon=lsr_tuple[3], icon=type_to_icon(lsr_tuple[8]), text=("%r"%gr_lsr_text(lsr_tuple, wrap_length=wrap_length))[1:-1])

# Create the GR LSR text box text
def gr_lsr_text(lsr_tuple, wrap_length):
    fields = [lsr_tuple[9],
              parser.parse(lsr_tuple[10]).astimezone(pytz.timezone('US/Central')).strftime('%-I:%M %p'),
              lsr_tuple[0],
              '{}, {}'.format(lsr_tuple[1], lsr_tuple[7]),
              lsr_tuple[6],
              "\n".join(textwrap.wrap(lsr_tuple[5], wrap_length))]

    if fields[0] == 'HAIL':
        fields[-1] = '{} INCH'.format(lsr_tuple[4])

    pad = str(max([len(field) for field in fields[0:4]]))
    template = 'Event:  {:>'+pad+'}\nTime:   {:>'+pad+'}\nPlace:  {:>'+pad+'}\nCounty: {:>'+pad+'}\nSource: {:>'+pad+'}\n\n{}'

    return template.format(*fields)

# Scale the raw lsr tuples from arc to cur time (element 10)
def scale_raw_lsr_to_cur_time(raw_tuple_list, timings):
    scaled_tuple_list = []
    for raw_tuple in raw_tuple_list:
        scaled_tuple_list.append((
            raw_tuple[0],
            raw_tuple[1],
            raw_tuple[2],
            raw_tuple[3],
            raw_tuple[4],
            raw_tuple[5],
            raw_tuple[6],
            raw_tuple[7],
            raw_tuple[8],
            raw_tuple[9],
            cur_time_from_arc(raw_tuple[10], timings=timings),
            raw_tuple[11],
        ))
    return scaled_tuple_list