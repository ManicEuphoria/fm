#! /usr/bin/env python
# -- encoding:utf - 8 --

import time
import tornado
import refresh
import json

from tornado import gen
from views.base import BaseHandler
from controllers import track_contr
from controllers import last_contr, user_contr
from models import userM, backgroundM, userTrack
from constants import redname, main
from utils import fredis, zeus


class MainHandler(BaseHandler):
    def get(self):
        username = self.get_secure_cookie("username")
        # Three kinds of situations
        # 1.user is first time -> welcome 2. user has registered, but
        # the track is not ready -> /loading 3.user can listen to radio
        if not username:
            self.render('welcome.html')
        elif userTrack.is_pre_tracks_exist(username) or\
                userM.is_all_finished(username):
            if userTrack.is_pre_tracks_exist(username):
                radio_type = "pre"
                self.set_secure_cookie('radio_type', radio_type)
                track = track_contr.get_next_song(username, "pre")
            else:
                radio_type = "normal"
                lib_ratio = main.LIB_RATIO
                emotion_range = zeus.choice(main.EMOTION_AREA)
                track = track_contr.get_next_song(
                    username, 'normal', lib_ratio=lib_ratio,
                    track_number=0, emotion_range=emotion_range)
                self.set_secure_cookie('last_tag', str(track.last_tag))

                self.set_secure_cookie('emotion_range',
                                       json.dumps(emotion_range))
                self.set_secure_cookie('track_number', str(0))
                self.set_secure_cookie('normal', str(radio_type))
                self.set_secure_cookie("lib_ratio", str(lib_ratio))
                self.set_secure_cookie('last_type', str(track.type))
                self.set_secure_cookie('emotion_range',
                                       json.dumps(emotion_range))
                self.set_secure_cookie("last_emotion_value",
                                       str(track.emotion_value))
                self.set_secure_cookie("tag_value", str(track.last_tag_value))

            last_contr.update_playing(username, track)
            self.render("radio.html", track=track)
        else:
            self.render('welcome.html')


class LoadHandler(BaseHandler):
    '''
    When the user initialize their radio,it should record user's
    information
    '''
    def get(self):
        access_token = self.get_argument("token")
        session_key = last_contr.token_to_session(access_token)
        username = last_contr.get_username(session_key)
        if userM.do_exist_user(username):
            userM.update_session(username, session_key)
            if track_contr.is_ready(username):
                self.set_secure_cookie("username", username, expires_days=300)
                # If the user has registered before, and track is ready for him
                self.redirect('/')
        else:
            user_contr.add_user(username, session_key)
            user_contr.add_waiting_user(username)
            self.set_secure_cookie("username", username, expires_days=300)
        self.render('loading.html')


class TestHandler(BaseHandler):
    def get(self):
        username = self.get_secure_cookie("username")
        tracks = track_contr.get_next_song(username, number=2)
        self.render('test.html', track=tracks)


