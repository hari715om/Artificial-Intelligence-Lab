import pygame
import sys
import random

WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 14

PADDLE_SPEED = 7
BALL_START_SPEED = 5
BALL_SPEED_UP_FACTOR = 1.05  
WIN_SCORE = 5

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - Local Two Player (WS vs IK)")
clock = pygame.time.Clock()

font_score = pygame.font.SysFont("Consolas", 40)
font_msg = pygame.font.SysFont("Consolas", 28)

left_paddle = pygame.Rect(60, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                          PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 60 - PADDLE_WIDTH,
                           HEIGHT // 2 - PADDLE_HEIGHT // 2,
                           PADDLE_WIDTH, PADDLE_HEIGHT)

ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2,
                   HEIGHT // 2 - BALL_SIZE // 2,
                   BALL_SIZE, BALL_SIZE)

ball_vel_x = BALL_START_SPEED
ball_vel_y = BALL_START_SPEED
left_score = 0
right_score = 0
game_over = False
winner_text = ""


def reset_ball(direction=None):
    global ball_vel_x, ball_vel_y
    ball.center = (WIDTH // 2, HEIGHT // 2)

    if direction is None:
        direction = random.choice([-1, 1])

    speed = BALL_START_SPEED
    ball_vel_x = speed * direction
    ball_vel_y = random.choice([-1, 1]) * speed


def reset_game():
    global left_score, right_score, game_over, winner_text
    left_score = 0
    right_score = 0
    winner_text = ""
    game_over = False
    reset_ball(direction=random.choice([-1, 1]))


reset_ball()


# ------------ MAIN LOOP ------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += PADDLE_SPEED

        if keys[pygame.K_i] and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_k] and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED

        ball.x += ball_vel_x
        ball.y += ball_vel_y

        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel_y = -ball_vel_y

        if ball.colliderect(left_paddle) and ball_vel_x < 0:
            ball.left = left_paddle.right  # avoid sticking
            ball_vel_x = -ball_vel_x * BALL_SPEED_UP_FACTOR
            ball_vel_y *= BALL_SPEED_UP_FACTOR

        if ball.colliderect(right_paddle) and ball_vel_x > 0:
            ball.right = right_paddle.left
            ball_vel_x = -ball_vel_x * BALL_SPEED_UP_FACTOR
            ball_vel_y *= BALL_SPEED_UP_FACTOR

        if ball.right < 0:
            right_score += 1
            if right_score >= WIN_SCORE:
                game_over = True
                winner_text = "Right Player (I/K) Wins!"
            reset_ball(direction=1)

        if ball.left > WIDTH:
            left_score += 1
            if left_score >= WIN_SCORE:
                game_over = True
                winner_text = "Left Player (W/S) Wins!"
            reset_ball(direction=-1)

    screen.fill((0, 0, 0))

    for y in range(0, HEIGHT, 20):
        if (y // 20) % 2 == 0:
            pygame.draw.rect(screen, (255, 255, 255),
                             (WIDTH // 2 - 2, y, 4, 10))

    pygame.draw.rect(screen, (255, 255, 255), left_paddle)
    pygame.draw.rect(screen, (255, 255, 255), right_paddle)
    pygame.draw.ellipse(screen, (255, 255, 255), ball)

    left_text = font_score.render(str(left_score), True, (255, 255, 255))
    right_text = font_score.render(str(right_score), True, (255, 255, 255))
    screen.blit(left_text, (WIDTH // 4 - left_text.get_width() // 2, 20))
    screen.blit(right_text, (WIDTH * 3 // 4 - right_text.get_width() // 2, 20))

    help_text = font_msg.render("W/S = Left, I/K = Right | First to 5 | SPACE = Restart",
                                True, (180, 180, 180))
    screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 40))

    if game_over:
        msg = font_msg.render(winner_text, True, (255, 215, 0))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))
        sub = font_msg.render("Press SPACE to play again", True, (200, 200, 200))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 5))

    pygame.display.flip()

pygame.quit()
sys.exit()
