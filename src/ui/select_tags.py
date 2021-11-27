import supervisely_lib as sly

import sly_globals as g
import sly_functions as f


def init_fields(state, data):
    state['selectedTags'] = []

    data['tagsTable'] = []
    data['selectedTagsStats'] = []


@g.my_app.callback("select_tags")
@sly.timeit
@g.update_fields
# @g.my_app.ignore_errors_and_show_dialog_window()
def select_tags(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    pass



