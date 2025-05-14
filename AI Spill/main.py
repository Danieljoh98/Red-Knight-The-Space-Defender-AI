import pygame
import os
import random
import time

# Initialize Pygame and the mixer for sound
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

# Set the frame rate
FPS = 60
clock = pygame.time.Clock()

# Colors
WHITE = (234, 232, 231)
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 0, 0)
STAMINA_COLOR = (34, 139, 34)
RED = (255, 0, 0)
ALIEN_COUNTER_COLOR = (138, 228, 79)
BLACK_TRANSPARENT = (0, 0, 0, 65)  # Semi-transparent black
PINK = (255, 105, 180)

# Load images
BACKGROUND_IMAGE_PATH = os.path.join("background.png")
background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

BOSS_BACKGROUND_IMAGE_PATH = os.path.join("boss_background.png")
boss_background_image = pygame.image.load(BOSS_BACKGROUND_IMAGE_PATH)
boss_background_image = pygame.transform.scale(boss_background_image, (WIDTH, HEIGHT))

FINISH_SCREEN_PATH = os.path.join("finish_screen.png")
finish_screen_image = pygame.image.load(FINISH_SCREEN_PATH)
finish_screen_image = pygame.transform.scale(finish_screen_image, (WIDTH, HEIGHT))

GAME_OVER_SCREEN_PATH = os.path.join("game_over_screen.png")
game_over_screen_image = pygame.image.load(GAME_OVER_SCREEN_PATH)
game_over_screen_image = pygame.transform.scale(game_over_screen_image, (WIDTH, HEIGHT))

CHARACTER_IMAGE_PATH = os.path.join("character.png")
character_image = pygame.image.load(CHARACTER_IMAGE_PATH)
character_image = pygame.transform.scale(character_image, (106, 106))

LAVA_IMAGE_PATH = os.path.join("lava.png")
lava_image = pygame.image.load(LAVA_IMAGE_PATH)
lava_image = pygame.transform.scale(lava_image, (50, 50))
lava_image = pygame.transform.flip(lava_image, False, True)  # Flip the image upside down

HEART_IMAGE_PATH = os.path.join("heart.png")
heart_image = pygame.image.load(HEART_IMAGE_PATH)
heart_image = pygame.transform.scale(heart_image, (45, 45))

ENEMY_IMAGE_PATH = os.path.join("alien.png")
enemy_image = pygame.image.load(ENEMY_IMAGE_PATH)
enemy_image = pygame.transform.scale(enemy_image, (73, 73))

SWORD_IMAGE_PATH = os.path.join("sword.png")
sword_image = pygame.image.load(SWORD_IMAGE_PATH)
sword_image_right = pygame.transform.scale(sword_image, (91, 60))
sword_image_left = pygame.transform.flip(sword_image_right, True, False)

# Explosion image
BOOM_IMAGE_PATH = os.path.join("boom.png")
boom_image = pygame.image.load(BOOM_IMAGE_PATH)

# Load sounds
LAVA_SOUND_PATH = os.path.join("lava.mp3")
lava_sound = pygame.mixer.Sound(LAVA_SOUND_PATH)
pygame.mixer.Channel(0).play(lava_sound, loops=-1)

ALIEN_SOUND_PATH = os.path.join("alien.mp3")
alien_sound = pygame.mixer.Sound(ALIEN_SOUND_PATH)

HEART_SOUND_PATH = os.path.join("hearth.mp3")
hearth_sound = pygame.mixer.Sound(HEART_SOUND_PATH)

BOOM_SOUND_PATH = os.path.join("boom.mp3")
boom_sound = pygame.mixer.Sound(BOOM_SOUND_PATH)

SLASH_SOUND_PATH = os.path.join("slash.mp3")
slash_sound = pygame.mixer.Sound(SLASH_SOUND_PATH)

BOSS_SOUND_PATH = os.path.join("boss.mp3")
boss_sound = pygame.mixer.Sound(BOSS_SOUND_PATH)

BOSS_SOUND_PATH = os.path.join("victory.mp3")
victory_sound = pygame.mixer.Sound(BOSS_SOUND_PATH)

# Font setup for instruction text and game over text
font = pygame.font.Font(None, 20)
game_over_font = pygame.font.Font(None, 120)
counter_font = pygame.font.Font(None, 90)

