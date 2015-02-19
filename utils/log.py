from utils.baselog import Xslog


visitlog = Xslog('visitor log', 'visitor.log')


COLORS = {
    'ENDC': 0,
    'r': 31,
    'g': 32,
    'b': 36,
    'y': 33,
    'black': 30,
}


def color(mes, color='b'):
    inte = "\x1B[%d;%dm" % (1, COLORS[color])
    return "%s %s\x1B[0m" % (inte, mes)
