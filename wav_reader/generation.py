"""Module responsible for generating wave forms and writing to wav files.

"""

import math


class WaveForm:

    def __init__(self, frequency):
        self.frequency = frequency

    def y_from_x(self, x):
        assert False, "Not implemented"

class SquareWaveForm(WaveForm):
    
    def __init__(self, frequency):
        WaveForm.__init__(self, frequency)
    
    def y_from_x(self, x):
        y_sin = math.sin(x)
        if y_sin < 0:
            return -1
        else:
            return 1
