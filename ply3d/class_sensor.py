import numpy as np


class Sensor_value:
    def __init__(self):
        self.single_val = 0
        self.x = 0
        self.y = 0
        self.z = 0

    def update_sensor(self, isRandom, x, y, z, single):
        if isRandom is True:
            self.single_val = np.random.randint(0, 100)

            # 入力値は10bit(0~1023)を想定
            self.x = np.random.randint(0, 1023)
            self.y = np.random.randint(0, 1023)
            self.z = np.random.randint(0, 1023)

        else:
            self.single_val = int(single)

            self.x = x
            self.y = y
            self.z = z

    def get_zero_to_hundred(self):
        return self.single_val

    def get_three_axis(self):
        return [self.x, self.y, self.z]
