import pickle

import supervisely_lib as sly

import sly_globals as g
import sly_functions as f


def init_fields(state, data):
    data['videosTable'] = []
    state['annotationsCached'] = False

    data['projectInfo'] = {
        'id': g.project_info.id,
        'name': g.project_info.name,
        'reference_image_url': g.project_info.reference_image_url,
        'project_type': g.project_meta.project_type,
        'items_count': g.project_info.items_count,
        'classes_count': len(g.project_meta.obj_classes),
        'tags_count': len(g.project_meta.tag_metas)

    }




def get_used_tags_count_by_annotation(annotation_for_video):
    used_tags = set([])

    tags_on_video = annotation_for_video.get('tags', [])

    for current_tag in tags_on_video:
        if current_tag['name'] in g.technical_tags_names:
            continue

        tag_name = current_tag.get('name', None)
        used_tags.add(tag_name)

    return len(used_tags)


def get_video_duration(video_annotation):
    try:
        return round(video_annotation['framesCount'] * video_annotation['framesToTimecodes'][1])
    except:
        return None


def get_stats_for_video_by_annotation(annotation_for_video):
    tagged_frames = f.get_tagged_frames_count_by_annotation(annotation_for_video)
    untagged_frames = annotation_for_video.get('framesCount') - tagged_frames
    tags_used = get_used_tags_count_by_annotation(annotation_for_video)
    total_frames = annotation_for_video.get('framesCount')

    return {
        'tagged_frames': tagged_frames,
        'untagged_frames': untagged_frames,
        'tags_used': tags_used,
        'elapsed_time': '-',  # fix
        'total_frames': total_frames,
        'video_duration': get_video_duration(video_annotation=annotation_for_video),
        'tagged_frames_percent': int(round(tagged_frames / total_frames, 2) * 100),
        'untagged_frames_percent': int(round(untagged_frames / total_frames, 2) * 100),

    }


def get_videos_table():
    videos_table = []

    datasets_in_project = g.api.dataset.get_list(g.project_id)

    for current_dataset in datasets_in_project:
        videos_list = g.api.video.get_list(current_dataset.id)

        for current_video in videos_list:
            annotation_for_video = g.api.video.annotation.download(current_video.id)
            g.videos2annotations[current_video.id] = annotation_for_video

            video_stats = get_stats_for_video_by_annotation(annotation_for_video)

            table_row = {
                'id': current_video.id,
                'name': current_video.name
            }
            table_row.update(video_stats)

            videos_table.append(table_row)
    return videos_table


@g.my_app.callback("download_videos_annotations")
@sly.timeit
@g.update_fields
# @g.my_app.ignore_errors_and_show_dialog_window()
def download_videos_annotations(api: sly.Api, task_id, context, state, app_logger, fields_to_update):
    fields_to_update['state.buttonsLoading.cacheAnn'] = False
    fields_to_update['state.annotationsCached'] = True

    # videos_table = get_videos_table()

    with open('videos_table.pkl', 'rb') as file:  # HARD DEBUG
        videos_table = pickle.load(file=file)

    with open('videos_to_annotations.pkl', 'rb') as file:
        g.videos2annotations = pickle.load(file=file)

    fields_to_update['data.videosTable'] = videos_table