# Game variables
game_over = False
player_vel_x = 0
player_vel_y = 0
gravity = 0.5
jump_power = -10
ground_level = HEIGHT - 50
jumps_remaining = 2
free_movement = False
speed_multiplier = 1
facing_right = True

# Life counter
lives = 3

# Explosion duration in milliseconds
EXPLOSION_DURATION = 50

# Attack mechanics
attack_duration = 30
attack_cooldown = 30
attack_timer = 0
attack_state = "ready"
attack_hitbox = None

# Stamina bar (larger)
stamina_max = 100
stamina = stamina_max
stamina_bar_width = 150
stamina_bar_height = 15

# Alien counter for tracking aliens destroyed
alien_counter = 32

# Flag to indicate if platforms should be drawn
platforms_visible = True
boss_mode = False  # New flag to track if in boss mode

# Enemy speed
enemy_speed = 5

pygame.init()

# Screen and font setup
WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
boss_font = pygame.font.Font(None, 44)  # Adjust font size as needed

# Set alien_counter to 32 to display "ALIEN BOSS" text
alien_counter = 32  # Ensure alien_counter is 32 when you want the text to appear

# Fill background with white (only needed in a loop or main display function)
screen.fill((255, 255, 255))

# Check if alien counter is 32 to display the "GAME BACKSTORY" text
if alien_counter == 32:
    # Backstory texts
    backstory_lines = [
        "",
        "RED KNIGTH THE SPACE DEFENDER",
        "",
        "",
        "In a realm where ancient legends blend with futuristic realms,",
        "the Red Knight stands as the last sentinel of a forgotten order.",
        "For centuries, his duty was to guard the mountain pass leading to the uncharted realms beyond.",
        "When an intergalactic empire discovered the pass, they saw an opportunity to conquer and exploit.",
        "Waves of alien invaders poured in, intent on claiming his world.",
        "Alone but unwavering, the Red Knight dons his armor one last time,",
        "wielding his ancient blade against advanced alien forces.",
        "Driven by honor, he fights not only to protect his homeland",
        "but to preserve the legacy of his order, the last defense against the endless dark.",
        "",
        "YOU CAN MOVE WITH THE ARROW KEYS AND ATTACK WITH SPACE",
    ]
    outline_color = (0, 0, 0)  # Black color for the outline
    text_color = (255, 0, 0)   # Red color for the main text
    y_offset = 20  # Starting y-position for the first line

    # Iterate through each line of text and render it
    for line in backstory_lines:
        # Render the outline in black, shifting in all directions
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_text = boss_font.render(line, True, outline_color)
            screen.blit(outline_text, (WIDTH // 2 - outline_text.get_width() // 2 + dx, y_offset + dy))

        # Render the main red text on top
        main_text = boss_font.render(line, True, text_color)
        screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2, y_offset))

        # Increase y_offset to position the next line below
        y_offset += 60

# Update the display to show the rendered text
pygame.display.flip()

# Simple wait to view result (remove or modify for use in a loop)
pygame.time.wait(33000)  # Wait 10 seconds to see the text before quitting

# Platform height pattern
platform_heights = [2, 2, 3, 1, 2, 3, 4, 5, 3, 4, 5, 6, 7, 3, 4, 5, 6, 1, 2, 3, 4, 5, 2, 3, 4, 5, 5, 6, 7, 5, 3, 1, 2, 3, 4, 4, 5, 5, 6, 5, 4, 4, 5, 6, 4, 4, 5, 4, 5, 4, 5, 6, 5, 6, 7, 8, 8, 8, 2, 3, 3, 1, 1]
platforms = []
platform_x = 100
horizontal_spacing = 400

for height in platform_heights:
    platforms.append(pygame.Rect(platform_x, HEIGHT - (height * 100), 200, 20))
    platform_x += horizontal_spacing

# Player setup
player_pos = pygame.Rect(platforms[0].x, platforms[0].y - 106, 106, 106)

# Updated binary pattern for alien placement
alien_pattern = "0001101011111101010111011110100000110100101111001001000100100111"

enemies = []
for i in range(1, len(platforms)):
    if i - 1 < len(alien_pattern) and alien_pattern[i - 1] == '1':
        platform = platforms[i]
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-10, 10)
        enemy_rect = pygame.Rect(platform.x + 10000 + offset_x, platform.y - 73 + offset_y, 73, 73)
        enemies.append({
            "rect": enemy_rect,
            "direction": 1,
            "base_y": enemy_rect.y - 100,
            "platform_y": enemy_rect.y + 73,
            "is_exploding": False,
            "explosion_start_time": None
        })

