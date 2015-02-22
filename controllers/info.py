import requests
import md5

from utils.geventWorker import Worker
from constants.main import SEARCH_URL, API_HEADERS, API_COOKIE
from constants.main import get_dfsid_url


def encrypted_id(id):
    byte1 = bytearray('3go8&$8*3*3h0k(2)2')
    byte2 = bytearray(id)
    byte1_len = len(byte1)
    for i in xrange(len(byte2)):
        byte2[i] = byte2[i] ^ byte1[i % byte1_len]
    m = md5.new()
    m.update(byte2)
    result = m.digest().encode('base64')[:-1]
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result


def download_url(track, progress):
    name = track.artist + ' ' + track.title
    params = {
        's': name,
        'type': 1,
        'offset': 0,
        'sub': 'false',
        'limit': 10
    }
    r = requests.post(SEARCH_URL, headers=API_HEADERS,
                      params=params, cookies=API_COOKIE)

    try:
        song_id = r.json()['result']['songs'][0]['id']
    except (TypeError, KeyError):
        track.mp3_url = None
        return

    dfsid_url = get_dfsid_url(song_id)
    r = requests.get(dfsid_url)
    try:
        dfsid = r.json()['songs'][0]['hMusic']['dfsId']
        print(r.json()['songs'][0]['mMusic']['dfsId'])
    except (TypeError, KeyError):
        track.mp3_url = None
        return

    en_id = encrypted_id(str(dfsid))
    track.mp3_url = en_id + '/' + str(dfsid)
    print(track.title)
    print(track.mp3_url)
    print(progress)


def fetch_tracks_urls(chosen_tracks):
    workers_number = 20
    url_gevent = Worker(workers_number)
    boss = url_gevent.generate_boss(chosen_tracks)
    workers = url_gevent.generate_workers(download_url)
    url_gevent.joinall(boss, workers)
