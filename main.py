from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

from window import Window


class Game(Window):
    def __init__(self, winSize: tuple[int, int] | str = (1000, 700), title = 'Window', backgroundColor: tuple[int, int, int] = (20, 20, 20)) -> None:
        super().__init__(winSize, title, backgroundColor)

        self.fps = 60
        self.fpsReference = 60

        self.pos = [0, 0]

    def onKeyDown(self, key: pygame.event):
        if key == pygame.K_ESCAPE:
            self.running = False

    def update(self, dt: float):
        self.pos[0] += 2 * dt * self.fpsReference
        self.pos[1] += 2 * dt * self.fpsReference

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.rect.Rect(self.pos[0], self.pos[1], 50, 50))

    
a = Game()
a.run()

