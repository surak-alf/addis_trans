import numpy as np

class DemandGenerator:
    def __init__(self, peak1=8, peak2=17):
        self.peak1 = peak1
        self.peak2 = peak2

    def get_arrival_rate(self, time_seconds):
        hour = time_seconds / 3600

        if 7 <= hour <= 9:
            return np.random.poisson(10)
        elif 16 <= hour <= 18:
            return np.random.poisson(12)
        else:
            return np.random.poisson(4)
