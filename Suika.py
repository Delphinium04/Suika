import pygame as pg
import pymunk as pm
import pymunk.pygame_util
import math
import random
import SettingsForSuika as user_settings
from typing import List  # to show type hint in collision_ball_hit()
from enum import IntEnum

SCREEN_SIZE = user_settings.Options().screen_size
FPS = user_settings.Options().fps

# https://www.pymunk.org/en/latest/pymunk.html Document

'''
수정 주의사항!
수정할 일 있으면 수정하되 주석 처리한 링크는 맨 위로 올려서라도 살려두기
레벨은 Color로 구분하지 않고 pymunk.Circle.radius를 통해 구분 (order_radius[] 와 get_next_radius() 사용하기 (최고레벨이면 -1 반환))

Debug Draw -> PyGame Draw 전환: https://stackoverflow.com/questions/53023396/how-not-to-render-ball-orientation-in-pymunk-space-debug-draw

'''

# region GameSetting

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

order_color = [WHITE, RED, ORANGE, YELLOW,
               GREEN, BLUE, THISTLE, HOTPINK, PURPLE]
order_score = [1, 2, 4, 8, 16, 32, 64, 128, 256]
order_radius = [15, 22, 42, 55, 68, 85, 94, 110, 130]

# 확통 내용?
skwed_probabitity = [0.7, 0.1, 0.05, 0.08, 0.04, 0.02, 0.01, 0, 0]
score = 0

# pygame init
running = True
game_over = False


class Ball():
    """
    클래스 생성 시 초기 위치, 반지름(초기값 고정), STATIC 여부 설정 가능\n
    set_color로 색 설정 후 set_visible()로 space에 추가
    """

    def __init__(self, pos=(0, 0), radius=order_radius[0], is_static=False):
        if is_static:
            self.body = pm.Body(body_type=pm.Body.KINEMATIC)
        else:
            self.body = pm.Body(1, 1)
        self.body.position = pos
        self.shape = pm.Circle(
            body=self.body, radius=radius, offset=(0, 0))
        self.shape.elasticity = 0.5
        self.shape.friction = 0.1
        self.is_dropped = False
        self.shape.color = (255, 255, 255, 255)

    def set_color(self, rgb: tuple):
        color = (rgb[0], rgb[1], rgb[2], 255)
        self.shape.color = color

    def set_position(self, pos: tuple):
        self.body.position = pos

    def set_visible(self):
        space.add(self.body, self.shape)
        if self.body.body_type != pm.Body.KINEMATIC:
            print(f'Level {order_radius.index(
                self.shape.radius)} ball Set visible')

    def get_position(self) -> tuple:
        return self.body.position


def get_next_radius(current_radius) -> int:
    next_idx = order_radius.index(current_radius) + 1
    return next_idx if next_idx < len(order_radius) else -1


def remove_ball(*args: Ball):
    if len(args) == 0:
        return
    for ball in args:
        if ball in balls:
            balls.remove(ball)
        space.remove(ball.shape, ball.body)


pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)
clock = pg.time.Clock()

random_index = range(len(order_score))
random_int = random.choices(random_index, weights=skwed_probabitity, k=1)[0]
next_ball_radius = order_radius[random_int]
next_ball_color = order_color[random_int]

# physics init
space = pm.Space()
space.gravity = (0, 1000)
draw_options = pymunk.pygame_util.DrawOptions(screen)

wall_bottom = pm.Body(body_type=pm.Body.STATIC)
wall_left = pm.Body(body_type=pm.Body.STATIC)
wall_right = pm.Body(body_type=pm.Body.STATIC)
wall_bottom_shape = pm.Segment(
    wall_bottom, (50, SCREEN_SIZE[1]-50), (SCREEN_SIZE[0]-50, SCREEN_SIZE[1]-50), 3)
wall_left_shape = pm.Segment(
    wall_left, (50, 100), (50, SCREEN_SIZE[1]-50), 3)
wall_right_shape = pm.Segment(
    wall_right, (SCREEN_SIZE[0]-50, 100), (SCREEN_SIZE[0]-50, SCREEN_SIZE[1]-50), 3)
