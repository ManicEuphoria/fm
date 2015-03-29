import os
import base64
import random

from constants import main
from constants.main import BASE_DIR


def read_constants_file(filename):
    '''
    Read file from constants like port.secret,
    Pay attention the type value of return is string
    '''
    file_path = os.path.join(BASE_DIR, 'constants/%s' % (filename))
    with open(file_path) as txt:
        var = txt.read()
    return var


def divide_level(num, all_number):
    '''
    According to the position ,divide them into different levels
    '''
    num_in_hundred = int(float(num) / float(all_number) * 100)
    level = num_in_hundred / 25 + 1
    return level


def is_similar(a_txt, b_txt):
    '''
    Detect the similarity between two text
    For purpose of not mistake for two same track
    @todo("Fix when Chinese character for instance World's End Girlfriend")
    @todo("Add the banned word for instance remix")
    '''
    a_txt = a_txt.upper()
    b_txt = b_txt.upper()
    a_list = a_txt.split()
    b_list = b_txt.split()
    count = 0
    for a_word in a_list:
        if a_word in b_list:
            count += 1
    return True if count >= 1 else False


def choice(items_list):
    '''
    Choose one item randomly from the items
    '''
    random.shuffle(items_list)
    return random.choice(items_list)


def next_jump_emotion(emotion_range):
    '''
    return the next emotion if the song is switched
    '''
    emo_start = emotion_range[0]
    emotion_jump_table = {
        375: [5, 7],
        300: [5, 6],
        275: [5, 7],
        200: [7, 8],
        125: [2, 1],
        100: [4, 2],
        25: [3, 4],
        0: [2, 4]
    }
    random_index = choice(range(2))
    emotion_index = emotion_jump_table[emo_start][random_index]
    return main.EMOTION_SEQUENCE[emotion_index]


def next_list_emotion(emotion_range):
    '''
    Return the next emotin if user has not switched the track during playlist
    '''
    emo_start = emotion_range[0]
    emotion_jump_table = {
        0: [5, 7],
        25: [5, 8],
        100: [5, 7],
        125: [6, 7],
        200: [2, 3],
        275: [2, 4],
        300: [1, 2],
        375: [2, 4],
    }
    random_index = choice(range(2))
    emotion_index = emotion_jump_table[emo_start][random_index]
    return main.EMOTION_SEQUENCE[emotion_index]
