import pygame as pg
import pymunk as pm
from pymunk import Vec2d
import random
import math
# https://stackoverflow.com/questions/53023396/how-not-to-render-ball-orientation-in-pymunk-space-debug-draw


def flipy(p):
    """Convert chipmunk physics to pygame coordinates."""
    return Vec2d(p[0], -p[1]+800)


class Entity(pg.sprite.Sprite):

    def __init__(self, pos, space, radius, mass=1):
        super().__init__()
        # The surface is a bit bigger, so that the circle fits better.
        self.orig_image = pg.Surface((radius*2+2, radius*2+2), pg.SRCALPHA)
        self.image = self.orig_image
        # Draw a circle onto the image.
        pg.draw.circle(
            self.image,
            pg.Color(random.randrange(256),
                     random.randrange(256),
                     random.randrange(256)),
            (radius+1, radius+1),  # +1 looks a bit better.
            radius)
        self.rect = self.image.get_rect(topleft=pos)

        # Create a Pymunk body and a shape and add them to the space.
        moment = pm.moment_for_circle(mass, radius, radius)
        self.body = pm.Body(mass, moment)
        self.shape = pm.Circle(self.body, radius)
        self.shape.friction = .1
        self.shape.elasticity = .99
        self.body.position = pos
        self.space = space
        self.space.add(self.body, self.shape)

    def update(self):
        # Update the rect because it's used to blit the image.
        self.rect.center = flipy(self.body.position)
        # Use the body's angle to rotate the image.
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.left < 0 or self.rect.right > 1280 or self.rect.y > 790:
            self.space.remove(self.body, self.shape)
            self.kill()


class Game:

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((1280, 800))
        self.done = False
        self.clock = pg.time.Clock()

        # Pymunk stuff
        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, -900.0)
        self.space.damping = .9
        self.static_lines = [
            pm.Segment(self.space.static_body, flipy(
                (60.0, 780.0)), flipy((650.0, 780.0)), .0),
            pm.Segment(self.space.static_body, flipy(
                (650.0, 780.0)), flipy((1218.0, 660.0)), .0)
        ]
        for lin in self.static_lines:
            lin.friction = 0.2
            lin.elasticity = 0.99
        self.space.add(self.static_lines)

        self.all_sprites = pg.sprite.Group()

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(60) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()
            self.current_fps = self.clock.get_fps()

        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button.
                    # Spawn an entity.
                    radius = random.randrange(20, 50)
                    self.all_sprites.add(
                        Entity(flipy(pg.mouse.get_pos()), self.space, radius))

        if pg.mouse.get_pressed()[2]:  # Right mouse button.
            radius = random.randrange(20, 50)
            self.all_sprites.add(
                Entity(flipy(pg.mouse.get_pos()), self.space, radius))

    def run_logic(self):
        self.space.step(1/60)
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(pg.Color(140, 120, 110))
        self.all_sprites.draw(self.screen)  # Draw the images of all sprites.

        # Draw the static lines.
        for line in self.static_lines:
            body = line.body
            p1 = flipy(body.position + line.a.rotated(body.angle))
            p2 = flipy(body.position + line.b.rotated(body.angle))
            pg.draw.lines(self.screen, pg.Color(
                'lightgray'), False, (p1, p2), 5)

        pg.display.flip()


if __name__ == '__main__':
    Game().run()
