import ast
import json
import time


import sly_globals as g
import sly_functions as f
import sly_constants as c

import supervisely_lib as sly

from functools import lru_cache


def init_fields(state, data):
    state['selectedSegment'] = None

    data['timelineTags'] = None

    state['timelineOptions'] = {
        "pointerColor": "rgba(224,56,62,1)"
    }

    state['selectedTimelineRow'] = None
    state['selectedSoloMode'] = 'union'

    state['rangesToPlay'] = None


@g.my_app.callback("solo_button_clicked")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def solo_button_clicked(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    button_stats = state['selectedTimelineRow']
    next_stage = (button_stats['soloButtonStage'] + 1) % len(c.solo_button_stages)

    new_button_stats = c.solo_button_stages[next_stage]
    row_index = button_stats['index']

    tags_table = g.api.app.get_field(g.task_id, 'data.selectedTagsStats')
    tags_table[row_index]['solo_button'] = new_button_stats

    f.update_play_intervals_by_table(tags_table, state['selectedSoloMode'], fields_to_update)

    fields_to_update[f'data.selectedTagsStats[{row_index}].solo_button'] = new_button_stats


@g.my_app.callback("solo_mode_changed")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def solo_mode_changed(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    tags_table = g.api.app.get_field(g.task_id, 'data.selectedTagsStats')
    f.update_play_intervals_by_table(tags_table, state['selectedSoloMode'], fields_to_update)

