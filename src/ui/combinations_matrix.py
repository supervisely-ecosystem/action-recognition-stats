import ast
import json
import time

import sly_globals as g
import sly_functions as f
import sly_constants as c

import supervisely_lib as sly
import timeline


def init_fields(state, data):
    state['matrixOptions'] = {
        "selectable": True,

        "height": None,
        "verticalLabel": 'TAG: VALUE',
        "horizontalLabel": 'TAG: VALUE',
    }

    state['matrixSelected'] = {
        "rowClass": None,
        "colClass": None,
        "row": None,
        "col": None
    }

    data['matrixData'] = {
        "diagonalMax": 100,
        "maxValue": 100,  # for recolor
        "classes": [],
        "data": []
    }

    state['combinationLoading'] = False


def get_frame_num_by_tags_intersection(first_tag, second_tag):
    tag1_key, tag1_value = [x.strip() for x in first_tag.split(':')]
    tag2_key, tag2_value = [x.strip() for x in second_tag.split(':')]
    frameRange1 = g.tags2stats[tag1_key][tag1_value]['frameRanges']
    frameRange2 = g.tags2stats[tag2_key][tag2_value]['frameRanges']

    return f.get_ranges_intersections_frame(frameRange1, frameRange2)


def get_table_row_indexes_by_tags(tags, table):
    rows_indexes = []

    for tag_to_find in tags:
        for index, row in enumerate(table):
            tag = row.get('tag')
            value = row.get('value')

            if tag == tag_to_find['tag'] and value == tag_to_find['value']:
                rows_indexes.append(index)

    return rows_indexes


def reset_solo_buttons(tags_table):
    for row_index, row in enumerate(tags_table):
        tags_table[row_index]['solo_button'] = c.solo_button_stages[0]

    return tags_table


@g.my_app.callback("matrix_cell_selected")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def matrix_cell_selected(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    first_tag = state['matrixSelected'].get('rowClass')
    second_tag = state['matrixSelected'].get('colClass')

    first_tag = {'tag': first_tag.split(':')[0].strip(),
                 'value': first_tag.split(':')[1].strip()}
    second_tag = {'tag': second_tag.split(':')[0].strip(),
                  'value': second_tag.split(':')[1].strip()}

    tags_table = g.api.app.get_field(g.task_id, 'data.selectedTagsStats')
    rows_indexes = get_table_row_indexes_by_tags([first_tag, second_tag], tags_table)

    reset_solo_buttons(tags_table)

    for row_index in rows_indexes:
        new_button_stats = c.solo_button_stages[1]
        tags_table[row_index]['solo_button'] = new_button_stats

    fields_to_update[f'data.selectedTagsStats'] = tags_table
    fields_to_update[f'state.selectedSoloMode'] = 'intersection'

    f.update_play_intervals_by_table(tags_table, 'intersection', fields_to_update)

    fields_to_update['data.scrollIntoView'] = 'videoPlayer'
    fields_to_update['state.combinationLoading'] = False

