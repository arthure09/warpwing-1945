# Initialize Pygame
import pygame
import random

pygame.init()
pygame.mixer.init()  # Initialize Pygame Mixer for sound

# Load sounds
shoot_sound = pygame.mixer.Sound("shoot.wav")
collision_sound = pygame.mixer.Sound("collision.wav")
level_up_sound = pygame.mixer.Sound("level_up.wav")
background_music = "background_music.ogg"

# Play background music in a loop
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)

# Screen dimensions
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN.get_size()
pygame.display.set_caption("Game STRUKDAT")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game constants
PIPE_SPEED = -6
PIPE_GAP = 400
FPS = 60
GRAVITY = 0.1
BIRD_JUMP = -8
BULLET_SPEED = 10
ENEMY_SPEED = -4
ENEMY_SPAWN_CHANCE = 0.5

# Level settings
LEVEL_THRESHOLDS = [20, 50, 100]  # Scores to transition levels
LEVEL_SPEED_MULTIPLIERS = [1, 1.5, 2]  # Speed multipliers for each level

# Bird properties
BIRD_WIDTH = 100
BIRD_HEIGHT = 100
bird_x = 100
bird_y = SCREEN_HEIGHT // 2
bird_x_change = 0
bird_y_change = 0

# Bullets
bullets = []

# Pipes
PIPE_WIDTH = 80
pipes = []

# Enemies
enemies = []

# Score variables
score = 0
best_score = 0
can_score = True
level = 1

# Leaderboard file
LEADERBOARD_FILE = "scores.txt"

# Font
font = pygame.font.Font(pygame.font.get_default_font(), 36)

# Load images
slide1 = pygame.image.load("slide1.png")
slide2 = pygame.image.load("slide2.png")
slide3 = pygame.image.load("slide3.png")
slide4 = pygame.image.load("slide4.png")
alien_image = pygame.image.load("alien.png")
plane_image = pygame.image.load("plane.png")
background_image = pygame.image.load("background2.png")
gunung_image = pygame.image.load("gunung.png")  # Load mountain image for pipes

# Scale images
slide1 = pygame.transform.scale(slide1, (SCREEN_WIDTH, SCREEN_HEIGHT))
slide2 = pygame.transform.scale(slide2, (SCREEN_WIDTH, SCREEN_HEIGHT))
slide3 = pygame.transform.scale(slide3, (SCREEN_WIDTH, SCREEN_HEIGHT))
slide4 = pygame.transform.scale(slide4, (SCREEN_WIDTH, SCREEN_HEIGHT))
alien_image = pygame.transform.scale(alien_image, (40, 40))
plane_image = pygame.transform.scale(plane_image, (BIRD_WIDTH, BIRD_HEIGHT))
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
gunung_image = pygame.transform.scale(gunung_image, (PIPE_WIDTH, 400))  # Scale mountain image for pipes

# Game states
class GameState:
    USERNAME_INPUT = 0
    LANDING_PAGE = 1
    RUNNING = 2
    GAME_OVER = 3
    GAME_COMPLETED = 4  # New state for game completion

game_state = GameState.USERNAME_INPUT
username = ""
slide_index = 0  # Tracks which slide is currently displayed

def display_username_input():
    """Display the screen for username input."""
    SCREEN.fill(BLACK)
    title_text = font.render("Enter Your Username:", True, WHITE)
    username_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2, 400, 50)
    pygame.draw.rect(SCREEN, WHITE, username_box, 2)

    username_text = font.render(username, True, WHITE)
    instruction_text = font.render("Press ENTER to continue", True, WHITE)

    SCREEN.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    SCREEN.blit(username_text, (username_box.x + 10, username_box.y + 10))
    SCREEN.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

def draw_bird(x, y):
    """Draw the plane on the screen."""
    SCREEN.blit(plane_image, (x, y))

def draw_bullets():
    """Draw bullets on the screen."""
    for bullet in bullets:
        pygame.draw.rect(SCREEN, YELLOW, bullet)

def move_bullets():
    """Move bullets and remove those that go off-screen."""
    global bullets
    for bullet in bullets:
        bullet.x += BULLET_SPEED
    bullets = [bullet for bullet in bullets if bullet.x < SCREEN_WIDTH]

