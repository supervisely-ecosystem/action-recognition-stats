import ast
import json
import time

import sly_globals as g
import sly_functions as f
import supervisely as sly


def init_fields(state, data):
    state['tagsOnFrame'] = []


