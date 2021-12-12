import supervisely_lib as sly

import sly_globals as g
import sly_functions as f
import sly_constants as c


def init_fields(state, data):
    state['selectedVideoId'] = None
    state['selectedVideo'] = {
        'generalStats': None,
        'tagsOnVideo': None
    }

    data['videoInfo'] = {}


def get_video_general_stats(video_id):
    video_annotation = g.videos2annotations[video_id]

    return {
        'Video ID': video_annotation.get('videoId'),
        'Video Name': video_annotation.get('videoName'),
        'Frames Count': video_annotation.get('Total Frames'),
        'Tagged Frames': f.get_tagged_frames_count_by_annotation(video_annotation),
        'Tags on Video': f.get_tags_on_video_count_by_annotation(video_annotation)
    }


def safe_dict_value_append(source_dict, key, new_value):
    list_of_values = source_dict.get(key, [])
    list_of_values.append(new_value)
    source_dict[key] = list_of_values


def format_tags_on_frames_to_stats(tags2stats, tags_on_frames):
    for current_tag in tags_on_frames:
        name = current_tag.get('name')
        value = current_tag.get('value')
        frame_range = current_tag.get('frameRange')

        if name and value is not None and frame_range:
            tags_values = tags2stats.get(name, {})

            tag_value_stats = tags_values.get(value, {})

            tag_color = g.project_meta.get_tag_meta(current_tag['name']).to_json()['color']

            safe_dict_value_append(tag_value_stats, 'frameRanges', frame_range)  # updating frame range
            safe_dict_value_append(tag_value_stats, 'colors', tag_color)  # updating frame range

            tags_values[value] = tag_value_stats
            tags2stats[name] = tags_values


def frame_ranges_to_count(frame_ranges):
    unique_frames = set()
    for frame_range in frame_ranges:
        for curr_frame in range(frame_range[0], frame_range[1] + 1, 1):
            unique_frames.add(curr_frame)

    return len(unique_frames)


def add_additional_stats(tags2stats, tags_on_frames):
    video_info = g.api.video.get_info_by_id(g.video_id)

    for tag_key in tags2stats.keys():
        for tag_value in tags2stats[tag_key].keys():
            current_tag = tags2stats[tag_key][tag_value]

            tagged_frames_count = frame_ranges_to_count(current_tag['frameRanges'])
            untagged_frames_count = video_info.frames_count - tagged_frames_count

            ranges_divs = [current_range[1] - current_range[0] for current_range in current_tag['frameRanges']]
            max_range = current_tag['frameRanges'][ranges_divs.index(max(ranges_divs))]
            min_range = current_tag['frameRanges'][ranges_divs.index(min(ranges_divs))]

            additional_stats = {
                'tagged_frames': tagged_frames_count,
                'untagged_frames': untagged_frames_count,
                'tagged_frames_percent': round(tagged_frames_count / video_info.frames_count, 2) * 100,
                'max_range': max_range,
                'min_range': min_range
            }
            current_tag.update(additional_stats)
            tags2stats[tag_key][tag_value] = current_tag


def get_tags_stats(tags_on_frames):
    tags2stats = {}

    format_tags_on_frames_to_stats(tags2stats, tags_on_frames)
    add_additional_stats(tags2stats, tags_on_frames)

    return tags2stats


def init_solo_button():
    solo_button_params = {
        'stage': 0,
    }
    solo_button_params.update(c.solo_button_stages[0])
    return solo_button_params


def tag_stats_to_table(tags2stats):
    table = []
    for tag_key in tags2stats.keys():
        for tag_value in tags2stats[tag_key].keys():

            row_init = {
                'tag': tag_key,
                'value': tag_value,
                'solo_button': init_solo_button()
            }

            row_init.update(tags2stats[tag_key][tag_value])

            table.append(row_init)
    return table


