import datetime
from string import Formatter

import sly_globals as g

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
        # if current_tag.get('name') in g.technical_tags_names: # DEBUG
        #     continue

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


def update_tags_by_frame(frame_number):
    tags_on_frame = []

    for tag_key in g.tags2stats.keys():
        for tag_value in g.tags2stats[tag_key].keys():
            current_tag = g.tags2stats[tag_key][tag_value]
            frames_ranges = current_tag['frameRanges']

            if tag_in_range(frames_ranges, frame_number):
                init_row = {
                    'tag': tag_key,
                    'value': tag_value,
                    'color': current_tag['colors'][0],
                    'prev': tag_in_range(frames_ranges, frame_number - 1),
                    'next': tag_in_range(frames_ranges, frame_number + 1)
                }
                tags_on_frame.append(init_row)

    g.api.app.set_field(g.task_id, 'state.tagsOnFrame', tags_on_frame)


def get_ranges_intersections_count(ranges1, ranges2):
    intersections_count = 0

    for current_range1 in ranges1:
        for current_range2 in ranges2:
            if current_range2[0] <= current_range1[0] <= current_range2[1]:
                end_of_inter_segment = min(current_range2[1], current_range1[1])
                intersections_count += end_of_inter_segment - current_range1[0] + 1

            elif current_range2[0] <= current_range1[1] <= current_range2[1]:
                start_of_inter_segment = max(current_range2[0], current_range1[0])
                intersections_count += current_range1[1] - start_of_inter_segment + 1

    return intersections_count


def get_ranges_intersections_frame(ranges1, ranges2):
    for current_range1 in ranges1:
        for current_range2 in ranges2:
            if current_range2[0] <= current_range1[0] <= current_range2[1]:
                return current_range1[0]
            elif current_range2[0] <= current_range1[1] <= current_range2[1]:
                return max(current_range2[0], current_range1[0])

    return None