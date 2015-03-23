#! /usr/bin/env python
# -- encoding:utf - 8 --

import time
import tornado
import refresh

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
        elif track_contr.is_ready(username):
            lib_ratio = main.LIB_RATIO
            emotion_range = zeus.choice(main.EMOTION_RANGE)
            track = track_contr.get_next_playlist(username, lib_ratio,
                                                  emotion_range)
            track = track_contr.get_next_song(username, 'normal')
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
        # username = "Patrickcai"
        radio_type = self.get_argument('radio_type', None)
        track = track_contr.get_next_song(username, radio_type)
        last_contr.update_playing(username, track)
        last_track = self.get_argument("last_track", None)
        if last_track:
            last_contr.scrobble(username, last_track)
        background_url = backgroundM.get_random()
        track_items = {"url": track.url,
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

        if track_contr.is_ready(username):
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
