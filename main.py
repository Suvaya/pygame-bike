import pygame
import sys
import cv2
import random

pygame.init()

# Set up display dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Bike Game")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
OBSTACLE_COLOR = (255, 92, 105)  # Green color for obstacles
# Track restart button state
restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)

restart_button_hovered = False

# Initialize clock
clock = pygame.time.Clock()
obstacle_speed = 0

# Load the car image and scale it down
car_image = pygame.image.load("assets/bike.png")
car_scale_factor = 0.5
car_width = int(car_image.get_width() * car_scale_factor)
car_height = int(car_image.get_height() * car_scale_factor)
car_image = pygame.transform.scale(car_image, (car_width, car_height))

# Set the initial position of the car at the bottom of the screen
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height

# Set the initial velocity of the car
car_x_velocity = 0

# Initialize OpenCV video capture
cap = cv2.VideoCapture('assets/Loop.mp4')

# Track game over state
game_over = False

# Track difficulty level selection
difficulty_selected = False
selected_difficulty = None

# Create a font for the "Game Over" message and restart button text
font_game_over = pygame.font.Font(None, 36)
font_restart = pygame.font.Font(None, 24)
font_score = pygame.font.Font(None, 24)
font_difficulty = pygame.font.Font(None, 36)

# Initialize the score counter and set the start time
score = 0
start_time = pygame.time.get_ticks()

# Initialize background audio
pygame.mixer.music.load("assets/background_music.mp3")
pygame.mixer.music.set_volume(0.5)  # Adjust the volume as needed
pygame.mixer.music.play(-1)  # Play the background music indefinitely
audio_playing = True

# Initialize obstacle constants
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
obstacles = []

# Define difficulty settings
easy_obstacle_frequency = 3  # Adjust as needed
hard_obstacle_frequency = 8  # Adjust as needed

easy_obstacle_speed = 5  # Adjust as needed
hard_obstacle_speed = 15  # Adjust as needed

# Define the menu screen
menu_button_easy_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
menu_button_hard_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

while not difficulty_selected:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if menu_button_easy_rect.collidepoint(event.pos):
                difficulty_selected = True
                selected_difficulty = "Easy"
            elif menu_button_hard_rect.collidepoint(event.pos):
                difficulty_selected = True
                selected_difficulty = "Hard"

    # Draw the menu screen
    screen.fill(BLACK)
    menu_text = font_difficulty.render("Select Difficulty:", True, WHITE)
    screen.blit(menu_text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
    pygame.draw.rect(screen, RED, menu_button_easy_rect)
    pygame.draw.rect(screen, RED, menu_button_hard_rect)
    menu_button_easy_text = font_difficulty.render("Easy", True, BLACK)
    menu_button_easy_text_rect = menu_button_easy_text.get_rect(center=menu_button_easy_rect.center)
    menu_button_hard_text = font_difficulty.render("Hard", True, BLACK)
    menu_button_hard_text_rect = menu_button_hard_text.get_rect(center=menu_button_hard_rect.center)
    screen.blit(menu_button_easy_text, menu_button_easy_text_rect)
    screen.blit(menu_button_hard_text, menu_button_hard_text_rect)

    pygame.display.flip()
    clock.tick(60)

# Game loop with selected difficulty
obstacle_frequency = easy_obstacle_frequency if selected_difficulty == "Easy" else hard_obstacle_frequency
obstacle_speed = easy_obstacle_speed if selected_difficulty == "Easy" else hard_obstacle_speed

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over and restart_button_rect.collidepoint(event.pos):
                # Restart the game when the restart button is clicked
                game_over = False
                car_x = WIDTH // 2 - car_width // 2
                car_x_velocity = 0
                score = 0
                start_time = pygame.time.get_ticks()
                audio_playing = True  # Set audio_playing to True to resume music
                pygame.mixer.music.play(-1)  # Restart the background music
                obstacles = []

    # Handle user input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        car_x_velocity = -5
    elif keys[pygame.K_RIGHT]:
        car_x_velocity = 5
    else:
        car_x_velocity = 0

    # Boundaries to keep the car within the screen
    if car_x > WIDTH:
        car_x = -car_width
    elif car_x < -car_width:
        car_x = WIDTH

    # Read a frame from the video
    ret, frame = cap.read()

    if not ret:
        # If the video ends, restart it
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Rotate the frame
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Convert the OpenCV frame to a Pygame surface
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
    screen.blit(frame, (0, 0))

    # Update the car's position
    car_x += car_x_velocity

    # Check for collisions between the car and obstacles
    if not game_over:
        car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
        for obstacle_x, obstacle_y in obstacles:
            obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
            if car_rect.colliderect(obstacle_rect):
                game_over = True
                if audio_playing:
                    pygame.mixer.music.stop()
                    audio_playing = False

    # Add new obstacles randomly
    if random.randint(0, 100) < obstacle_frequency:  # Adjust the number for obstacle frequency
        obstacle_x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
        obstacle_y = 100
        obstacles.append((obstacle_x, obstacle_y))

    # Move the obstacles down
    for i, (obstacle_x, obstacle_y) in enumerate(obstacles):
        obstacle_y += obstacle_speed  # Adjust the speed of obstacles
        obstacles[i] = (obstacle_x, obstacle_y)

        # Remove obstacles that are out of the screen
        if obstacle_y > HEIGHT:
            obstacles.pop(i)

    # Draw obstacles
    for (obstacle_x, obstacle_y) in obstacles:
        pygame.draw.rect(screen, OBSTACLE_COLOR, (obstacle_x, obstacle_y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    # Clear the screen with black when it's game over
    if game_over:
        screen.fill(BLACK)

        # Display "Game Over" message
        game_over_text = font_game_over.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 18))

        # Display final score
        final_score_text = font_score.render(f"Final Score: {score}", True, WHITE)
        screen.blit(final_score_text, (WIDTH // 2 - 120, HEIGHT // 12 + 50))

        # Create a rounded restart button
        restart_button_color = RED if restart_button_hovered else WHITE
        pygame.draw.ellipse(screen, restart_button_color, restart_button_rect)
        restart_text = font_restart.render("Restart", True, BLACK)
        text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_text, text_rect)

    # Only draw the car if it's not game over
    if not game_over:
        screen.blit(car_image, (car_x, car_y))

    # Update the score in milliseconds (counts as 100 per second)
    if not game_over:
        score = (pygame.time.get_ticks() - start_time) // 10

    # Display the score in the top-right corner (black color)
    score_text = font_score.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

    # Check if the mouse is hovering over the restart button
    mouse_x, mouse_y = pygame.mouse.get_pos()
    restart_button_hovered = restart_button_rect.collidepoint(mouse_x, mouse_y)
