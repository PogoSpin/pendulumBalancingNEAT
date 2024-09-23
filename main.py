from os import environ
from vector import Vector2d
from math import sin, cos, pi

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

from window import Window


class Game(Window):
    class Cart:
        friction = 0.15

        def __init__(self, winSize) -> None:
            self.pos = Vector2d(winSize[0] / 2, winSize[1] / 2)
            self.vel = 0
            self.acceleration = 0

            self.moves = [False, False]

        def update(self, timeCoefficient):
            if (self.moves[0] and self.moves[1]) or (not self.moves[0] and not self.moves[1]):
                self.acceleration = 0
            elif self.moves[0]:
                self.acceleration = -2
            else:
                self.acceleration = 2

            self.acceleration -= self.vel*Game.Cart.friction
            
            self.vel += self.acceleration * timeCoefficient

            self.pos.x += self.vel * timeCoefficient

    class Pendulum:
        drag = 2.5

        def __init__(self, winSize: tuple[int, int], mass: int, length: float) -> None:
            self.pos = Vector2d(winSize[0] / 2, winSize[1] / 2)
            self.mass = 0.1
            self.length = length

            self.angle = pi*1.01
            self.angularVelocity = 0
            self.angularAcceleration = 0
    
        def update(self, cartAcceleration, timeCoefficient):
            g = 3  # gravity

            # computes angular accel from grav and cart movement
            #                                     gravity part                                      cart part
            self.angularAcceleration = (-g * sin(self.angle) / self.length)  +  (cos(self.angle) * cartAcceleration / self.length)

            self.angularAcceleration -= self.angularVelocity*Game.Pendulum.drag/self.length    # drag as a negative acceleration instead of velocity mult

            # standard
            self.angularVelocity += self.angularAcceleration * timeCoefficient
            self.angle += self.angularVelocity * timeCoefficient


    def __init__(self, winSize: tuple[int, int] | str = (1000, 700), title = 'Window', backgroundColor: tuple[int, int, int] = (20, 20, 20)) -> None:
        super().__init__(winSize, title, backgroundColor)

        self.fps = 60
        self.fpsReference = 60  # IE: targeted fps

        self.pos = [0, 0]

        self.cart = Game.Cart(winSize)
        self.pendulum = Game.Pendulum(winSize, 10, 100)

    def onKeyDown(self, key: pygame.event):
        if key == pygame.K_ESCAPE:
            self.running = False

        if key == pygame.K_LEFT:
            self.cart.moves[0] = True

        elif key == pygame.K_RIGHT:
            self.cart.moves[1] = True

    def onKeyUp(self, key: pygame.event):
        if key == pygame.K_LEFT:
            self.cart.moves[0] = False

        elif key == pygame.K_RIGHT:
            self.cart.moves[1] = False


    def update(self, dt: float):
        timeCoefficient = dt * self.fpsReference  # like dt but weighted/normalized with fps reference so it's 1 when running at targeted fps
        self.cart.update(timeCoefficient)
        self.pendulum.update(self.cart.acceleration, timeCoefficient)

    def draw(self):
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.winSize[1] / 2), (self.winSize[0], self.winSize[1] / 2))
        pygame.draw.rect(self.screen, (200, 0, 0), pygame.rect.Rect(self.cart.pos.x-25, self.cart.pos.y-12.5, 50, 25))
        pygame.draw.line(self.screen, (255, 255, 255), (self.cart.pos.x, self.cart.pos.y), (self.cart.pos.x + cos(self.pendulum.angle + pi/2)*self.pendulum.length, self.cart.pos.y + sin(self.pendulum.angle + pi/2)*self.pendulum.length), 3)
    
a = Game()
a.run()