# Overlay for background transparency
overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((255, 255, 255, 76))

# Boss platforms placeholder
boss_platforms = []

# Boss phase flag and boss background setup
boss_phase = False
flash_start_time = None  # Start time for flashing effect
flash_duration = 2  # Duration for flashing effect in seconds
flash_interval = 0.2  # Interval for each flash in seconds
boss_background_image = pygame.image.load("boss_background.png")
boss_background_image = pygame.transform.scale(boss_background_image, (WIDTH, HEIGHT))

# Load boss music
BOSS_MUSIC_PATH = os.path.join("boss.mp3")
boss_music = pygame.mixer.Sound(BOSS_MUSIC_PATH)

# Track previous lives to check if lives decrease
previous_lives = lives

# Initialize boss variables
boss_image_path = os.path.join("boss.png")
boss_image = pygame.image.load(boss_image_path)
boss_image = pygame.transform.scale(boss_image, (400, 400))
boss_spawn_time = 0  # Track when boss spawns
boss_active = False
boss_rect = pygame.Rect(WIDTH - 400, 100, 400, 400)  # Boss positioned on the right side
boss_direction = 1  # 1 for moving down, -1 for moving up
boss_health = 10  # Boss health with 10 sections

import pygame
import os
import random
import time

# Initialize Pygame and the mixer for sound
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

# Set the frame rate
FPS = 60
clock = pygame.time.Clock()

# Colors
WHITE = (234, 232, 231)
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 0, 0)
STAMINA_COLOR = (34, 139, 34)
RED = (255, 0, 0)
PINK = (255, 192, 203)
ALIEN_COUNTER_COLOR = (138, 228, 79)
BLACK_TRANSPARENT = (0, 0, 0, 65)  # Semi-transparent black

# Load images
BACKGROUND_IMAGE_PATH = os.path.join("background.png")
background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

BOSS_BACKGROUND_IMAGE_PATH = os.path.join("boss_background.png")
boss_background_image = pygame.image.load(BOSS_BACKGROUND_IMAGE_PATH)
boss_background_image = pygame.transform.scale(boss_background_image, (WIDTH, HEIGHT))

CHARACTER_IMAGE_PATH = os.path.join("character.png")
character_image = pygame.image.load(CHARACTER_IMAGE_PATH)
character_image = pygame.transform.scale(character_image, (106, 106))

LAVA_IMAGE_PATH = os.path.join("lava.png")
lava_image = pygame.image.load(LAVA_IMAGE_PATH)
lava_image = pygame.transform.scale(lava_image, (50, 50))
lava_image = pygame.transform.flip(lava_image, False, True)  # Flip the image upside down

HEART_IMAGE_PATH = os.path.join("heart.png")
heart_image = pygame.image.load(HEART_IMAGE_PATH)
heart_image = pygame.transform.scale(heart_image, (45, 45))

ENEMY_IMAGE_PATH = os.path.join("alien.png")
enemy_image = pygame.image.load(ENEMY_IMAGE_PATH)
enemy_image = pygame.transform.scale(enemy_image, (73, 73))

SWORD_IMAGE_PATH = os.path.join("sword.png")
sword_image = pygame.image.load(SWORD_IMAGE_PATH)
sword_image_right = pygame.transform.scale(sword_image, (91, 60))
sword_image_left = pygame.transform.flip(sword_image_right, True, False)

BOOM_IMAGE_PATH = os.path.join("boom.png")
boom_image = pygame.image.load(BOOM_IMAGE_PATH)

BOSS_IMAGE_PATH = os.path.join("boss.png")
boss_image = pygame.image.load(BOSS_IMAGE_PATH)
boss_image = pygame.transform.scale(boss_image, (400, 400))

# Load sounds
LAVA_SOUND_PATH = os.path.join("lava.mp3")
lava_sound = pygame.mixer.Sound(LAVA_SOUND_PATH)
pygame.mixer.Channel(0).play(lava_sound, loops=-1)

ALIEN_SOUND_PATH = os.path.join("alien.mp3")
alien_sound = pygame.mixer.Sound(ALIEN_SOUND_PATH)

