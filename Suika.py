import math
import random
import pygame as pg
import pymunk as pm
import pymunk.pygame_util
from pymunk import Vec2d


'''
Debug Draw: https://stackoverflow.com/questions/53023396/how-not-to-render-ball-orientation-in-pymunk-space-debug-draw
'''

SCREEN_SIZE = (800, 800)
PREVIEW_BALL_OFFSET_Y = 60
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
THISTLE = (255, 0, 255)
HOTPINK = (255, 105, 180)
PURPLE = (128, 0, 128)

COLOR_ORDER: list = [WHITE, RED, ORANGE, YELLOW,
                     GREEN, BLUE, THISTLE, HOTPINK, PURPLE]
SCORE_ORDER: list = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RADIUS_ORDER: list = [15, 22, 29, 40, 55, 70, 85, 100, 120]

COOLDOWN_DURATION = 1000  # 0초 1000 = 1초


def get_next_radius(cur_radius):
    ''' return -1 if radius is max level '''
    if cur_radius == RADIUS_ORDER[-1]:
        return -1
    index = RADIUS_ORDER.index(cur_radius)
    return index + 1


def flipy(p):
    """Convert chipmunk physics to pygame coordinates."""
    return Vec2d(p[0], -p[1]+800)


class Game:
    class Ball(pg.sprite.Sprite):

        def __init__(self, pos, radius, color, space, is_static=False):
            super().__init__()
            # args
            self.color = pg.Color(color)

            self.origin_image = pg.Surface(
                (radius*2+2, radius*2+2), pg.SRCALPHA)
            self.image = self.origin_image

            pg.draw.circle(self.image, self.color,
                           (radius+1, radius+1), radius)
            self.rect = self.image.get_rect(topleft=pos)

            if is_static:
                self.body = pm.Body(body_type=pm.Body.KINEMATIC)
            else:
                self.body = pm.Body(10000000, 1)
                self.body.velocity_func = Game.custom_gravity

            self.body.position = pos
            self.shape = pm.Circle(body=self.body, radius=radius)
            self.shape.elasticity = 0
            self.shape.friction = 1
            self.shape.color = self.color
            self.space = space
            self.space.add(self.body, self.shape)

        def update(self):
            self.rect.center = flipy(self.body.position)
            # Use the body's angle to rotate the image.
            self.image = pg.transform.rotozoom(
                self.origin_image, math.degrees(self.body.angle), 1)
            self.rect = self.image.get_rect(center=self.rect.center)

        def get_radius(self):
            return self.shape.radius

        def get_color(self) -> pg.Color:
            return self.color

        def set_color(self, rgb: tuple):
            self.color = pg.Color(rgb)
            self.shape.color = self.color

        def set_position(self, pos: tuple):
            self.body.position = pos

        def get_position(self) -> tuple:
            return self.body.position

    def __init__(self):
        # Pygame Setting
        pg.init()
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.done = False
        self.clock = pg.time.Clock()

        # Suika Setting
        self.game_over = False
        self.is_ball_cooldown = False
        self.last_create_time = 0
        self.score = 0
        self.ball_probability = [0.7, 0.3, 0, 0, 0, 0, 0, 0, 0]

        self.balls: list[self.Ball] = []
        self.ball_range = range(len(SCORE_ORDER))
        self.random_int = random.choices(
            self.ball_range, weights=self.ball_probability, k=1)[0]
        self.next_ball_radius = RADIUS_ORDER[self.random_int]
        self.next_ball_color = COLOR_ORDER[self.random_int]

        # Pymunk stuff
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        # FEATURE?
        # self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.all_sprites = pg.sprite.Group()

        self.planet = self.Ball(
            (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2), RADIUS_ORDER[4], WHITE, self.space, True)

        self.wall_bottom = pm.Body(body_type=pm.Body.STATIC)
        self.wall_bottom_shape = pm.Segment(
            self.wall_bottom, (50, SCREEN_SIZE[1]-50), (SCREEN_SIZE[0]-50, SCREEN_SIZE[1]-50), 3)
        self.wall_left = pm.Body(body_type=pm.Body.STATIC)
        self.wall_right = pm.Body(body_type=pm.Body.STATIC)
        self.wall_left_shape = pm.Segment(
            self.wall_left, (250, 100), (250, SCREEN_SIZE[1]-50), 3)
        self.wall_right_shape = pm.Segment(
            self.wall_right, (SCREEN_SIZE[0]-50, 100), (SCREEN_SIZE[0]-50, SCREEN_SIZE[1]-50), 3)
        self.space.add(self.wall_left, self.wall_left_shape)
        self.space.add(self.wall_right, self.wall_right_shape)
        self.space.add(self.wall_bottom, self.wall_bottom_shape)

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(60) / 1000
            if self.game_over:
                self.show_exit_menu()
            else:
                self.handle_events()
                self.run_logic()
                self.check_collision()
                self.check_end()
                self.draw()
                self.current_fps = self.clock.get_fps()

        pg.display.quit()
        pg.quit()
        exit()

    def show_exit_menu(self):
        font = pg.font.Font(None, 36)
        game_over_text_lines = [
            "GAME OVER",
            f"Your Score is: {self.score}",
            "restart by pressing SPACE",
            "quit game by pressing ESCAPE"
        ]
        for i, line in enumerate(game_over_text_lines):
            line_text = font.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_SIZE[0] / 2 - line_text.get_width() / 2,
                                         SCREEN_SIZE[1] / 2 - line_text.get_height() / 2 + i * line_text.get_height()))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    Game().run()
                    self.balls.clear()
                    self.score = 0
                    self.game_over = False
                elif event.key == pg.K_ESCAPE:
                    self.done = True
        pg.display.flip()
        self.screen.fill(pg.Color((0, 0, 0, 200)))

    def handle_events(self):
        # Keyboard Event
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                self.game_over = True
        # Mouse Event
        if pg.mouse.get_pressed()[0]:
            current_time = pg.time.get_ticks()
            is_cooldown = current_time - self.last_create_time < COOLDOWN_DURATION
            if not is_cooldown:
                self.last_create_time = current_time
                is_cooldown = True
                mouse_pos = pg.mouse.get_pos()

                # 80 < X < SCREENSIZE.X - 80
                x = max(80, min(mouse_pos[0], SCREEN_SIZE[0] - 80))
                y = PREVIEW_BALL_OFFSET_Y
                self.generate_ball(x, y)

                next_index = random.choices(
                    self.ball_range, weights=self.ball_probability, k=1)[0]
                self.next_ball_color = COLOR_ORDER[next_index]
                self.next_ball_radius = RADIUS_ORDER[next_index]

    def run_logic(self):
        self.space.step(1/60)
        self.all_sprites.update()

    def change_probability(self):
        if self.score >= 4 and self.score < 12:
            self.ball_probability = [0.55, 0.4, 0.05, 0, 0, 0, 0, 0, 0]
        elif self.score >= 12 and self.score < 32:
            self.ball_probability = [0.35, 0.35, 0.25, 0.05, 0, 0, 0, 0, 0]
        elif self.score >= 32 and self.score < 128:
            self.ball_probability = [0.2, 0.35, 0.25, 0.15, 0.05, 0, 0, 0, 0]
        elif self.score >= 128:
            self.ball_probability = [0.1, 0.35, 0.27, 0.18, 0.1, 0, 0, 0, 0]
        return

    def check_collision(self):
        # if ball merged -> return
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                ball_i, ball_j = self.balls[i], self.balls[j]
                pointSet = ball_i.shape.shapes_collide(ball_j.shape)
                is_hit = len(pointSet.points) != 0  # 접점
                # hit and level is same
                if is_hit and ball_i.get_radius() == ball_j.get_radius():
                    next_index = get_next_radius(ball_i.get_radius())
                    self.change_probability()
                    # if level is NOT max generate new ball
                    if next_index != -1:
                        target_pos = ((ball_i.get_position()[0] + ball_j.get_position()[0])/2,
                                      (ball_i.get_position()[1] + ball_j.get_position()[1])/2)
                        new_ball = self.Ball(
                            target_pos, RADIUS_ORDER[next_index], COLOR_ORDER[next_index], self.space)
                        self.balls.append(new_ball)
                        self.score += SCORE_ORDER[next_index-1]
                    else:
                        self.score += SCORE_ORDER[-1]
                    self.remove_ball(ball_i, ball_j)
                    return

    def draw(self):
        self.screen.fill(pg.Color(140, 120, 110))
        self.all_sprites.draw(self.screen)  # Draw the images of all sprites.

        pg.draw.circle(self.screen, self.planet.get_color(),
                       self.planet.get_position(), self.planet.get_radius())

        mouse_x = max(80, min(pg.mouse.get_pos()[0], SCREEN_SIZE[1] - 80))
        pg.draw.circle(self.screen, self.next_ball_color,
                       (mouse_x, PREVIEW_BALL_OFFSET_Y), self.next_ball_radius)

        for ball in self.balls:
            pg.draw.circle(self.screen, ball.get_color(),
                           ball.get_position(), ball.get_radius())

        # color order draw
        colors_coord_y = SCREEN_SIZE[1] - 20
        colors_each_space = 40
        for i, color in enumerate(COLOR_ORDER):
            pg.draw.circle(
                self.screen, color, (40 + i * colors_each_space, colors_coord_y), 10)

        # draw score
        font = pg.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (SCREEN_SIZE[0] / 2 -
                                      score_text.get_width()/2, 20))
        # bottom, left, right
        pg.draw.line(self.screen, WHITE,  (50,
                     SCREEN_SIZE[1]-50), (SCREEN_SIZE[0]-50, SCREEN_SIZE[1]-50), 3)
        pg.draw.line(self.screen, WHITE, (250, 100),
                     (250, SCREEN_SIZE[1]-50), 3)
        pg.draw.line(self.screen, WHITE,
                     (SCREEN_SIZE[0]-50, 100), (SCREEN_SIZE[0]-50, SCREEN_SIZE[1]-50), 3)

        pg.display.flip()

    def check_end(self):
        for ball in self.balls:
            if ball.shape.shapes_collide(self.wall_left_shape).points or \
                    ball.shape.shapes_collide(self.wall_right_shape).points or \
                    ball.shape.shapes_collide(self.wall_bottom_shape).points:
                self.game_over = True

    def generate_ball(self, x, y):
        ball = self.Ball((x, y), self.next_ball_radius,
                         self.next_ball_color, self.space)
        ball.set_color(self.next_ball_color)
        ball.set_position((x, y))
        self.balls.append(ball)

    def remove_ball(self, *args):
        for ball in args:
            if ball in self.balls:
                self.balls.remove(ball)
            self.space.remove(ball.shape, ball.body)

    def custom_gravity(body: pm.Body, gravity, damping, dt):
        current_coord = body.position
        target_vec = ((SCREEN_SIZE[0]/2 - current_coord[0])*2,
                      (SCREEN_SIZE[1]/2 - current_coord[1])*2)
        pymunk.Body.update_velocity(body, target_vec, damping, dt)


if __name__ == '__main__':
    Game().run()
