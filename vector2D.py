import math


class Vector2D(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            # Vector multiplication
            return self.x * other.x + self.y * other.y
        else:
            # Scalar multiplication
            return Vector2D(self.x * other, self.y * other)

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "{0} {1}".format(self.x, self.y)

    def get_length(self):
        return (self.x ** 2 + self.y ** 2) ** (1/2)

    def get_distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** (1/2)

    def get_angle(self, other, radians=False):
        """
        Will return the angle between this vector and the other vector.
        """
        if self.get_length() == 0 or other.get_length() == 0:
            return 0
        if not radians:
            return (360 / (2 * math.pi)) * (math.atan2(other.y, other.x) - math.atan2(self.y, self.x))
        else:
            return math.atan2(other.y, other.x) - math.atan2(self.y, self.x)

    def normalize(self):
        if self.get_length() == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / self.get_length(), self.y / self.get_length())

    def projection(self, other):
        if self.get_length() == 0 or other.get_length() == 0:
            return Vector2D(0, 0)
        return ((other * self) / other.length ** 2) * other

    def reflection(self, other):
        return 2 * self.projection(other) - self

