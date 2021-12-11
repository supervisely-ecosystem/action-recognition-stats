import supervisely_lib as sly

import sly_globals as g
import sly_functions as f
import sly_constants as c



def init_fields(state, data):
    state['selectedTags'] = []

    data['tagsTable'] = []
    data['selectedTagsStats'] = []

    state['selectedRowFromTagsTable'] = None
    state['rowFromTagsTableLoading'] = False


@g.my_app.callback("select_tags")
@sly.timeit
@g.update_fields
# @g.my_app.ignore_errors_and_show_dialog_window()
def select_tags(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    pass


@g.my_app.callback("tags_table_row_selected")
@sly.timeit
@g.update_fields
# @g.my_app.ignore_errors_and_show_dialog_window()
def tags_table_row_selected(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    fields_to_update['state.rowFromTagsTableLoading'] = False
    selected_row = state['selectedRowFromTagsTable']
    if selected_row is None:
        return -1

    selected_tag = {'tag': str(selected_row.get('tag', '')),
                    'value': str(selected_row.get('value', ''))}

    tags_table = g.api.app.get_field(g.task_id, 'data.selectedTagsStats')
    rows_indexes = f.get_table_row_indexes_by_tags([selected_tag], tags_table)

    f.reset_solo_buttons(tags_table)

    for row_index in rows_indexes:
        new_button_stats = c.solo_button_stages[1]
        tags_table[row_index]['solo_button'] = new_button_stats

    fields_to_update[f'data.selectedTagsStats'] = tags_table

    f.update_play_intervals_by_table(tags_table, state['selectedSoloMode'], fields_to_update)

    fields_to_update['data.scrollIntoView'] = 'videoPlayer'