def generate_pipe():
    """Generate a new pair of pipes with dynamic gaps."""
    global PIPE_GAP
    dynamic_gap = max(150, PIPE_GAP - (level - 1) * 20)  # Decrease gap by 20 per level, minimum gap is 150
    pipe_height = random.randint(200, SCREEN_HEIGHT - 400)
    top_pipe = pygame.Rect(SCREEN_WIDTH, 0, PIPE_WIDTH, pipe_height)
    bottom_pipe = pygame.Rect(SCREEN_WIDTH, pipe_height + dynamic_gap, PIPE_WIDTH, SCREEN_HEIGHT - pipe_height - dynamic_gap)
    return top_pipe, bottom_pipe

def generate_enemy(top_pipe, bottom_pipe):
    """Generate an enemy in the middle of the pipe gap."""
    enemy_y = top_pipe.bottom + (bottom_pipe.top - top_pipe.bottom) // 2 - 20
    enemy = pygame.Rect(SCREEN_WIDTH, enemy_y, 40, 40)
    return enemy

def move_pipes():
    """Move pipes to the left and remove off-screen pipes."""
    global pipes
    for pipe in pipes:
        pipe.x += PIPE_SPEED * LEVEL_SPEED_MULTIPLIERS[level - 1]
    pipes = [pipe for pipe in pipes if pipe.right > 0]

def move_enemies():
    """Move enemies to the left and remove off-screen enemies."""
    global enemies
    for enemy in enemies:
        enemy.x += ENEMY_SPEED * LEVEL_SPEED_MULTIPLIERS[level - 1]
    enemies = [enemy for enemy in enemies if enemy.x > 0]

def draw_pipes(pipe_list):
    """Draw all pipes using the gunung.png image."""
    for pipe in pipe_list:
        if pipe.y == 0:  # Top pipe
            flipped_gunung = pygame.transform.flip(gunung_image, False, True)
            SCREEN.blit(flipped_gunung, (pipe.x, pipe.bottom - 400))
        else:  # Bottom pipe
            SCREEN.blit(gunung_image, (pipe.x, pipe.y))

def draw_enemies():
    """Draw all alien enemies."""
    for enemy in enemies:
        SCREEN.blit(alien_image, (enemy.x, enemy.y))

def check_collision(bird_rect):
    """Check if the bird collides with a pipe or the screen boundaries."""
    global pipes, can_score
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            collision_sound.play()  # Play collision sound
            can_score = True
            return True
    if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT:
        collision_sound.play()  # Play collision sound
        can_score = True
        return True
    return False

def check_bird_enemy_collision(bird_rect):
    """Check if the bird collides with any enemy."""
    for enemy in enemies:
        if bird_rect.colliderect(enemy):
            collision_sound.play()  # Play collision sound
            return True
    return False

def check_bullet_enemy_collision():
    """Check if bullets collide with enemies."""
    global bullets, enemies, score
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

def update_score():
    """Update the score when the bird passes through a pipe."""
    global score, can_score
    for pipe in pipes:
        if bird_x + BIRD_WIDTH < pipe.centerx < bird_x + BIRD_WIDTH + 5 and can_score:
            score += 1
            can_score = False
    if all(pipe.centerx < bird_x for pipe in pipes):
        can_score = True

def display_score():
    """Display the score on the screen."""
    score_text = font.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(score_text, (10, 10))

def display_level():
    """Display the current level."""
    level_text = font.render(f"Level: {level}", True, WHITE)
    SCREEN.blit(level_text, (SCREEN_WIDTH - 150, 10))

def display_game_completed():
    """Display the Game Completed screen."""
    SCREEN.blit(slide4, (0, 0))

def save_score(username, score):
    """Save the score to the leaderboard file."""
    with open(LEADERBOARD_FILE, "a") as file:
        file.write(f"{username} {score}\n")

def get_top_scores():
    """Get the top 5 scores from the leaderboard file."""
    try:
        with open(LEADERBOARD_FILE, "r") as file:
            scores = [line.strip().split() for line in file.readlines()]
            scores = [(name, int(score)) for name, score in scores]
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:5]
    except FileNotFoundError:
        return []

