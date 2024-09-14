from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame

class Window:
    def __init__(self, winSize: tuple[int, int] | str, title = 'Window', backgroundColor: tuple[int, int, int] = (10, 10, 10)) -> None:
        pygame.init()

        if type(winSize) == str:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, vsync = 1)
            self.winSize = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        else:
            self.screen = pygame.display.set_mode(winSize, vsync = 1)
            self.winSize = winSize

        self.width = winSize[0]
        self.height = winSize[1]

        # pygame.SCALED = True     maybe include

        self.title = title

        pygame.display.set_caption(self.title)
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 50)

        self.running = True


    def handleEvents(self):
        '''Handles inputs'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.onKeyDown(event.key)

    def onKeyDown(self, key: pygame.event):
        '''Function to handle keypresses. Override in child classes'''
        pass

    def update(self, dt: float):
        '''Funtion to update the game state. Override in child classes'''
        pass

    def draw(self):
        '''Function to draw to the window. Override in child classes'''
        pass

    def run(self):
        '''Main loop'''
        while self.running:
            self.handleEvents()

            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds (60 fps)

            self.update(dt)

            self.screen.fill((0, 0, 0))  # Clear screen with black

            self.draw()

            pygame.display.flip()  # Update the display

        self.quit()

    def quit(self):
        pygame.quit()