def get_tag_intersection_matrix(tags_stats_in_table_form):
    tags2intersections = {}

    for row_original in tags_stats_in_table_form:
        intersection_with_current_original = {}

        for row_intersected in tags_stats_in_table_form:
            original_frame_ranges = row_original['frameRanges']
            intersected_frame_ranges = row_intersected['frameRanges']

            intersection_with_current_original[f'{row_intersected["tag"]}: {row_intersected.get("value")}'] = \
                f.get_ranges_intersections_count(original_frame_ranges, intersected_frame_ranges)

        tags2intersections[f'{row_original["tag"]}: {row_original.get("value")}'] = intersection_with_current_original

    return tags2intersections


def get_max_value(tags2intersections, diagonal):
    max_value = 0

    for tag, intersections in tags2intersections.items():
        if diagonal:
            if intersections[tag] > max_value:
                max_value = intersections[tag]

        else:
            for curr_value in intersections.values():
                if curr_value > max_value:
                    max_value = curr_value

    return max_value


def get_matrix_data(tags2intersections):
    data = []
    totals = []

    for tag, intersections in tags2intersections.items():

        matrix_row = []
        value_on_row = 0
        for curr_value in intersections.values():
            matrix_row.append({'value': curr_value})
            value_on_row += curr_value

        matrix_row.append({'value': value_on_row})
        totals.append({'value': value_on_row})

        data.append(matrix_row)

    data.append(totals)
    return data


def convert_to_sly_matrix(tags2intersections):
    return {
        "diagonalMax": get_max_value(tags2intersections, diagonal=True),
        "maxValue": get_max_value(tags2intersections, diagonal=False),  # for recolor
        "classes": [class_name for class_name in list(tags2intersections.values())[0]],
        "data": get_matrix_data(tags2intersections),
    }


def fill_combinations_matrix(tags_stats_in_table_form, fields_to_update):
    tags2intersections = get_tag_intersection_matrix(tags_stats_in_table_form)
    if len(tags2intersections) > 0:
        fields_to_update['data.matrixData'] = convert_to_sly_matrix(tags2intersections)


def fill_tags_table(fields_to_update):
    tags_stats_in_table_form = tag_stats_to_table(g.tags2stats)
    fields_to_update['data.selectedTagsStats'] = tags_stats_in_table_form

    return tags_stats_in_table_form


def fill_pie_chart(tags_stats_in_table_form, fields_to_update):
    labels_with_values = {}

    for row in tags_stats_in_table_form:
        label = row.get("tag")
        value = row.get("value")
        frame_ranges = row.get('frameRanges')

        if label is not None and value is not None and frame_ranges is not None:
            tags_count_for_this_value = len(f.get_frames_list_from_ranges(frame_ranges))

            labels_with_values[label] = labels_with_values.get(label, 0) + tags_count_for_this_value

    chart_data = [{
        'labels': list(labels_with_values.keys()),
        'values': list(labels_with_values.values()),
        "type": "pie"
    }]

    fields_to_update['data.tagsOnPieChart.data'] = chart_data


@g.my_app.callback("select_video")
@sly.timeit
@g.update_fields
# @g.my_app.ignore_errors_and_show_dialog_window()
def select_video(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    g.video_id = state['selectedVideoId']

    fields_to_update['data.videoInfo'] = api.video.get_info_by_id(g.video_id)

    fields_to_update['state.selectedVideo.generalStats'] = get_video_general_stats(g.video_id)  # video tags part
    fields_to_update['state.selectedVideo.tagsOnVideo'] = f.get_tags_list_by_type('video', g.video_id)
    fields_to_update['state.selectedVideo.annotators'] = f.get_video_workers_by_id('annotators', g.video_id)
    fields_to_update['state.selectedVideo.reviewers'] = f.get_video_workers_by_id('reviewers', g.video_id)

    tags_on_frames = f.get_tags_list_by_type('frame', g.video_id)  # frames tags part
    g.tags2stats = get_tags_stats(tags_on_frames)

    f.merge_tag_value_frame_ranges(g.tags2stats)

    # fill additional widgets
    tags_stats_in_table_form = fill_tags_table(fields_to_update)  # table
    fill_pie_chart(tags_stats_in_table_form, fields_to_update)  # pie-chart
    fill_combinations_matrix(tags_stats_in_table_form, fields_to_update)  # matrix

    f.update_tags_by_frame(state['currentFrame'])
