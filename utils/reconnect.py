import requests
import socket

from utils import fredis


class StatusException(Exception):
    def __init__(self, state):
        self.state = state

    def __str__(self):
        return repr(self.state)


good_ips_name = 'good_ips:list'


def get_random_ip():
    '''
    Pick one ip by random
    '''
    proxies_ip = fredis.r_cli.srandmember(good_ips_name)
    return proxies_ip


def delete_ip(proxies_ip):
    '''
    Delete the specific proxies ip
    '''
    fredis.r_cli.srem(good_ips_name, proxies_ip)


def post(*args, **kwargs):
    proxies_ip = get_random_ip()
    proxies = {'http': 'http://%s' % (proxies_ip)}
    try:
        r = requests.post(proxies=proxies, timeout=6, *args, **kwargs)
        if r.status_code == 200:
            status = r.json()['code']
            if status == 406:
                raise StatusException("Limit")
        else:
            raise StatusException(r.status_code)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout,
            socket.timeout, StatusException, socket.error) as e:
        print('bad ip')
        r = post(*args, **kwargs)
        print(str(e))
    return r
