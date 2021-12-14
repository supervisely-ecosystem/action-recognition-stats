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

    f.set_solo_buttons_by_tags(selected_tags=[first_tag, second_tag], fields_to_update=fields_to_update)