def display_game_over():
    """Display the Game Over screen with leaderboard."""
    SCREEN.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, WHITE)
    your_score_text = font.render(f"Your Score: {score}", True, WHITE)
    best_score_text = font.render(f"Best Score: {best_score}", True, WHITE)
    replay_text = font.render("Press ENTER to play again", True, WHITE)

    SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
    SCREEN.blit(your_score_text, (SCREEN_WIDTH // 2 - your_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
    SCREEN.blit(best_score_text, (SCREEN_WIDTH // 2 - best_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

    # Display leaderboard
    leaderboard_title = font.render("Leaderboard:", True, WHITE)
    SCREEN.blit(leaderboard_title, (SCREEN_WIDTH // 2 - leaderboard_title.get_width() // 2, SCREEN_HEIGHT // 2))
    top_scores = get_top_scores()
    for i, (name, top_score) in enumerate(top_scores):
        score_text = font.render(f"{i + 1}. {name}: {top_score}", True, WHITE)
        SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50 + i * 30))

    SCREEN.blit(replay_text, (SCREEN_WIDTH // 2 - replay_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    SCREEN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Username input
            if game_state == GameState.USERNAME_INPUT:
                if event.key == pygame.K_RETURN and username.strip():
                    game_state = GameState.LANDING_PAGE
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20 and event.unicode.isprintable():
                        username += event.unicode

            # Landing page navigation
            elif game_state == GameState.LANDING_PAGE:
                if event.key == pygame.K_RETURN:
                    slide_index += 1
                    if slide_index > 2:  # Move to game after last slide
                        game_state = GameState.RUNNING

            # Game controls
            elif game_state == GameState.RUNNING:
                if event.key == pygame.K_SPACE:
                    bullet = pygame.Rect(bird_x + BIRD_WIDTH, bird_y + BIRD_HEIGHT // 2 - 5, 10, 10)
                    bullets.append(bullet)
                    shoot_sound.play()  # Play shooting sound
                if event.key == pygame.K_w:
                    bird_y_change = -5
                if event.key == pygame.K_s:
                    bird_y_change = 5
                if event.key == pygame.K_a:
                    bird_x_change = -5
                if event.key == pygame.K_d:
                    bird_x_change = 5

            # Game Over or Completed screen navigation
            elif game_state in [GameState.GAME_OVER, GameState.GAME_COMPLETED]:
                if event.key == pygame.K_RETURN:
                    game_state = GameState.USERNAME_INPUT
                    pipes.clear()
                    enemies.clear()
                    bullets.clear()
                    bird_x, bird_y = 100, SCREEN_HEIGHT // 2
                    score = 0
                    bird_x_change = 0
                    bird_y_change = 0

        if event.type == pygame.KEYUP and game_state == GameState.RUNNING:
            if event.key in [pygame.K_w, pygame.K_s]:
                bird_y_change = 0
            if event.key in [pygame.K_a, pygame.K_d]:
                bird_x_change = 0

    # Game state logic
    if game_state == GameState.USERNAME_INPUT:
        display_username_input()

    elif game_state == GameState.LANDING_PAGE:
        if slide_index == 0:
            SCREEN.blit(slide1, (0, 0))
        elif slide_index == 1:
            SCREEN.blit(slide2, (0, 0))
        elif slide_index == 2:
            SCREEN.blit(slide3, (0, 0))

    elif game_state == GameState.RUNNING:
        # Draw background
        SCREEN.blit(background_image, (0, 0))

        # Apply gravity and movement to bird
        bird_x += bird_x_change
        bird_y_change += GRAVITY
        bird_y += bird_y_change
        bird_x = max(0, min(SCREEN_WIDTH - BIRD_WIDTH, bird_x))
        bird_y = max(0, min(SCREEN_HEIGHT - BIRD_HEIGHT, bird_y))

        # Update pipes
        move_pipes()

        # Update enemies
        if len(pipes) >= 2 and random.random() < ENEMY_SPAWN_CHANCE / FPS:
            enemies.append(generate_enemy(pipes[0], pipes[1]))
        move_enemies()

        # Generate new pipes
        while len(pipes) < 6:  # Generate more pipes to increase difficulty
            pipes += generate_pipe()

        # Check for collisions
        bird_rect = pygame.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
        if check_collision(bird_rect) or check_bird_enemy_collision(bird_rect):
            save_score(username, score)  # Save the score before game over
            game_state = GameState.GAME_OVER
            if score > best_score:
                best_score = score

        # Update and draw game elements
        update_score()
        move_bullets()
        check_bullet_enemy_collision()
        draw_bullets()
        draw_enemies()
        draw_bird(bird_x, bird_y)
        draw_pipes(pipes)
        display_score()
        display_level()

        # Check level progression
        if level < len(LEVEL_THRESHOLDS) and score >= LEVEL_THRESHOLDS[level - 1]:
            level += 1
            level_up_sound.play()  # Play level-up sound

        # Check if game is completed
        if score >= 100:
            save_score(username, score)  # Save the score before game completed
            game_state = GameState.GAME_COMPLETED

    elif game_state == GameState.GAME_COMPLETED:
        display_game_completed()

    elif game_state == GameState.GAME_OVER:
        display_game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
