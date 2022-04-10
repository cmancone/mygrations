from .base import base
import mygrations
def execute(options, print_results=True):

    obj = Version(options)
    return obj.execute(print_results=print_results)
class Version(base):
    def execute(self, print_results=True):
        version_info = [
            f'mygrations v{mygrations.__version__}',
            'Copyright (c) 2022 Conor Mancone (cmancone@gmail.com)',
            'MIT License',
        ]
        if print_results:
            "\n".join(version_info)
        return (print_results, True)
