import requests
import md5

from utils.geventWorker import Worker
from constants.main import SEARCH_URL, API_HEADERS, API_COOKIE
from constants.main import get_dfsid_url
from utils.zeus import is_similar


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
    '''
    Download mp3 url if not in the database
    '''
    if track.mp3_url:
        return

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
        # @todo(Improve if two tracks is
        # Until We Bleed (feat. Lykke Li) (PatrickReza Dubstep Remix) )
        # Until We Bleed (feat. Lykke Li)
        # They should choose the version with no dubstep remix
        songs = r.json()['result']['songs']
        for song in songs:
            title = song['name']
            artist = song['artists'][0]['name']
            is_artist_similar = is_similar(artist, track.artist)
            is_title_similar = is_similar(title, track.title)
            if is_title_similar and is_artist_similar:
                song_id = song['id']
                track.song_id = song_id
                break
        else:
            track.mp3_url = None
            return
    except (TypeError, KeyError) as e:
        print(e)
        track.mp3_url = None
        return

    dfsid_url = get_dfsid_url(song_id)
    r = requests.get(dfsid_url)
    try:
        dfsid = r.json()['songs'][0]['hMusic']['dfsId']
        album_url = r.json()['songs'][0]['album']['blurPicUrl']
        album_url += '?param=160y160'
        album_id = r.json()['songs'][0]['album']['id']
        artist_id = r.json()["songs"][0]['artists'][0]['id']
        duration = r.json()['songs'][0]['hMusic']['playTime'] / 1000
    except (TypeError, KeyError) as e:
        print(e)
        track.mp3_url = None
        return
    en_id = encrypted_id(str(dfsid))
    track.mp3_url = en_id + '/' + str(dfsid)
    track.album_url = album_url
    track.album_id = album_id
    track.artist_id = artist_id
    track.duration = duration


def fetch_tracks_urls(chosen_tracks):
    workers_number = 100
    url_gevent = Worker(workers_number)
    boss = url_gevent.generate_boss(chosen_tracks)
    workers = url_gevent.generate_workers(download_url)
    url_gevent.joinall(boss, workers)
