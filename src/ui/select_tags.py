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

    f.set_solo_buttons_by_tags(selected_tags=[selected_tag], fields_to_update=fields_to_update)


