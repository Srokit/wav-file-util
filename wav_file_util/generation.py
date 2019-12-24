"""Module that contains wave form classes.

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
            return 0
        else:
            return 1

class SineWaveForm(WaveForm):

    def __init__(self, frequency):
        WaveForm.__init__(self, frequency)

    def y_from_x(self, x):
        y = math.sin(x)
        # shift up to range [0,1]
        return y / 2 + 1/2

class SawtoothWaveForm(WaveForm):

    def __init__(self, frequency):
        WaveForm.__init__(self, frequency)

    def y_from_x(self, x):
        return x - int(x)


wave_forms_by_name = {
    'square': SquareWaveForm,
    'sine': SineWaveForm,
    'sawtooth': SawtoothWaveForm
}
