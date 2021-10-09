from .base import base
import mygrations
def execute(options):

    obj = Version(options)
    obj.execute()
class Version(base):
    def execute(self):
        print('mygrations v%s' % mygrations.__version__)
        print('Copyright (c) 2021 Conor Mancone (cmancone@gmail.com)')
        print('MIT License')
