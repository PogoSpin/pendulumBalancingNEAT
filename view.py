from time import sleep
import neat
from os import environ, path
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
        gravity = float(input())
        # gravity = 3


        def __init__(self, winSize: tuple[int, int], mass: int, length: float) -> None:
            self.pos = Vector2d(winSize[0] / 2, winSize[1] / 2)
            self.mass = 0.1
            self.length = length

            self.angle = pi
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
        def __init__(self, winSize) -> None:
            self.pendulum = Game.Pendulum(winSize, 10, 100)
            self.cart = Game.Cart(winSize)

            self.streak = 1
            self.inStreak = False


    def __init__(self, winSize: tuple[int, int] | str = (1000, 700), title = 'Window', backgroundColor: tuple[int, int, int] = (20, 20, 20)) -> None:
        super().__init__(winSize, title, backgroundColor)

        self.fps = 60
        self.fpsReference = 60  # IE: targeted fps

        self.agents = []
        self.bestGenome = None

        self.initPygame()

    def create(self, genomes, config):
        self.genomes = genomes
        self.config = config

        self.nets = []
        self.ge = []

        self.agents.clear()

        for _, g in self.genomes:
            g.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(g, self.config)
            self.nets.append(net)

            self.agents.append(Game.Agent(self.winSize))

            self.ge.append(g)

    def onKeyDown(self, key: pygame.event):
        if key == pygame.K_ESCAPE:
            self.running = False

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
                


                # if agent.pendulum.angle >= 2.793 and agent.pendulum.angle <= 3.491:
                #     self.ge[id].fitness += 0.1 / (abs(agent.pendulum.angularVelocity) + 0.1)
                # else:
                #     self.ge[id].fitness += 0.001 / (abs(agent.pendulum.angularVelocity) + 0.1)

            

    def run(self):
        '''Main loop'''
        dt = 1/self.fps
        self.running = True
        frame = 0

        while self.running:
            # self.handleEvents()

            self.update(dt)

            self.screen.fill(self.backgroundColor)  # Clear screen with black

            self.draw()

            pygame.display.flip()  # Update the display
            
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds (60 fps)
            frame += 1
            if frame > 500:
                self.running = False

        highestFitness = -1

        for id, agent in enumerate(self.agents):
            if agent.inStreak:
                self.ge[id].fitness += agent.streak
                agent.streak = 1
                agent.inStreak = False

            if self.ge[id].fitness > highestFitness:
                highestFitness = self.ge[id].fitness
                self.bestGenome = self.ge[id]

        # if highestFitness >= 1000:
        #     if self.Pendulum.gravity < 3:
        #         self.Pendulum.gravity += 0.01
        #         print('\nINCREASING GRAVITY\n')
        #         sleep(2)



    def draw(self):
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.winSize[1] / 2), (self.winSize[0], self.winSize[1] / 2))
        
        for i, agent in enumerate(self.agents):
            if i == 0:
                pygame.draw.rect(self.screen, (0, 255, 0), pygame.rect.Rect(agent.cart.pos.x-25, agent.cart.pos.y-12.5, 50, 25))
            else:
                pygame.draw.rect(self.screen, (200, 0, 0), pygame.rect.Rect(agent.cart.pos.x-25, agent.cart.pos.y-12.5, 50, 25))

            pygame.draw.line(self.screen, (255, 255, 255), (agent.cart.pos.x, agent.cart.pos.y), (agent.cart.pos.x + cos(agent.pendulum.angle + pi/2)*agent.pendulum.length, agent.cart.pos.y + sin(agent.pendulum.angle + pi/2)*agent.pendulum.length), 3)
    
a = Game()

def eval_genomes(genomes, config):
    print(a.Pendulum.gravity)
    
    a.create(genomes, config)
    a.run()

def use_genome(config):
    import pickle

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)
    
    with open('best.pickle', "rb") as f:
        genome = pickle.load(f)
    
    genomes = [(1, genome)]

    eval_genomes(genomes, config)

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

    try:
        winner = p.run(eval_genomes, 5000)

        with open("best.pickle", "wb") as f:
            pickle.dump(winner, f)
            f.close()
    except KeyboardInterrupt:
        print('Stopped by user, saving best genome.\n')
        print(a.bestGenome)

        with open("best.pickle", "wb") as f:
            pickle.dump(a.bestGenome, f)
            f.close()


if __name__ == '__main__':
    local_dir = path.dirname(__file__)
    config_path = path.join(local_dir, 'config.txt')


    # run_neat(config_path)
    use_genome(config_path)