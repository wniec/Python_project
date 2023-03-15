class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def precedes(self, other):
        return self.x <= other.x and self.y <= other.y

    def follows(self, other):
        return self.x >= other.x and self.y >= other.y

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def subtract(self, other):
        self.x -= other.x
        self.y -= other.y
