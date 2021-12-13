import datetime
from string import Formatter
from itertools import chain

import sly_globals as g
import sly_constants as c

from sly_fields_names import ItemsStatusField


def get_tagged_frames_count_by_annotation(annotation_for_video):
    tagged_frames = set([])

    tags_on_video = annotation_for_video.get('tags', [])

    for current_tag in tags_on_video:
        if current_tag['name'] in g.technical_tags_names:
            continue

        frame_range = current_tag.get('frameRange', None)

        if frame_range:
            for i in range(frame_range[0], frame_range[1] + 1, 1):
                tagged_frames.add(i)

    return len(tagged_frames)


def get_tags_on_video_count_by_annotation(annotation_for_video):
    tags_on_video_count = 0

    tags_on_video = annotation_for_video.get('tags', [])

    for current_tag in tags_on_video:
        if current_tag['name'] in g.technical_tags_names:
            continue

        frame_range = current_tag.get('frameRange', None)

        if frame_range:
            tags_on_video_count += frame_range[1] - frame_range[0] + 1

    return tags_on_video_count


def get_tags_list_by_type(tag_type, video_id):
    video_annotation = g.videos2annotations[video_id]
    tags_on_video = video_annotation.get('tags', [])

    tags_list = []

    for current_tag in tags_on_video:
        if current_tag.get('name') in g.technical_tags_names: # DEBUG
            continue

        frame_range = current_tag.get('frameRange')
        tag_value = current_tag.get('value')

        if tag_value is not None and tag_type == 'video' and frame_range is None:
            tags_list.append(current_tag)
        elif tag_value is not None and tag_type == 'frame' and frame_range:
            tags_list.append(current_tag)

    return tags_list


def tag_in_range(frames_ranges, frame_number):
    for frame_range in frames_ranges:
        if int(frame_range[0]) <= int(frame_number) <= int(frame_range[1]):
            return True
    return False


def get_frames_ranges_from_list(frames_list):
    frame_ranges = []

    first_frame_in_range = None
    prev_frame_index = -1

    for frame_index in frames_list:
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

def update_tags_by_frame(frame_number):
    tags_on_frame = []

    for tag_key in g.tags2stats.keys():
        for tag_value in g.tags2stats[tag_key].keys():
            current_tag = g.tags2stats[tag_key][tag_value]
            frames_ranges = current_tag['frameRanges']

            frames_list = sorted(get_frames_list_from_ranges(frames_ranges))

            if tag_in_range(frames_ranges, frame_number):
                init_row = {
                    'tag': tag_key,
                    'value': tag_value,
                    'color': current_tag['colors'][0],
                    'prev': tag_in_range(frames_ranges, frame_number - 1),
                    'next': tag_in_range(frames_ranges, frame_number + 1),
                    'tag_position': f'{frames_list.index(frame_number) + 1} / {len(frames_list)}'
                }
                tags_on_frame.append(init_row)

    g.api.app.set_field(g.task_id, 'state.tagsOnFrame', tags_on_frame)


def get_ranges_intersections_count(ranges1, ranges2):
    # intersections_count = 0

    ranges1 = set(get_frames_list_from_ranges(ranges1))
    ranges2 = set(get_frames_list_from_ranges(ranges2))

    raw_ranges = [ranges1, ranges2]

    return len((list(set.intersection(*raw_ranges))))
    # print()

    # for current_range1 in ranges1:
    #     for current_range2 in ranges2:
    #         if current_range2[0] <= current_range1[0] <= current_range2[1]:
    #             end_of_inter_segment = min(current_range2[1], current_range1[1])
    #             intersections_count += end_of_inter_segment - current_range1[0] + 1
    #
    #         elif current_range2[0] <= current_range1[1] <= current_range2[1]:
    #             start_of_inter_segment = max(current_range2[0], current_range1[0])
    #             intersections_count += current_range1[1] - start_of_inter_segment + 1
    #
    #
    # for current_range1 in ranges2:
    #     for current_range2 in ranges1:
    #         if current_range1 == current_range2:
    #             continue
    #
    #         if current_range2[0] <= current_range1[0] <= current_range2[1]:
    #             end_of_inter_segment = min(current_range2[1], current_range1[1])
    #             intersections_count += end_of_inter_segment - current_range1[0] + 1
    #
    #         elif current_range2[0] <= current_range1[1] <= current_range2[1]:
    #             start_of_inter_segment = max(current_range2[0], current_range1[0])
    #             intersections_count += current_range1[1] - start_of_inter_segment + 1

    return intersections_count

get_ranges_intersections_count([[260, 758]], [[447, 633], [663, 758]])

def get_ranges_intersections_frame(ranges1, ranges2):
    for current_range1 in ranges1:
        for current_range2 in ranges2:
            if current_range2[0] <= current_range1[0] <= current_range2[1]:
                return current_range1[0]
            elif current_range2[0] <= current_range1[1] <= current_range2[1]:
                return max(current_range2[0], current_range1[0])

    return None




def merge_close_ranges(frame_ranges):
    frames_list = sorted(get_frames_list_from_ranges(frame_ranges))
    return get_frames_ranges_from_list(frames_list)


def merge_tag_value_frame_ranges(tags2stats):
    for tag_name, tag_values in tags2stats.items():
        for tag_value, tag_stats in tag_values.items():
            frame_ranges = tags2stats[tag_name][tag_value].get('frameRanges')
            if frame_ranges is not None:
                tags2stats[tag_name][tag_value]['frameRanges'] = merge_close_ranges(frame_ranges)


def get_frame_num_by_tags_intersection(first_tag, second_tag):
    tag1_key, tag1_value = [x.strip() for x in first_tag.split(':')]
    tag2_key, tag2_value = [x.strip() for x in second_tag.split(':')]
    frameRange1 = g.tags2stats[tag1_key][tag1_value]['frameRanges']
    frameRange2 = g.tags2stats[tag2_key][tag2_value]['frameRanges']

    return get_ranges_intersections_frame(frameRange1, frameRange2)


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


def update_play_intervals_by_table(tags_table, play_mode, fields_to_update):
    ranges_to_play = get_ranges_to_play(play_mode, tags_table)
    fields_to_update[f'state.rangesToPlay'] = ranges_to_play if len(ranges_to_play) > 0 else None
    fields_to_update[f'state.videoPlayerOptions.intervalsNavigation'] = True if len(ranges_to_play) > 0 else False


def get_project_custom_data(project_id):
    project_info = g.api.project.get_info_by_id(project_id)
    if project_info.custom_data:
        return project_info.custom_data
    else:
        return {}


def get_video_workers_by_id(worker_type, video_id):
    item_info = g.item2stats.get(f'{video_id}')

    if item_info is not None:
        return item_info.get(worker_type, [])


