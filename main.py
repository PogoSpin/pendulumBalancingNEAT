from time import sleep
import neat
from os import environ, path
from vector import Vector2d
from math import sin, cos, pi
from random import random

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
            self.winSize = winSize

            self.inputs = [False, False]

        def update(self, timeCoefficient):
            if (self.inputs[0] and self.inputs[1]) or (not self.inputs[0] and not self.inputs[1]):
                self.acceleration = 0
            elif self.inputs[0]:
                self.acceleration = -2
            else:
                self.acceleration = 2

            self.acceleration -= self.vel*Game.Cart.friction
            
            self.vel += self.acceleration * timeCoefficient

            self.pos.x += self.vel * timeCoefficient
            if self.pos.x < 25:
                self.pos.x = 26
                self.vel = 0
                self.acceleration = 0

            elif self.pos.x > self.winSize[0] - 25:
                self.pos.x = self.winSize[0] - 26
                self.vel = 0
                self.acceleration = 0

    class Pendulum:
        drag = 2.5
        gravity = 0.1

        def __init__(self, winSize: tuple[int, int], length: float, angle: float) -> None:
            self.pos = Vector2d(winSize[0] / 2, winSize[1] / 2)
            self.mass = 0.1
            self.length = length

            self.angle = angle
            self.angularVelocity = 0
            self.angularAcceleration = 0
    
        def update(self, cartAcceleration, timeCoefficient):
            # computes angular accel from grav and cart movement
            #                                     gravity part                                      cart part
            self.angularAcceleration = (-Game.Pendulum.gravity * sin(self.angle) / self.length)  +  (cos(self.angle) * cartAcceleration / self.length)

            self.angularAcceleration -= self.angularVelocity*Game.Pendulum.drag/self.length    # drag as a negative acceleration instead of velocity mult

            # standard
            self.angularVelocity += self.angularAcceleration * timeCoefficient
            self.angle += self.angularVelocity * timeCoefficient

            self.angle = self.angle % (2 * pi)

    class Agent:
        def __init__(self, winSize, angle: float) -> None:
            self.pendulum = Game.Pendulum(winSize, 100, angle)
            self.cart = Game.Cart(winSize)

            self.streak = 1
            self.inStreak = False


    def __init__(self, winSize: tuple[int, int] | str = (1000, 700), render: bool = True, title: str = 'Window', backgroundColor: tuple[int, int, int] = (20, 20, 20)) -> None:
        super().__init__(winSize, title, backgroundColor)

        self.fps = 60
        self.fpsReference = 60  # IE: targeted fps

        self.render = render

        self.agents = []

        if self.render:
            self.initPygame()

    def create(self, genomes, nets, ge, config):
        self.genomes = genomes
        self.nets = nets
        self.config = config
        self.ge = ge

        self.agents.clear()

        angle = pi
        if random() > 0.5:
            angle += 0.05
        else:
            angle -= 0.05

        for _, g in self.genomes:
            g.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(g, self.config)
            self.nets.append(net)

            self.agents.append(Game.Agent(self.winSize, angle))

            self.ge.append(g)

    def update(self, dt: float):
        timeCoefficient = dt * self.fpsReference  # like dt but weighted/normalized with fps reference so it's 1 when running at targeted fps
        for id, agent in enumerate(self.agents):
            output = self.nets[id].activate([agent.pendulum.angle, agent.pendulum.angularVelocity, agent.cart.pos.x])

            if output[0] > 0.75:
                agent.cart.inputs[0] = True
            else:
                agent.cart.inputs[0] = False

            if output[1] > 0.75:
                agent.cart.inputs[1] = True
            else:
                agent.cart.inputs[1] = False

            agent.cart.update(timeCoefficient)
            agent.pendulum.update(agent.cart.acceleration, timeCoefficient)

            
            if agent.pendulum.angle >= pi/2 and agent.pendulum.angle <= pi + pi/2:
                agent.inStreak = True
                agent.streak *= 1.014
            else:
                if agent.inStreak:
                    self.ge[id].fitness += agent.streak
                    agent.streak = 1
                    agent.inStreak = False
            

    def run(self):
        '''Main loop'''
        dt = 1/self.fps
        self.running = True
        frame = 0

        while self.running:


            if self.render:
                self.handleEvents()

                self.update(dt)

                self.screen.fill(self.backgroundColor)  # Clear screen with black

                self.draw()

                pygame.display.flip()  # Update the display
                
                dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds (60 fps)

            else:
                self.update(dt)

            frame += 1
            if frame > 500:
                self.running = False

        for id, agent in enumerate(self.agents):
            if agent.inStreak:
                self.ge[id].fitness += agent.streak
                agent.streak = 1
                agent.inStreak = False


    def draw(self):
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.winSize[1] / 2), (self.winSize[0], self.winSize[1] / 2))
        
        for i, agent in enumerate(self.agents):
            if i == 0:
                pygame.draw.rect(self.screen, (0, 255, 0), pygame.rect.Rect(agent.cart.pos.x-25, agent.cart.pos.y-12.5, 50, 25))
            else:
                pygame.draw.rect(self.screen, (200, 0, 0), pygame.rect.Rect(agent.cart.pos.x-25, agent.cart.pos.y-12.5, 50, 25))

            pygame.draw.line(self.screen, (255, 255, 255), (agent.cart.pos.x, agent.cart.pos.y), (agent.cart.pos.x + cos(agent.pendulum.angle + pi/2)*agent.pendulum.length, agent.cart.pos.y + sin(agent.pendulum.angle + pi/2)*agent.pendulum.length), 3)
    
a = Game(render = False)

def eval_genomes(genomes, config):
    nets = []
    ge = []
    a.create(genomes, nets, ge, config)
    a.run()

def run_neat(config):
    import pickle
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-85')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 100)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)
        f.close()

if __name__ == '__main__':
    local_dir = path.dirname(__file__)
    config_path = path.join(local_dir, 'config.txt')


    run_neat(config_path)