class NextHandler(BaseHandler):
    def get(self):

        username = self.get_secure_cookie("username")
        radio_type = self.get_secure_cookie('radio_type')
        last_track = self.get_argument("last_track", None)
        lib_ratio = self.get_secure_cookie("lib_ratio")
        if not lib_ratio:
            lib_ratio = main.LIB_RATIO
        else:
            lib_ratio = int(lib_ratio)
        emotion_range = self.get_secure_cookie("emotion_range")
        if not emotion_range:
            emotion_range = [100, 125]
        else:
            emotion_range = json.loads(emotion_range)
        track_number = self.get_secure_cookie("track_number")
        if not track_number:
            track_number = 0
        else:
            track_number = int(track_number)

        last_type = self.get_secure_cookie("last_type")
        last_tag = self.get_secure_cookie('last_tag')
        last_emotion_value = self.get_secure_cookie("last_emotion_value")
        if last_emotion_value:
            last_emotion_value = int(last_emotion_value)
        tag_value = self.get_secure_cookie('tag_value')
        if tag_value:
            tag_value = int(tag_value)
        if radio_type == "pre" and not userM.is_all_finished(username):
            track = track_contr.get_next_song(username, "pre")
        else:
            reverse_type = None
            lib_ratio, emotion_range, track_number, reverse_type, last_tag, tag_value\
                = track_contr.next_status(
                    lib_ratio, emotion_range, track_number, last_track,
                    last_type, last_tag, tag_value)
            track = track_contr.get_next_song(username, "normal",
                                              lib_ratio=lib_ratio,
                                              emotion_range=emotion_range,
                                              track_number=track_number,
                                              reverse_type=reverse_type,
                                              last_tag=last_tag,
                                              tag_value=tag_value,
                                              last_emotion_value=last_emotion_value)
            print('track_number is %s' % (track_number))
            print('emotio range %s' % (emotion_range))
            print("lib_ratio %s" % (lib_ratio))
            self.set_secure_cookie("last_tag", str(track.last_tag))
            self.set_secure_cookie("tag_value", str(track.last_tag_value))
            self.set_secure_cookie("last_emotion_value",
                                   str(track.emotion_value))
            self.set_secure_cookie('radio_type', 'normal')
            self.set_secure_cookie('lib_ratio', str(lib_ratio))
            self.set_secure_cookie('track_number', str(track_number))
            self.set_secure_cookie('emotion_range', json.dumps(emotion_range))
            self.set_secure_cookie('last_type', str(track.type))
        last_contr.update_playing(username, track)
        if last_track:
            last_contr.scrobble(username, last_track)
        background_url = backgroundM.get_random()
        track_items = {"mp3_url": track.mp3_url,
                       "title": "'" + track.title + "'",
                       'artist': track.artist,
                       'album_url': track.album_url,
                       'song_id': track.song_id,
                       'is_star': track.is_star,
                       'duration': track.duration,
                       'background_url': background_url}
        self.write(track_items)


class LoveHandler(BaseHandler):
    '''
    User love a track, then record it in the last.fm
    '''
    def get(self):
        username = self.get_secure_cookie("username")
        # username = "Patrickcai"
        loved_track = self.get_argument("track", None)
        if not loved_track:
            self.write({'status': "fail"})
        last_contr.loved_track(username, loved_track)
        self.write({'status': "OK"})


class UnloveHandler(BaseHandler):
    '''
    User unlove the track, then record it to the last.fm
    '''
    def get(self):
        username = self.get_secure_cookie("username")
        # username = "Patrickcai"
        unloved_track = self.get_argument("track", None)
        if not unloved_track:
            self.write({'status': "fail"})
        last_contr.unloved_track(username, unloved_track)
        self.write({'status': "OK"})


class StatusHandler(BaseHandler):
    '''
    When the user began to wait the begining of the radio, it should
    know whether it is ready
    '''
    def get(self):
        username = self.get_secure_cookie("username")
        if not username:
            self.write({'status': "ok"})

        if userTrack.is_pre_tracks_exist(username) or\
                userM.is_all_finished(username):
            self.write({'status': "ok"})
        else:
            self.write({'status': 'fail'})


class CheckHandler(BaseHandler):
    '''
    Check user's remaing songs and refresh their track
    '''
    def get(self):
        print('start check')
        username = self.get_secure_cookie('username')
        if len(userTrack.choose_rec_tracks(username)) == 0:
            self.write({'status': "Fail"})
        print('end check')
        refresh.check_and_refresh(username)
        self.write({'status': "OK"})


class EmotionHandler(BaseHandler):
    '''
    User choose emotion or check its status
    '''
    def get(self):
        username = self.get_secure_cookie("username")
        request_type = self.get_argument('request', None)
        emotion = self.get_argument("emotion_type", None)
        if request_type == "choose" and emotion:
            message = username + "||" + emotion
            fredis.r_cli.publish(redname.EMOTION_REFRESH, message)