HEART_SOUND_PATH = os.path.join("hearth.mp3")
hearth_sound = pygame.mixer.Sound(HEART_SOUND_PATH)

BOOM_SOUND_PATH = os.path.join("boom.mp3")
boom_sound = pygame.mixer.Sound(BOOM_SOUND_PATH)

SLASH_SOUND_PATH = os.path.join("slash.mp3")
slash_sound = pygame.mixer.Sound(SLASH_SOUND_PATH)

BOSS_SOUND_PATH = os.path.join("boss.mp3")
boss_music = pygame.mixer.Sound(BOSS_SOUND_PATH)

# Fonts
font = pygame.font.Font(None, 20)
game_over_font = pygame.font.Font(None, 120)
counter_font = pygame.font.Font(None, 90)
boss_font = pygame.font.Font(None, 100)

# Game variables
game_over = False
player_vel_x = 0
player_vel_y = 0
gravity = 0.5
jump_power = -10
ground_level = HEIGHT - 50
jumps_remaining = 2
free_movement = False
speed_multiplier = 1
facing_right = True

# Life counter
lives = 3

# Explosion duration in milliseconds
EXPLOSION_DURATION = 100

# Attack mechanics
attack_duration = 30
attack_cooldown = 30
attack_timer = 0
attack_state = "ready"
attack_hitbox = None

# Stamina bar (larger)
stamina_max = 100
stamina = stamina_max
stamina_bar_width = 150
stamina_bar_height = 15

# Alien counter for tracking aliens destroyed
alien_counter = 32

# Flags
platforms_visible = True
boss_mode = False

# Enemy speed
enemy_speed = 4

# Platform pattern
platform_heights = [2, 2, 3, 1, 2, 3, 4, 5, 3, 4, 5, 6, 7, 3, 4, 5, 6, 1, 2, 3, 4, 5, 2, 3, 4, 5, 5, 6, 7, 5, 3, 1, 2, 3, 4, 4, 5, 5, 6, 5, 4, 4, 5, 6, 4, 4, 5, 4, 5, 4, 5, 6, 5, 6, 7, 8, 8, 8, 2, 3, 3, 1, 1]
platforms = []
platform_x = 100
horizontal_spacing = 400

for height in platform_heights:
    platforms.append(pygame.Rect(platform_x, HEIGHT - (height * 100), 200, 20))
    platform_x += horizontal_spacing

# Player setup
player_pos = pygame.Rect(platforms[0].x, platforms[0].y - 106, 106, 106)

# Enemy setup based on binary pattern
alien_pattern = "0001101011111101010111011110100000110100101111001001000100100111"
enemies = []
for i in range(1, len(platforms)):
    if i - 1 < len(alien_pattern) and alien_pattern[i - 1] == '1':
        platform = platforms[i]
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-10, 10)
        enemy_rect = pygame.Rect(platform.x + 80 + offset_x, platform.y - 80 + offset_y, 73, 73)
        enemies.append({
            "rect": enemy_rect,
            "direction": 1,
            "base_y": enemy_rect.y - 100,
            "platform_y": enemy_rect.y + 73,
            "is_exploding": False,
            "explosion_start_time": None
        })

# Overlay for background transparency
overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((255, 255, 255, 76))

# Boss variables
boss_active = False
boss_phase = False
boss_phase_start_time = None
boss_health = 10
boss_flash_duration = 2  # Flash duration for 2 seconds before boss appears
boss_flash_interval = 0.2  # Flashing interval
boss_position_y = 100  # Starting y-position of the boss
boss_direction = 1
boss_speed = 2

# Game loop
running = True
boss_phase_start_time = None
boss_flash_duration = 2  # Total flash duration for 2 seconds
boss_flash_interval = 0.2  # Interval for black and white flashes
boss_flash_end_time = None  # Track when the flashing ends
boss_health = 10
boss_direction = 1
boss_speed = 2
boss_position_y = 100
boss_active = False
boss_minion_spawn_time = None  # Initialize as None
max_boss_minions = 250
boss_minions_spawned = 0
total_spawn_duration = 10 * 60  # 10 minutes in seconds
spawn_interval = total_spawn_duration / max_boss_minions  # Calculate the interval to evenly spawn 250 minions over 10 minutes
last_minion_spawn_time = 0
lost_life_for_boss_mode = False  # Track if life was lost for entering boss mode
respawn_time = None  # Track when the player last lost a life
protection_circle_start_time = None  # Track when the protective circle starts
protection_duration = 1  # 1-second protection after respawn
falling_through = False  # Variable to track if player is falling through platforms

