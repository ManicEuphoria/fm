class Rate(object):
    def __init__(self, track_number):
        self.track_number = track_number
        self.start_value = 60

    def add_rate(self, num):
        '''
        Return the value in int
        '''
        value = int(float(num) / float(self.track_number) *
                    (100 - self.start_value))
        rate_value = self.start_value + value
        return rate_value


class RateConvert(object):
    '''
    For example in the track list which is already ordered by weight
    from small to big.There are 100 tracks in the list
    each track should be rated between the value from 3 to 6
    The formula is :
        rate_value = start_value+(end_value-start_value)*(position/length)
    '''
    def __init__(self, tracks_list, start_value, end_value):
        self.tracks_list = tracks_list
        self.start_value = start_value
        self.end_value = end_value
        self.length = len(tracks_list)

    def rate(self):
        for pos, track in enumerate(self.tracks_list):
            rate_value = self.start_value
            rate_value += int((self.end_value - self.start_value) *
                              (float(pos) / float(self.length)))
            track.rate = rate_value
        return self.tracks_list
