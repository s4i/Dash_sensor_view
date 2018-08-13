import numpy as np


class Sensor_value:
    def __init__(self):
        self.pyroelectric = 0  # pyroelectric:焦電
        self.x = 0
        self.y = 0
        self.z = 0

    def update_sensor(self, isRandom, pyro, x, y, z):
        if isRandom is True:
            # 焦電センサ(入力値は0~100を想定)
            self.pyroelectric = np.random.randint(0, 100)

            # 三軸加速度センサ(入力値は10bit(0~1023)を想定)
            self.x = np.random.randint(0, 1023)
            self.y = np.random.randint(0, 1023)
            self.z = np.random.randint(0, 1023)

        else:
            self.pyroelectric = int(pyro)

            self.x = x
            self.y = y
            self.z = z

    def get_zero_to_hundred(self):
        return self.pyroelectric

    def get_three_axis(self):
        return [self.x, self.y, self.z]
