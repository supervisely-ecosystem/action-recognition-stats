import ast
import json
import time
from itertools import chain

import sly_globals as g
import sly_functions as f
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


solo_button_stages = {
    0: {
        'stage': 0,  # disabled
        'soloButtonColorText': '#3d3d3d',
        'soloButtonColorBg': 'white'
    },
    1: {
        'stage': 1,  # tagged frames
        'soloButtonColorText': 'white',
        'soloButtonColorBg': '#ebc85b'
    },
    2: {
        'stage': 2,  # untagged frames
        'soloButtonColorText': '#ebc85b',
        'soloButtonColorBg': 'white'
    }
}


def get_frames_ranges_from_list(unfilled_frames):
    frame_ranges = []

    first_frame_in_range = None
    prev_frame_index = -1

    for frame_index in unfilled_frames:
        if first_frame_in_range is None:
            first_frame_in_range = frame_index
            prev_frame_index = frame_index

        elif frame_index - 1 == prev_frame_index:
            prev_frame_index = frame_index

        else:
            frame_ranges.append([first_frame_in_range, prev_frame_index])

            first_frame_in_range = frame_index
            prev_frame_index = frame_index

    if first_frame_in_range is not None:
        if [first_frame_in_range, prev_frame_index] not in frame_ranges:
            frame_ranges.append([first_frame_in_range, prev_frame_index])

    return frame_ranges


def get_frames_list_from_ranges(frames_ranges):
    frames_set = set()

    for frame_range in frames_ranges:
        for current_frame in range(frame_range[0], frame_range[1] + 1, 1):
            frames_set.add(current_frame)

    return list(frames_set)


def reverse_ranges(frames_ranges, frames_count):
    all_frames = set([current_frame for current_frame in range(frames_count)])
    filled_frames = get_frames_list_from_ranges(frames_ranges)

    unfilled_frames = all_frames - set(filled_frames)
    return get_frames_ranges_from_list(unfilled_frames)


# @lru_cache(maxsize=5)
def get_ranges_to_play(solo_mode, tags_table):
    raw_ranges = []

    video_info = g.api.app.get_field(g.task_id, 'data.videoInfo')

    for row in tags_table:
        if row['solo_button']['stage'] == 1:  # tagged frames
            raw_ranges.append(get_frames_list_from_ranges(row['frameRanges']))
        elif row['solo_button']['stage'] == 2:  # untagged frames
            reversed_ranges = reverse_ranges(row['frameRanges'], video_info['frames_count'])
            raw_ranges.append(get_frames_list_from_ranges(reversed_ranges))

    if len(raw_ranges) == 0:
        return []

    if solo_mode == 'union':
        return get_frames_ranges_from_list(sorted(list(set(chain.from_iterable(raw_ranges)))))
    elif solo_mode == 'intersection':
        raw_ranges = list(map(set, raw_ranges))
        return get_frames_ranges_from_list(sorted(list(set.intersection(*raw_ranges))))
    else:
        return -1


@g.my_app.callback("solo_button_clicked")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def solo_button_clicked(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    button_stats = state['selectedTimelineRow']
    next_stage = (button_stats['soloButtonStage'] + 1) % len(solo_button_stages)

    new_button_stats = solo_button_stages[next_stage]
    row_index = button_stats['index']

    tags_table = g.api.app.get_field(g.task_id, 'data.selectedTagsStats')
    tags_table[row_index]['solo_button'] = new_button_stats

    ranges_to_play = get_ranges_to_play(state['selectedSoloMode'], tags_table)

    fields_to_update[f'state.rangesToPlay'] = ranges_to_play if len(ranges_to_play) > 0 else None
    fields_to_update[f'data.selectedTagsStats[{row_index}].solo_button'] = new_button_stats


@g.my_app.callback("solo_mode_changed")
@sly.timeit
@g.update_fields
@g.my_app.ignore_errors_and_show_dialog_window()
def solo_mode_changed(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    tags_table = g.api.app.get_field(g.task_id, 'data.selectedTagsStats')
    ranges_to_play = get_ranges_to_play(state['selectedSoloMode'], tags_table)
    fields_to_update[f'state.rangesToPlay'] = ranges_to_play if len(ranges_to_play) > 0 else None
