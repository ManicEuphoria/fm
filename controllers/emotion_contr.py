import collections
import cPickle

from decimal import Decimal
from constants import main
from controllers import last_contr

x_axis_percentage = cPickle.load(open("constants/per_x", "r"))
y_axis_percentage = cPickle.load(open("constants/per_y", "r"))
x_axis_type = cPickle.load(open("constants/type_x", "r"))
y_axis_type = cPickle.load(open("constants/type_y", "r"))


TrackEmotion = collections.namedtuple("TrackEmotion", [
    'track_uuid', 'artist', "title", "emotion"])


def calculate_tags(user_track, progress):
    '''
    Download music and calculate the tags emotion
    '''
    user_tags = last_contr.get_top_tags(user_track)
    track_tags_list = _transform_to_tracktag(user_tags)
    emotion_dict = calculate_emotion(track_tags_list, axis="x")
    track_emotion = TrackEmotion(user_track.track_uuid, user_track.artist,
                                 user_track.title, emotion_dict)
    return track_emotion


def _transform_to_tracktag(user_tags):
    '''
    Transform from list of Topitem(see f8533c37)
    to a list fo tag-value tuple
    such as [("rock", 1), ("pop", 2)]
    '''
    tracktag_list = []
    for user_tag in user_tags:
        if user_tag.item.name in main.VALID_TAGS:
            if int(user_tag.weight) < main.MIDDLE_VALUE:
                value = 1
            elif int(user_tag.weight) >= main.MIDDLE_VALUE:
                value = 2
            else:
                break
            track_tag = (user_tag.item.name, value)
            tracktag_list.append(track_tag)
    return tracktag_list


def calculate_emotion(track_tags_list, axis):
    '''
    User bayers to calculate emotion
    track_tags_list a list fo tag-value tuple
    such as [("rock", 1), ("pop", 2)]
    middel value is a dict, value is measured in 100
    {"high": 83, "low":12, "up": 4, "down":4}
    return value is
    ('high', 83) or ("no", -1)
    '''
    if axis == "x":
        axis_type = x_axis_type
        axis_percentage = x_axis_percentage
    elif axis == "y":
        axis_type = y_axis_type
        axis_percentage = y_axis_percentage

    track_tags = dict(zip(main.VALID_TAGS,
                          [0 for i in xrange(len(main.VALID_TAGS))]))
    for raw_track_tag in track_tags_list:
        track_tags[raw_track_tag[0]] = raw_track_tag[1]

    emotion_result = {}
    for emotion, tags_percentage in axis_type.iteritems():
        one_emotion_percentage = []
        for tag, index in track_tags.iteritems():
            perce = tags_percentage[tag][index]
            if perce == 0:
                one_emotion_percentage.append(main.MIN_DUMMY)
            else:
                one_emotion_percentage.append(tags_percentage[tag][index])
        one_emotion_percentage.append(axis_percentage[emotion])
        result = reduce(lambda x, y: x * y, one_emotion_percentage)
        emotion_result[emotion] = result
        # if There is no tag
    emotion_result = _to_percentage(emotion_result)
    emotion = max(emotion_result, key=emotion_result.get)
    emotion_result = (emotion, emotion_result[emotion])
    if not track_tags_list:
        emotion_result = ('no', -1)
    return emotion_result


def _to_percentage(emotion_result):
    total = sum(emotion_result.values())
    results = {}
    for emotion, value in emotion_result.iteritems():
        results[emotion] = int((Decimal(str(value)) / Decimal(str(total)))
                               * 100)
    return results