space.add(wall_bottom, wall_bottom_shape)
space.add(wall_left, wall_left_shape)
space.add(wall_right, wall_right_shape)

# preview ball init
preview_ball = Ball(is_static=True)
preview_ball.set_color(next_ball_color)
preview_ball.set_visible()

balls: List[Ball] = []
# endregion

while running:
    if game_over:
        font = pg.font.Font(None, 36)
        game_over_text_lines = [
            "GAME OVER",
            f"Your Score is: {score}",
            "restart by pressing SPACE",
            "quit game by pressing ESCAPE"
        ]
        for i, line in enumerate(game_over_text_lines):
            line_text = font.render(line, True, WHITE)
            screen.blit(line_text, (SCREEN_SIZE[0] / 2 - line_text.get_width() / 2,
                        SCREEN_SIZE[1] / 2 - line_text.get_height() / 2 + i * line_text.get_height()))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    remove_ball(*balls)
                    balls.clear()
                    score = 0
                    game_over = False
                elif event.key == pg.K_ESCAPE:
                    running = False
        space.debug_draw(draw_options)
        pg.display.update()
        continue

    screen.fill(BLACK)
    clock.tick(FPS)
    space.step(1/FPS)  # Physics framerate interval

    # 항상 다음 공 미리보기
    preview_ball_coord_y = 20
    preview_ball.set_color(next_ball_color)
    preview_ball.set_position((pg.mouse.get_pos()[0], preview_ball_coord_y))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.pos[0] > 40 and event.pos[0] < SCREEN_SIZE[0] - 40:
                # draw a ball when mouse is clicked
                x = event.pos[0]
                y = min(event.pos[1], 30)
                ball = Ball(pos=(x, y), radius=next_ball_radius)
                ball.set_color(next_ball_color)
                ball.set_position((x, y))
                ball.set_visible()
                balls.append(ball)
                print(f"current {len(balls)} balls")
                # random setting
                next_index = random.choices(
                    random_index, weights=skwed_probabitity, k=1)[0]
                next_ball_color = order_color[next_index]
                next_ball_radius = order_radius[next_index]
                # refresh preview ball
                remove_ball(preview_ball)
                preview_ball = Ball(pos=(pg.mouse.get_pos()[0], 30),
                                    radius=next_ball_radius, is_static=True)
                preview_ball.set_visible()

    # check current position is valid
    for ball in balls:
        pos = ball.get_position()
        if pos[0] < 0 or pos[0] > SCREEN_SIZE[0] or pos[1] < 0 or pos[1] > SCREEN_SIZE[1]:
            remove_ball(ball)
            game_over = True
            print('TEST: GAME OVER')
            continue

    for i in range(len(balls)):
        # if ball removed, escape all of for loops
        need_to_escape = False
        for j in range(i+1, len(balls)):
            pointSet = balls[i].shape.shapes_collide(balls[j].shape)
            is_hit = len(pointSet.points) != 0
            # hit and level is same
            if is_hit and balls[i].shape.radius == balls[j].shape.radius:
                next_level_index = get_next_radius(balls[i].shape.radius)
                # if level != max
                if next_level_index != -1:
                    target_pos = ((balls[i].get_position()[0] + balls[j].get_position()[0])/2,
                                  (balls[i].get_position()[1] + balls[j].get_position()[1])/2)
                    b = Ball(target_pos, radius=order_radius[next_level_index])
                    b.set_color(order_color[next_level_index])
                    b.set_visible()
                    balls.append(b)
                remove_ball(balls[i], balls[j])
                need_to_escape = True
                break
        if need_to_escape:
            break

    # draw color
    colors_coord_y = SCREEN_SIZE[1] - 20
    colors_each_space = 40
    for i, color in enumerate(order_color):
        pg.draw.circle(
            screen, color, (40 + i * colors_each_space, colors_coord_y), 10)

    # draw score
    font = pg.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (SCREEN_SIZE[0] / 2 -
                score_text.get_width()/2, 20))
    space.debug_draw(draw_options)
    pg.display.update()
    continue


pg.quit()
