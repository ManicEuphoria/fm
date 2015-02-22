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