# Define the flag to track if the lava collision happened during boss mode
boss_mode_lava_triggered = False

# In the game loop:
if alien_counter <= 0 and not boss_phase_start_time:
    boss_phase_start_time = time.time()
    boss_flash_end_time = boss_phase_start_time + boss_flash_duration
    boss_phase = True  # Enter boss phase
    alien_counter += 10  # Add 10 to the alien counter when entering boss mode
    platforms_visible = False  # Hide normal platforms
    boss_platforms = []  # Create boss platforms
    for i in range(10):
        boss_platform_y = HEIGHT - (i * 160 + 100)
        boss_platform_rect = pygame.Rect(-50000, boss_platform_y, 99999, 20)
        gaps = random.sample(range(0, 99999, 1000), 100)
        boss_platforms.append({"rect": boss_platform_rect, "gaps": gaps})
    pygame.mixer.Channel(1).play(boss_music, loops=-1)  # Start boss music in a loop

    # Execute the player position reset and sound action once when boss mode activates
    if not boss_mode_activated:
        pygame.mixer.Channel(1).play(hearth_sound)
        player_pos.x = platforms[0].x
        player_pos.y = platforms[0].y - player_pos.height
        player_vel_y = 0
        boss_mode_activated = True  # Ensure this action only occurs once during boss mode

# Set boss_rect to the position from where aliens should start spawning during boss mode
boss_rect = pygame.Rect(WIDTH, 100, 400, 400)  # Positioned off-screen on the right side

