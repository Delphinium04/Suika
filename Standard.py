import pygame
import math
import random

from enum import IntEnum

screen_width = 600
screen_height = 800


class Ball_args(IntEnum):
    X = 0
    Y = 1
    SPEED = 2
    HORIZONTAL_SPEED = 3
    NEXT_COLOR = 4
    NEXT_RADIUS = 5
    IS_DROPPING = 6


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

skwed_probabitity = [0.7, 0.1, 0.05, 0.08, 0.04, 0.02, 0.01, 0, 0]
gravity = 0.05
score = 0

ball_speed = 1
balls = []
balls_to_add = []
balls_to_remove = []

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.init()
running = True
game_over = False

index = range(len(order_score))
random_int = random.choices(index, weights=skwed_probabitity, k=1)[0]
next_ball_radius = order_radius[random_int]
next_ball_color = order_color[random_int]

while running:
    screen.fill(BLACK)
    # 항상 다음 공 미리보기
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_y = 20
    pygame.draw.circle(screen, next_ball_color,
                       (mouse_x, mouse_y), next_ball_radius)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] > 40 and event.pos[0] < 560:
                # draw a ball when mouse is clicked
                ball_x = event.pos[0]
                ball_y = min(event.pos[1], 50)
                horizontal_speed = 0
                is_dropping = True
                balls.append([ball_x, ball_y, ball_speed, horizontal_speed,
                             next_ball_color, next_ball_radius, is_dropping])

                next_index = random.choices(
                    index, weights=skwed_probabitity, k=1)[0]
                next_ball_color = order_color[next_index]
                next_ball_radius = order_radius[next_index]

    if not game_over:
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                # 85줄 append로 넘겨준 1차원 배열 요소 인덱스를 Ball_args enum 사용
                dx = balls[i][Ball_args.X] - balls[j][Ball_args.X]
                dy = balls[i][Ball_args.Y] - balls[j][Ball_args.Y]
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if distance < balls[i][Ball_args.NEXT_RADIUS] + balls[j][Ball_args.NEXT_RADIUS]:
                    if balls[i][Ball_args.NEXT_COLOR] == balls[j][Ball_args.NEXT_COLOR]:
                        color_index = order_color.index(
                            balls[i][Ball_args.NEXT_COLOR])
                        # handle special case when two last order balls collide they will be removed and score will be doubled
                        if color_index == len(order_color) - 1:
                            score += order_score[color_index] * 2
                        if color_index + 1 < len(order_color):
                            new_x = (balls[i][Ball_args.X] + balls[j]
                                     [Ball_args.X]) / 2 + random.uniform(-1, 1)
                            new_y = (balls[i][Ball_args.Y] + balls[j]
                                     [Ball_args.Y]) / 2 + random.uniform(0, 1)
                            balls_to_add.append([new_x, new_y, balls[i][2], balls[i][3] + balls[j][3],
                                                order_color[color_index + 1], order_radius[color_index + 1], False])
                            score += order_score[color_index + 1]

                        balls_to_remove.append(balls[i])
                        balls_to_remove.append(balls[j])
                        break

                    # if they touch but not of same color
                    else:
                        # check overlap
                        overlap = balls[i][Ball_args.NEXT_RADIUS] + \
                            balls[j][Ball_args.NEXT_RADIUS] - distance
                        dx = dx / distance
                        dy = dy / distance
                        balls[i][Ball_args.X] += dx * overlap / 2
                        balls[i][Ball_args.Y] += dy * overlap / 2
                        balls[j][Ball_args.X] -= dx * overlap / 2
                        balls[j][Ball_args.Y] -= dy * overlap / 2

                        # update speed of both balls when they collide
                        # 밑에 더 있던 balls[][Ball_args.HORIZONTAL~] *= 1 지움
                        balls[i][Ball_args.SPEED] = 0
                        balls[j][Ball_args.SPEED] = 0

                        # update the is_dropping flag
                        balls[i][Ball_args.IS_DROPPING] = False
                        balls[j][Ball_args.IS_DROPPING] = False

        # remove and add balls
        for ball in balls_to_remove:
            if ball in balls:
                balls.remove(ball)
        for ball in balls_to_add:
            balls.append(ball)

        # empty the lists
        balls_to_remove.clear()
        balls_to_add.clear()

        # draw balls
        for ball in balls:
            box_top = 40
            # if ball is not dropping and above the box, game over
            if (not ball[Ball_args.IS_DROPPING]) and ball[Ball_args.Y] - ball[Ball_args.NEXT_RADIUS] < box_top:
                game_over = True
                break
            ball[Ball_args.SPEED] += gravity

            box_bottom = 720 - ball[Ball_args.NEXT_RADIUS]
            box_left = 40 + ball[Ball_args.NEXT_RADIUS]
            box_right = 560 - ball[Ball_args.NEXT_RADIUS]
            if ball[Ball_args.Y] >= box_bottom:
                ball[Ball_args.Y] = box_bottom

            # 가속이 이상하게 됨
            elif (ball[Ball_args.IS_DROPPING]):
                ball[Ball_args.Y] += ball[Ball_args.SPEED] * 0.1
            else:
                ball[Ball_args.Y] += ball[Ball_args.SPEED]

            # update x position of ball
            ball[Ball_args.X] += ball[Ball_args.HORIZONTAL_SPEED]
            # check if ball is out of box horizontally
            if ball[Ball_args.X] < box_left:
                ball[Ball_args.X] = box_left + 1
                ball[Ball_args.HORIZONTAL_SPEED] *= -0.5
            elif ball[Ball_args.X] > box_right:
                ball[Ball_args.X] = box_right - 1
                ball[Ball_args.HORIZONTAL_SPEED] *= -0.5
            any_ball = pygame.draw.circle(
                screen, ball[Ball_args.NEXT_COLOR], (ball[Ball_args.X], ball[Ball_args.Y]), ball[Ball_args.NEXT_RADIUS])

        # draw 3 lines to make a rectangle with upper side open
        pygame.draw.line(screen, WHITE, (40, 40), (40, 720), 1)
        pygame.draw.line(screen, WHITE, (40, 720), (560, 720), 1)
        pygame.draw.line(screen, WHITE, (560, 720), (560, 40), 1)

        # draw a warning line at top of box with red dotted line
        dotted_line_y = 40
        dotted_line_length = 4
        dotted_line_space = 4

       # grey color dotted line
        dotted_line_color = (128, 128, 128)
        for x in range(40, 560, dotted_line_length + dotted_line_space):
            pygame.draw.line(screen, dotted_line_color, (x, dotted_line_y),
                             (x + dotted_line_length, dotted_line_y), 1)

        # draw color order
        color_order_y = screen_height - 20
        color_order_spacing = 40
        for i, color in enumerate(order_color):
            pygame.draw.circle(
                screen, color, (40 + i * color_order_spacing, color_order_y), 10)

        # draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (screen_width / 2 -
                    score_text.get_width()/2, 20))
        pygame.display.update()

    if game_over:
        font = pygame.font.Font(None, 36)
        game_over_text_lines = [
            "GAME OVER",
            f"Your Score is: {score}",
            "restart by pressing SPACE",
            "quit game by pressing ESCAPE"
        ]
        for i, line in enumerate(game_over_text_lines):
            line_text = font.render(line, True, WHITE)
            screen.blit(line_text, (screen_width / 2 - line_text.get_width() / 2,
                        screen_height / 2 - line_text.get_height() / 2 + i * line_text.get_height()))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # reset gaem when space is pressed
                    balls.clear()
                    balls_to_add.clear()
                    balls_to_remove.clear()
                    score = 0
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    # quit game when esc is pressed
                    running = False

pygame.quit()
