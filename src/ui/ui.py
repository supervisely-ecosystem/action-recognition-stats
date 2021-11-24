import supervisely_lib as sly
import sly_globals as g

import input_project
import select_video

@sly.timeit
def init(state, data):
    state['buttonsLoading'] = {
        "cacheAnn": False,
    }

    input_project.init_fields(state=state, data=data)
    select_video.init_fields(state=state, data=data)









