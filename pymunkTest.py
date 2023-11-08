import pygame
import math
import random
import pymunk
import pymunk.pygame_util
from enum import IntEnum

screen_size = (600, 600)
FPS = 60

screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
pygame.init()

running = True
game_over = False

# Physics
# https://youtu.be/tF4PctX66ek
space = pymunk.Space()
space.gravity = (0, 1000)
draw_options = pymunk.pygame_util.DrawOptions(screen)

# floor = pymunk.Body(body_type=pymunk.Body.STATIC)
# floor.position = (0, screen_height - 100)
# floor_shape = pymunk.Segment(floor, (0, 0), (screen_width, 0), 1)
# floor_shape.elasticity = 1
# space.add(floor, floor_shape)


class Ball():
    ball = None
    ball_shape = None

    def __init__(self, pos: tuple = (0, 0), radius: int = 10):
        self.ball = pymunk.Body(mass=1, moment=1)
        self.ball.position = pos
        self.ball_shape = pymunk.Circle(
            body=self.ball, radius=radius, offset=(0, 0))
        self.ball_shape.elasticity = 0.5
        return

    def set_visible(self):
        global space
        space.add(self.ball, self.ball_shape)


while running:
    clock.tick(FPS)
    space.step(1/FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            ball = Ball((300, 50), 10)
            ball.set_visible()

    # screen.fill(BLACK)

    screen.fill((0, 0, 0))
    space.debug_draw(draw_options)
    pygame.display.flip()

pygame.quit()
