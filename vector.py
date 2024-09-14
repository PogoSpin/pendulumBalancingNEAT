from math import sqrt

class Vector2d:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2d') -> 'Vector2d':
        if isinstance(other, Vector2d):
            return Vector2d(self.x + other.x, self.y + other.y)
        return NotImplemented
        
    def __sub__(self, other: 'Vector2d') -> 'Vector2d':
        if isinstance(other, Vector2d):
            return Vector2d(self.x - other.x, self.y - other.y)
        return NotImplemented
    
    def __mul__(self, other: 'Vector2d') -> 'Vector2d':
        if isinstance(other, Vector2d):
            return Vector2d(self.x * other.x, self.y * other.y)
        return NotImplemented
    
    def __truediv__(self, other: 'Vector2d') -> 'Vector2d':
        if isinstance(other, Vector2d):
            return Vector2d(self.x / other.x, self.y / other.y)
        return NotImplemented
    
    def dot(self, other: 'Vector2d') -> float:
        return self.x * other.x + self.y * other.y
    
    def magnitude(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def __repr__(self) -> str:
        return f'({self.x}, {self.y})'