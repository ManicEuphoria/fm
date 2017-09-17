import time

from models import userTrack
from pyechonest import song, config
from pyechonest.util import EchoNestException

config.ECHO_NEST_API_KEY = "K26XNSWEBGDX645MV"


def get_energy():
    all_tracks = userTrack.get_no_energy_tracks()
    all_tracks = [[one_track.artist, one_track.title, one_track.track_uuid]
                  for one_track in all_tracks]
    fin_tracks = []
    print("The tracks number %s" % (len(all_tracks)))
    for index in xrange(len(all_tracks)):
        track = all_tracks[index]
        try:
            results = song.search(artist=track[0], title=track[1])
            result = results[0]
            energy = result.get_audio_summary(True)['energy']
            energy *= 400
            track.append(energy)
            fin_tracks.append(track)
            print("energy %s, index%s" % (energy, index))
            index += 1
        except EchoNestException as e:
            print(e)
            # Add it to the db
            if fin_tracks:
                userTrack.add_energy_tracks(fin_tracks)
                print("add to db")
            print("wait 20 seconds")
            time.sleep(20)
        except Exception as e:
            if e == 'timed out':
                time.sleep(5)
                print("Time out")
                continue
            print(e)
            track.append(None)
            index += 1
            fin_tracks.append(track)


def emo_to_energy():
    '''
    If there are no energy value then use the emotion value
    '''
    userTrack.set_energy_emotion()


if __name__ == '__main__':
    # get_energy()
    emo_to_energy()
