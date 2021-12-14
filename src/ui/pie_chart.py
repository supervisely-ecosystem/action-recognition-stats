import ast
import json
import time

import sly_globals as g
import sly_functions as f
import sly_constants as c

import supervisely_lib as sly


def init_fields(state, data):
    state['selectedSegment'] = None
    state['pieChartSelectedSector'] = {
        'label': '-',
        'value': '-',
    }

    data['timelineTags'] = None

    data['tagsOnPieChart'] = c.pie_chart_template
    data['valuesOnPieChart'] = c.pie_chart_template

    state['loadingPieChart'] = False


@g.my_app.callback("pie_chart_tag_selected")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def pie_chart_tag_selected(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    fields_to_update['state.loadingPieChart'] = False
    selected_tag = state['pieChartSelectedSector']
    f.fill_pie_chart_values_by_tag_name(tag_name=selected_tag['label'],
                                        fields_to_update=fields_to_update)


@g.my_app.callback("pie_chart_value_selected")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def pie_chart_value_selected(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    fields_to_update['state.loadingPieChart'] = False
    selected_tag = state['pieChartSelectedSector']

    selected_tag = {'tag': str(selected_tag['label']),
                    'value': str(selected_tag['value'])}

    f.set_solo_buttons_by_tags(selected_tags=[selected_tag], fields_to_update=fields_to_update)