while running:
    clock.tick(FPS)

    # Event handling for quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check if alien counter hits 0 to start boss phase
    if alien_counter <= 0 and not boss_phase_start_time:
        boss_phase_start_time = time.time()
        boss_flash_end_time = boss_phase_start_time + boss_flash_duration
        boss_phase = True  # Enter boss phase
        alien_counter += 10  # Add 10 to the alien counter when entering boss mode
        platforms_visible = False  # Hide normal platforms
        boss_platforms = []  # Create boss platforms
        for i in range(10):
            boss_platform_y = HEIGHT - (i * 160 + 100)
            boss_platform_rect = pygame.Rect(-50000, boss_platform_y, 99999, 20)
            gaps = random.sample(range(0, 99999, 1000), 0)
            boss_platforms.append({"rect": boss_platform_rect, "gaps": gaps})
        pygame.mixer.Channel(1).play(boss_music, loops=-1)  # Start boss music in a loop

        # Lose and regain a life when boss mode starts, without playing the heart sound
        if not lost_life_for_boss_mode:
            lives -= 1
            pygame.time.delay(500)  # Delay of 500 milliseconds (0.5 seconds)
            lives += 1
            lost_life_for_boss_mode = True

    # Flashing effect before switching to boss background
    if boss_phase and boss_flash_end_time and time.time() < boss_flash_end_time:
        # Alternate between black and white screens every 0.2 seconds
        if int((time.time() - boss_phase_start_time) // boss_flash_interval) % 2 == 0:
            screen.fill(WHITE)
        else:
            screen.fill(BLACK)
    elif boss_phase:  # Switch to boss background after flashing
        screen.blit(boss_background_image, (0, 0))

        # Boss movement and activation logic
        if not boss_active:
            boss_active = True  # Activate boss, prevents multiple spawns

        # Boss movement up and down within bounds
        boss_position_y += boss_speed * boss_direction
        if boss_position_y <= 100 or boss_position_y >= HEIGHT - boss_image.get_height():
            boss_direction *= -1  # Reverse direction at bounds

        # Update the boss's position for spawning aliens
        boss_rect.y = boss_position_y

        # Draw boss on the right side of the screen
        screen.blit(boss_image, (WIDTH - boss_image.get_width(), boss_position_y))

        # Draw the boss health bar 50 pixels higher (at 750 pixels from the top)
        health_bar_y = boss_position_y - 30
        health_bar_width = 35
        health_bar_spacing = 40

        # Draw each health section in pink for remaining health
        for i in range(boss_health):
            pygame.draw.rect(screen, PINK, (WIDTH - boss_image.get_width() - 10 + i * health_bar_spacing, health_bar_y, health_bar_width, 20))

        # Draw each depleted health section in red
        for i in range(10 - boss_health):
            x_position = WIDTH - boss_image.get_width() - 10 + (boss_health + i) * health_bar_spacing
            pygame.draw.rect(screen, RED, (x_position, health_bar_y, health_bar_width, 20))

        # Draw "ALIEN BOSS" text centered at the top of the screen
        alien_text = boss_font.render("ALIEN BOSS", True, PINK)
        alien_text_outline = boss_font.render("ALIEN BOSS", True, WHITE)
        screen.blit(alien_text_outline, (WIDTH // 2 - alien_text_outline.get_width() // 2 - 4, 20))  # Outline
        screen.blit(alien_text, (WIDTH // 2 - alien_text.get_width() // 2, 24))  # Main text

        # Boss Minion Spawning Logic - Spawning during boss phase at regular intervals
        current_time = time.time()
        time_since_boss_appeared = current_time - boss_phase_start_time

        # Only spawn minions if at least 1 second has passed since losing a heart
        if boss_phase and boss_minions_spawned < max_boss_minions and (respawn_time is None or (current_time - respawn_time >= 1)) and time_since_boss_appeared >= spawn_interval:
            if current_time - last_minion_spawn_time >= spawn_interval:
                # Spawn a minion from the right side of the screen (beyond visible area)
                minion_rect = pygame.Rect(WIDTH + 3000, boss_rect.y + boss_rect.height // 2, 73, 73)
                enemies.append({
                    "rect": minion_rect,
                    "direction": -1,  # Move to the left
                    "speed": enemy_speed * 10,  # Two times as fast as normal enemies
                    "is_exploding": False,
                    "explosion_start_time": None,
                    "spawned_by_boss": True
                })
                last_minion_spawn_time = current_time
                boss_minions_spawned += 1

    else:
        screen.blit(background_image, (0, 0))  # Regular background

    # Player movement, gravity, and attacks code
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_vel_x = -5 * speed_multiplier
        facing_right = False
    elif keys[pygame.K_RIGHT]:
        player_vel_x = 5 * speed_multiplier
        facing_right = True
    else:
        player_vel_x = 0

    if keys[pygame.K_UP] and on_ground:  # Allow jump only if on ground
        player_vel_y = jump_power
        on_ground = False

    # Allow player to fall through platforms if the down key is pressed
    if keys[pygame.K_DOWN]:
        falling_through = True
    else:
        falling_through = False

    if not free_movement:
        player_vel_y += gravity

    player_pos.x += player_vel_x
    player_pos.y += player_vel_y

    # Ensure character does not respawn on top of an alien
    if player_pos.y > HEIGHT or player_pos.collidelist([enemy["rect"] for enemy in enemies if not enemy["is_exploding"]]) != -1:
        lives -= 1
        if lives > 0:
            player_pos.x = platforms[0].x
            player_pos.y = platforms[0].y - player_pos.height
            player_vel_y = 0
            if boss_mode:  # Clear all enemies only if boss mode is active
                enemies.clear()
            respawn_time = time.time()  # Set the respawn time to enforce a delay before spawning enemies again
            protection_circle_start_time = respawn_time  # Start the protective circle

        else:
            running = False

    # Draw the protective circle around the character after respawn
    if protection_circle_start_time is not None:
        elapsed_protection_time = time.time() - protection_circle_start_time
        if elapsed_protection_time <= protection_duration:
            # Draw the red protective circle
            protective_circle_center = (player_pos.x + player_pos.width // 2 - camera_x_offset, player_pos.y + player_pos.height // 2)
            pygame.draw.circle(screen, RED, protective_circle_center, 200, 3)  # Draw with a radius of 200 pixels (1000x1000 diameter)

            # Remove enemies that enter the protective circle
            for enemy in enemies[:]:
                enemy_center = (enemy["rect"].x + enemy["rect"].width // 2, enemy["rect"].y + enemy["rect"].height // 2)
                distance = ((enemy_center[0] - player_pos.x) ** 2 + (enemy_center[1] - player_pos.y) ** 2) ** 0.5
                if distance <= 200:  # If the enemy is within the protective circle
                    enemies.remove(enemy)
        else:
            protection_circle_start_time = None  # End protection after the duration expires

    # Define camera offset
    camera_x_offset = player_pos.x - 100  # Keep player at 100 pixels from the left

    # Draw the lava if not in boss phase
    lava_hitbox = pygame.Rect(-9999999, ground_level, 99999999, 50)
    if not boss_phase:
        for i in range((WIDTH // 50) + 2):
            lava_x = (i * 50) - (camera_x_offset % 50)
            screen.blit(lava_image, (lava_x, ground_level))
    
    if player_pos.colliderect(lava_hitbox):
        lives -= 1
        pygame.mixer.Channel(1).play(hearth_sound)
        player_pos.x = platforms[0].x
        player_pos.y = platforms[0].y - player_pos.height
        player_vel_y = 0
        if boss_mode:  # Clear all enemies only if boss mode is active
            enemies.clear()

    # Platform collision detection
    on_ground = False
    if platforms_visible:
        for platform in platforms:
            if player_pos.colliderect(platform) and player_vel_y > 0 and not falling_through:
                player_pos.y = platform.y - player_pos.height
                player_vel_y = 0
                on_ground = True
                jumps_remaining = 2

    if boss_phase:
        for boss_platform in boss_platforms:
            boss_platform_rect = boss_platform["rect"]
            if player_pos.colliderect(boss_platform_rect) and player_vel_y > 0 and not falling_through:
                player_pos.y = boss_platform_rect.y - player_pos.height
                player_vel_y = 0
                on_ground = True
                jumps_remaining = 2

    # Handle attacks
    if keys[pygame.K_SPACE] and attack_state == "ready" and stamina == stamina_max:
        attack_state = "active"
        attack_timer = attack_duration
        stamina = 0
        pygame.mixer.Channel(3).play(slash_sound)

    if attack_state == "active":
        sword_image_to_use = sword_image_right if facing_right else sword_image_left
        attack_offset_x = 86 if facing_right else -50
        attack_hitbox = pygame.Rect(player_pos.x + attack_offset_x, player_pos.y + 25,
                                    sword_image_to_use.get_width(), sword_image_to_use.get_height())
        screen.blit(sword_image_to_use, attack_hitbox.move(-camera_x_offset, 0))
        attack_timer -= 1
        if attack_timer <= 0:
            attack_state = "cooldown"
            attack_timer = attack_cooldown

    elif attack_state == "cooldown":
        attack_timer -= 1
        stamina += stamina_max / attack_cooldown
        if stamina >= stamina_max:
            stamina = stamina_max
            attack_state = "ready"
            attack_hitbox = None

    # Enemy handling
    for enemy in enemies[:]:
        if abs(enemy["rect"].x - player_pos.x) < 200 and not enemy.get("sound_played", False):
            pygame.mixer.Channel(2).play(alien_sound)
            enemy["sound_played"] = True

        if attack_hitbox and attack_hitbox.colliderect(enemy["rect"]):
            enemy["is_exploding"] = True
            enemy["explosion_start_time"] = pygame.time.get_ticks()
            pygame.mixer.Channel(6).play(boom_sound)

        if player_pos.colliderect(enemy["rect"]) and not enemy["is_exploding"]:
            lives -= 1
            pygame.mixer.Channel(1).play(hearth_sound)
            player_pos.x = platforms[0].x
            player_pos.y = platforms[0].y - player_pos.height
            player_vel_y = 0
            if boss_mode:  # Clear all enemies only if boss mode is active
                enemies.clear()
            break

    for enemy in enemies[:]:
        if enemy["is_exploding"]:
            if pygame.time.get_ticks() - enemy["explosion_start_time"] > EXPLOSION_DURATION:
                enemies.remove(enemy)
                alien_counter -= 1
                if boss_phase and boss_health > 0:
                    boss_health -= 1

        else:
            if not enemy.get("spawned_by_boss", False):
                # Move the regular aliens up and down
                enemy["rect"].y += enemy["direction"] * enemy_speed
                if enemy["rect"].y >= enemy["platform_y"] - 40:
                    enemy["direction"] = -1
                elif enemy["rect"].y <= enemy["base_y"] - 100:
                    enemy["direction"] = 1
            else:
                # Boss-spawned aliens only move horizontally
                enemy["rect"].x += enemy["direction"] * enemy["speed"]

    # Draw platforms and other elements
    if platforms_visible:
        for platform in platforms:
            platform_rect = platform.move(-camera_x_offset, 0)
            pygame.draw.rect(screen, BLACK, platform_rect)

    if boss_phase:
        for boss_platform in boss_platforms:
            platform_rect = boss_platform["rect"].move(-camera_x_offset, 0)
            boss_surface = pygame.Surface((boss_platform["rect"].width, boss_platform["rect"].height), pygame.SRCALPHA)
            boss_surface.fill(BLACK_TRANSPARENT)
            for gap in boss_platform["gaps"]:
                pygame.draw.rect(boss_surface, (0, 0, 0, 0), (gap, 0, 100, boss_platform["rect"].height))
            screen.blit(boss_surface, platform_rect.topleft)

    # Draw player
    character_display = pygame.transform.flip(character_image, not facing_right, False)
    screen.blit(character_display, player_pos.move(-camera_x_offset, 0))

    # Draw enemies
    for enemy in enemies:
        if enemy["is_exploding"]:
            screen.blit(pygame.transform.scale(boom_image, enemy_image.get_size()), enemy["rect"].move(-camera_x_offset, 0))
        else:
            screen.blit(enemy_image, enemy["rect"].move(-camera_x_offset, 0))

    # Draw lives and stamina
    for i in range(lives):
        screen.blit(heart_image, (10 + i * 50, 10))

    stamina_ratio = stamina / stamina_max
    stamina_bar_length = int(stamina_bar_width * stamina_ratio)
    pygame.draw.rect(screen, STAMINA_COLOR, (10, 70, stamina_bar_length, stamina_bar_height))
    pygame.draw.rect(screen, BLACK, (10, 70, stamina_bar_width, stamina_bar_height), 2)

    # Draw alien counter with thicker black outline
    alien_counter_color = PINK if boss_phase else ALIEN_COUNTER_COLOR
    alien_counter_text_outline = counter_font.render(str(alien_counter), True, BLACK)
    alien_counter_text = counter_font.render(str(alien_counter), True, alien_counter_color)
    counter_x, counter_y = WIDTH - 120, 30
    # Draw outline multiple times to make it thicker
    for offset in [-3, -2, -1, 0, 1, 2, 3]:
        screen.blit(alien_counter_text_outline, (counter_x + offset, counter_y + offset))
    screen.blit(alien_counter_text, (counter_x, counter_y))
    alien_icon = pygame.transform.scale(enemy_image, (50, 50))
    screen.blit(alien_icon, (counter_x - 60, counter_y))

    # Game Over / Win logic
    if lives <= 0:
        # Display the game over screen for 7 seconds
        screen.blit(game_over_screen_image, (0, 0))
        pygame.mixer.Channel(0).stop()  # Stop boss music if still playing
        if not pygame.mixer.Channel(1).get_busy():  # Only play if not already playing
            pygame.mixer.Channel(1).play(hearth_sound)  # Play the game over sound once
        pygame.display.flip()
        pygame.time.delay(7000)  # Wait for 7 seconds
        running = False  # Automatically quit after 7 seconds
    
    if alien_counter == -1:
        # Added Victory Boom Effect Sequence
        # Display multiple boom.png images and play boom.mp3 5 times over 5 seconds before the "YOU WON" screen
        for i in range(5):  # Play boom sound 5 times
            pygame.mixer.Channel(4).play(boom_sound)
            
            # Display Boom images randomly on screen
            boom_positions = []
            for _ in range(30):  # 30 Boom images to display
                boom_x = random.randint(0, WIDTH - boom_image.get_width())
                boom_y = random.randint(0, HEIGHT - boom_image.get_height())
                boom_positions.append((boom_x, boom_y))
            
            # Draw the booms on screen
            screen.fill(BLACK)  # Fill the screen with black to emphasize booms
            for boom_x, boom_y in boom_positions:
                screen.blit(boom_image, (boom_x, boom_y))
            
            pygame.display.flip()
            pygame.time.delay(1000)  # Delay 1 second for each iteration

        # Set background to white before the finish screen
        screen.fill(WHITE)
        pygame.display.flip()

        # Display the finish screen for 7 seconds
        screen.blit(finish_screen_image, (0, 0))
        pygame.mixer.Channel(1).stop()  # Stop boss music if still playing
        pygame.mixer.Channel(2).play(victory_sound)  # Play the victory sound once
        pygame.display.flip()
        pygame.display.flip()
        pygame.time.delay(7000)

        running = False

    # Update display
    pygame.display.flip()

pygame.mixer.stop()
pygame.quit()
