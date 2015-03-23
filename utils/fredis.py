import redis


r_cli = redis.StrictRedis(host="localhost", port=6379, db=0)


def subscribe(sub_name):
    '''
    Return the subscribe object
    '''
    ps = r_cli.pubsub()
    ps.subscribe(sub_name)
    return ps
