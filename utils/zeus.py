import os
import base64
import random
import re

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


def is_similar(a_txt, b_txt, is_tight=False, is_title=False):
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
    if is_tight and is_title:
        if not set(b_list) & main.TITLE_BANNED and \
                set(a_list) & main.TITLE_BANNED:
            return False
    return True if count >= 1 else False


def is_album_legal(album):
    '''
    Tell whether the album contains the illegal tokens like 'live'
    or itunes session
    '''
    album_upper = album.upper()
    for token in main.ALBUM_BANNED:
        result = re.search(r'%s', album_upper)
        if result:
            return False
    else:
        return True


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
        0: [200, 300],
        100: [300, 400],
        200: [100, 200],
        300: [0, 100],
    }
    return emotion_jump_table[emo_start]


def next_list_emotion(emotion_range):
    '''
    Return the next emotin if user has not switched the track during playlist
    '''
    emo_start = emotion_range[0]
    emotion_jump_table = {
        0: [[100, 200]],
        100: [[0, 100], [200, 300]],
        200: [[100, 200], [300, 400]],
        300: [[200, 300]],
    }
    return choice(emotion_jump_table[emo_start])
