import pygame
import os
import random
import time
import cv2
import numpy as np
import math  # Added for fire effect calculations

# Initialize Pygame and the mixer for sound
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Set up the display
WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Knight: Space Defender")

# Set the frame rate
FPS = 60
clock = pygame.time.Clock()

# Colors
WHITE = (234, 232, 231)
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 0, 0)
STAMINA_COLOR = (34, 139, 34)
RED = (255, 0, 0)
PINK = (255, 105, 180)
ALIEN_COUNTER_COLOR = (138, 228, 79)
BLACK_TRANSPARENT = (0, 0, 0, 65)

# Game state variables
game_state = "story"  # "story", "story_playing", "playing", "game_over", "victory"
story_start_time = time.time()
story_timer = 0
game_over = False
running = True
cheat_message = ""
cheat_message_timer = 0

# Alien enraged system
aliens_enraged = False
enraged_flash_start = None
enraged_message_timer = 0
first_enhanced_alien_seen = False

# Player variables
player_vel_x = 0
player_vel_y = 0
gravity = 0.6  # Increased from 0.5 to make jumping quicker (faster fall)
jump_power = -12  # Back to original height (was -15, now -12)
ground_level = HEIGHT - 50
on_ground = False
facing_right = True
speed_multiplier = 1
fly_mode = False  # New fly mode toggle

# Life system
lives = 3
max_lives = 3

# Explosion and attack system
EXPLOSION_DURATION = 500  # milliseconds
attack_duration = 18  # Made 10% quicker (was 20, now 18)
attack_cooldown = 30
attack_timer = 0
attack_state = "ready"
attack_hitbox = None
attack_progress = 0.0  # Track slash progress from 0.0 to 1.0

# Stamina system
stamina_max = 100
stamina = stamina_max
stamina_bar_width = 150
stamina_bar_height = 15
stamina_regen_rate = 2.5

# Boss system
alien_counter = 32
boss_phase = False
boss_active = False
boss_health = 10
boss_max_health = 10
boss_position_y = 100
boss_direction = 1
boss_speed = 2
boss_phase_start_time = None
boss_flash_duration = 2
boss_flash_interval = 0.2

# Knight fire effect when entering boss mode
knight_fire_effect = False
knight_fire_start_time = None
knight_fire_duration = 1.5  # 1.5 seconds of fire effect
knight_fire_flash_count = 0
knight_fire_flash_interval = 0.25  # Flash every 0.25 seconds (4 flashes in 1 second)

# Protection system after respawn
protection_start_time = None
protection_duration = 2.0  # 2 seconds of protection
protection_active = False

# Camera system
camera_x_offset = 0

# Sound system
sound_channels = {
    'lava': 0,
    'sfx': 1,
    'alien': 2,
    'attack': 3,
    'explosion': 4,
    'boss_music': 5,
    'ambient': 6
}

# Load and initialize images safely
def load_image(path, size=None, flip_x=False, flip_y=False):
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        if flip_x or flip_y:
            image = pygame.transform.flip(image, flip_x, flip_y)
        return image
    except pygame.error as e:
        print(f"Could not load image {path}: {e}")
        # Create a placeholder colored rectangle
        if size:
            placeholder = pygame.Surface(size)
            placeholder.fill((255, 0, 255))  # Magenta placeholder
            return placeholder
        return pygame.Surface((50, 50))

# Load and initialize sounds safely
def load_sound(path, volume=1.0):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except pygame.error as e:
        print(f"Could not load sound {path}: {e}")
        return None

# Load all images
background_image = load_image("background.png", (WIDTH, HEIGHT))
boss_background_image = load_image("boss_background.png", (WIDTH, HEIGHT))
finish_screen_image = load_image("win_screen.png", (WIDTH, HEIGHT))
game_over_screen_image = load_image("game_over_screen.png", (WIDTH, HEIGHT))
character_image = load_image("character.png", (106, 106))
lava_image = load_image("lava.png", (50, 50), flip_y=True)
heart_image = load_image("heart.png", (45, 45))
enemy_image = load_image("alien.png", (73, 73))
sword_image = load_image("sword.png", (100, 66))  # 10% bigger (91x60 -> 100x66)
sword_image_right = sword_image
sword_image_left = pygame.transform.flip(sword_image_right, True, False)
boom_image = load_image("boom.png", (73, 73))
boss_image = load_image("boss.png", (400, 400))

# Load all sounds
lava_sound = load_sound("lava.mp3", 0.3)
alien_sound = load_sound("alien.mp3", 0.7)
hearth_sound = load_sound("hearth.mp3", 0.8)
boom_sound = load_sound("boom.mp3", 0.6)
slash_sound = load_sound("slash.mp3", 0.5)
boss_music = load_sound("boss.mp3", 0.4)
victory_sound = load_sound("victory.mp3", 0.8)

# Font setup
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 120)
counter_font = pygame.font.Font(None, 90)
boss_font = pygame.font.Font(None, 44)
story_font = pygame.font.Font(None, 36)

# Platform setup
platform_heights = [2, 2, 3, 1, 2, 3, 4, 5, 3, 4, 5, 6, 7, 3, 4, 5, 6, 1, 2, 3, 4, 5, 2, 3, 4, 5, 5, 6, 7, 5, 3, 1, 2, 3, 4, 4, 5, 5, 6, 5, 4, 4, 5, 6, 4, 4, 5, 4, 5, 4, 5, 6, 5, 6, 7, 8, 8, 8, 2, 3, 3, 1, 1]
platforms = []
platform_x = 100
horizontal_spacing = 400

for height in platform_heights:
    platforms.append(pygame.Rect(platform_x, HEIGHT - (height * 100), 200, 20))
    platform_x += horizontal_spacing

# Player setup - Start properly positioned on first platform
player_pos = pygame.Rect(platforms[0].x, platforms[0].y - 106, 106, 106)
on_ground = True  # Start on ground to prevent initial falling

# Enemy setup
alien_pattern = "0001101011111101010111011110100000110100101111001001000100100111"
enemies = []
explosions = []

def create_enemies():
    global enemies
    enemies.clear()
    enemy_count = 0
    for i in range(1, min(len(platforms), len(alien_pattern) + 1)):
        if alien_pattern[i - 1] == '1':
            platform = platforms[i]
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-10, 10)
            enemy_rect = pygame.Rect(platform.x + 80 + offset_x, platform.y - 80 + offset_y, 73, 73)
            
            # Count enemies to make last 10 special, BUT only if alien_counter is 10 or less
            enemy_count += 1
            total_enemies = alien_pattern.count('1')
            is_last_10 = enemy_count > (total_enemies - 10) and alien_counter <= 10
            
            enemies.append({
                "rect": enemy_rect,
                "direction": 1,
                "base_y": enemy_rect.y - 100,
                "platform_y": enemy_rect.y + 73,
                "speed": 2 if is_last_10 else 2,  # Same speed as normal aliens (slowed down)
                "sound_played": False,
                "spawned_by_boss": False,
                "is_special": is_last_10  # Mark special enemies only when alien_counter <= 10
            })

create_enemies()

# Boss platform setup
boss_platforms = []

def create_boss_platforms():
    global boss_platforms
    boss_platforms.clear()
    for i in range(10):
        boss_platform_y = HEIGHT - (i * 160 + 100)
        boss_platform_rect = pygame.Rect(-50000, boss_platform_y, 99999, 20)
        boss_platforms.append({"rect": boss_platform_rect})

def play_sound(sound, channel_name, loops=0):
    """Safely play a sound on a specific channel"""
    if sound and channel_name in sound_channels:
        try:
            pygame.mixer.Channel(sound_channels[channel_name]).play(sound, loops)
        except pygame.error:
            pass

def stop_sound(channel_name):
    """Stop sound on a specific channel"""
    if channel_name in sound_channels:
        try:
            pygame.mixer.Channel(sound_channels[channel_name]).stop()
        except pygame.error:
            pass

def reset_player_position():
    """Reset player to starting position"""
    global player_vel_x, player_vel_y, protection_start_time, protection_active, on_ground, fly_mode
    player_pos.x = platforms[0].x
    player_pos.y = platforms[0].y - 106  # Ensure proper positioning above platform
    player_vel_x = 0
    player_vel_y = 0
    on_ground = True  # Start on ground
    fly_mode = False  # Disable fly mode on respawn
    protection_start_time = time.time()
    protection_active = True

def start_boss_phase():
    """Initialize boss phase"""
    global boss_phase, boss_active, boss_phase_start_time, alien_counter
    global knight_fire_effect, knight_fire_start_time, knight_fire_flash_count
    boss_phase = True
    boss_active = True
    boss_phase_start_time = time.time()
    alien_counter = 10  # Reset counter for boss phase
    create_boss_platforms()
    stop_sound('lava')
    play_sound(boss_music, 'boss_music', -1)
    reset_player_position()
    
    # Start knight fire effect
    knight_fire_effect = True
    knight_fire_start_time = time.time()
    knight_fire_flash_count = 0
    print("Knight fire effect activated!")

def play_intro_video():
    """Play the START.mp4 intro video for 1 minute with start_audio.m4a"""
    global game_state
    
    try:
        # Load video with OpenCV
        video_path = "START.mp4"
        if not os.path.exists(video_path):
            print("START.mp4 not found, skipping to game")
            game_state = "playing"
            return
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Could not open video file")
            game_state = "playing"
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30  # Default fallback
        
        # Play audio_start.mp3 for the intro video
        audio_played = False
        try:
            # Prioritize audio_start.mp3
            if os.path.exists("audio_start.mp3"):
                pygame.mixer.music.load("audio_start.mp3")
                pygame.mixer.music.play()
                audio_played = True
                print("Playing audio_start.mp3")
            else:
                # Try other audio formats as fallback
                audio_files = ["start_audio.m4a", "start_audio.mp3", "start_audio.wav", "START.wav", "START.mp3"]
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        try:
                            pygame.mixer.music.load(audio_file)
                            pygame.mixer.music.play()
                            audio_played = True
                            print(f"Playing {audio_file}")
                            break
                        except pygame.error as e:
                            print(f"Could not play {audio_file}: {e}")
                            continue
            
            if not audio_played:
                print("audio_start.mp3 not found. Place it in the game folder for intro audio.")
        except Exception as e:
            print(f"Audio error: {e}")
            
        if not audio_played:
            print("Playing video without audio")
        
        clock = pygame.time.Clock()
        video_playing = True
        start_time = time.time()
        video_duration = 55  # 55 seconds as requested
        
        while video_playing and cap.isOpened():
            # Check if 1 minute has passed
            elapsed_time = time.time() - start_time
            if elapsed_time >= video_duration:
                video_playing = False
                game_state = "playing"
                break
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    cap.release()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        video_playing = False
                        game_state = "playing"
                        pygame.mixer.music.stop()
                        break
            
            if not video_playing:
                break
            
            ret, frame = cap.read()
            if not ret:
                # Video ended, restart video for 1 minute duration
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
                ret, frame = cap.read()
                if not ret:
                    video_playing = False
                    game_state = "playing"
                    break
            
            # Convert frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Scale frame to fill entire screen
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            
            # Convert to pygame surface
            frame = frame.swapaxes(0, 1)  # Swap x and y axes for pygame
            frame_surface = pygame.surfarray.make_surface(frame)
            
            # Draw fullscreen frame
            screen.blit(frame_surface, (0, 0))
            
            # Optional: Show remaining time
            remaining_time = int(video_duration - elapsed_time)
            if remaining_time > 0:
                time_text = font.render(f"Time: {remaining_time}s", True, WHITE)
                screen.blit(time_text, (WIDTH - 100, 10))
            
            pygame.display.flip()
            clock.tick(fps)
        
        cap.release()
        pygame.mixer.music.stop()
        
    except Exception as e:
        print(f"Error playing video: {e}")
        pygame.mixer.music.stop()
        game_state = "playing"

def show_text_intro():
    """Minimal text intro - removed long story"""
    screen.fill(BLACK)
    
    simple_lines = [
        "RED KNIGHT: SPACE DEFENDER",
        "",
        "Use ARROW KEYS to move",
        "Use SPACE to attack",
        "",
        "Press ESC to start game..."
    ]
    
    y_offset = HEIGHT // 2 - 100
    for line in simple_lines:
        text = story_font.render(line, True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 50
        # Draw outline
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_text = story_font.render(line, True, WHITE)
            screen.blit(outline_text, (WIDTH // 2 - outline_text.get_width() // 2 + dx, y_offset + dy))
        
        # Draw main text
        main_text = story_font.render(line, True, RED)
        screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2, y_offset))
        y_offset += 45

def handle_explosions():
    """Handle explosion animations and cleanup"""
    global explosions, alien_counter, boss_health
    current_time = pygame.time.get_ticks()
    
    for explosion in explosions[:]:
        if current_time - explosion["start_time"] > EXPLOSION_DURATION:
            explosions.remove(explosion)
            alien_counter -= 1
            if boss_phase and boss_health > 0:
                boss_health -= 1

def update_enemies():
    """Update enemy positions and behavior"""
    global enemies
    import math
    current_time = pygame.time.get_ticks()
    
    for enemy in enemies[:]:
        # Update special status dynamically - only active when alien_counter <= 10
        if alien_counter <= 10 and not enemy.get("spawned_by_boss", False):
            # Check if this enemy should be special (last 10 in the pattern)
            enemy_index = 0
            for i, other_enemy in enumerate(enemies):
                if other_enemy == enemy:
                    enemy_index = i
                    break
            
            total_enemies = len([e for e in enemies if not e.get("spawned_by_boss", False)])
            enemy["is_special"] = enemy_index >= (total_enemies - 10)
        else:
            enemy["is_special"] = False
        
        if not enemy.get("spawned_by_boss", False):
            # Special movement for last 10 enemies - truly random around platforms
            if enemy.get("is_special", False):
                # Initialize random movement parameters if not set
                if "movement_timer" not in enemy:
                    enemy["movement_timer"] = 0
                    enemy["direction_x"] = random.choice([-1, 1])
                    enemy["direction_y"] = random.choice([-1, 1])
                    enemy["speed_x"] = random.uniform(1, 3)
                    enemy["speed_y"] = random.uniform(1, 3)
                    enemy["direction_change_timer"] = random.randint(60, 180)  # Change direction every 1-3 seconds
                    enemy["original_platform_x"] = enemy["rect"].x
                    enemy["original_platform_y"] = enemy["rect"].y
                
                enemy["movement_timer"] += 1
                
                # Change direction randomly
                if enemy["movement_timer"] >= enemy["direction_change_timer"]:
                    enemy["direction_x"] = random.choice([-1, 1])
                    enemy["direction_y"] = random.choice([-1, 1])
                    enemy["speed_x"] = random.uniform(1, 3)
                    enemy["speed_y"] = random.uniform(1, 3)
                    enemy["direction_change_timer"] = random.randint(60, 180)
                    enemy["movement_timer"] = 0
                
                # Move in current direction
                enemy["rect"].x += enemy["direction_x"] * enemy["speed_x"]
                enemy["rect"].y += enemy["direction_y"] * enemy["speed_y"]
                
                # Keep them within reasonable bounds around their platform
                platform_x = enemy["original_platform_x"]
                platform_y = enemy["original_platform_y"]
                max_distance = 150  # Maximum distance from original position
                
                # Bounce off invisible boundaries
                if enemy["rect"].x < platform_x - max_distance:
                    enemy["rect"].x = platform_x - max_distance
                    enemy["direction_x"] = 1
                elif enemy["rect"].x > platform_x + max_distance:
                    enemy["rect"].x = platform_x + max_distance
                    enemy["direction_x"] = -1
                
                if enemy["rect"].y < platform_y - max_distance:
                    enemy["rect"].y = platform_y - max_distance
                    enemy["direction_y"] = 1
                elif enemy["rect"].y > platform_y + 50:  # Don't go below platform
                    enemy["rect"].y = platform_y + 50
                    enemy["direction_y"] = -1
            else:
                # Regular enemy movement (up and down)
                enemy["rect"].y += enemy["direction"] * enemy["speed"]
                if enemy["rect"].y >= enemy["platform_y"] - 40:
                    enemy["direction"] = -1
                elif enemy["rect"].y <= enemy["base_y"] - 100:
                    enemy["direction"] = 1
        else:
            # Boss spawned enemies (horizontal movement with random variations)
            if not hasattr(enemy, "random_timer"):
                enemy["random_timer"] = 0
                enemy["random_y_offset"] = 0
                enemy["random_speed_modifier"] = 1.0
            
            enemy["random_timer"] += 1
            
            # Add random movement every 30 frames (0.5 seconds)
            if enemy["random_timer"] % 30 == 0:
                enemy["random_y_offset"] = random.randint(-20, 20)  # Random vertical movement
                enemy["random_speed_modifier"] = random.uniform(0.8, 1.4)  # Speed variation
            
            # Apply horizontal movement with random speed
            enemy["rect"].x += enemy["direction"] * enemy["speed"] * enemy["random_speed_modifier"]
            
            # Apply random vertical movement
            enemy["rect"].y += enemy["random_y_offset"] * 0.1  # Slow vertical drift
            
            # Remove if off screen
            if enemy["rect"].x < -100:
                enemies.remove(enemy)
                continue
        
        # Play alien sound when close to player
        if abs(enemy["rect"].x - player_pos.x) < 200 and not enemy["sound_played"]:
            play_sound(alien_sound, 'alien')
            enemy["sound_played"] = True

def handle_collisions():
    """Handle all collision detection"""
    global lives, attack_hitbox, protection_active, boss_health, boss_position_y
    
    # Skip collisions if protected
    if protection_active:
        return
    
    # Direct boss hit detection during boss phase
    if boss_phase and attack_hitbox and boss_health > 0:
        # Create boss hitbox
        boss_hitbox = pygame.Rect(WIDTH - 400, boss_position_y, 400, 400)
        if attack_hitbox.colliderect(boss_hitbox):
            boss_health -= 1
            play_sound(boom_sound, 'explosion')
            print(f"Boss hit! Health remaining: {boss_health}")
    
    # Check lava collision
    lava_hitbox = pygame.Rect(-9999999, ground_level, 99999999, 50)
    if player_pos.colliderect(lava_hitbox):
        lives -= 1
        play_sound(hearth_sound, 'sfx')
        reset_player_position()
        if boss_phase:
            # Clear boss spawned enemies
            enemies[:] = [e for e in enemies if not e.get("spawned_by_boss", False)]
    
    # Check enemy collisions
    for enemy in enemies[:]:
        # Attack collision
        if attack_hitbox and attack_hitbox.colliderect(enemy["rect"]):
            explosions.append({
                "rect": enemy["rect"].copy(),
                "start_time": pygame.time.get_ticks()
            })
            play_sound(boom_sound, 'explosion')
            enemies.remove(enemy)
            continue
        
        # Player collision
        if player_pos.colliderect(enemy["rect"]):
            lives -= 1
            play_sound(hearth_sound, 'sfx')
            reset_player_position()
            if boss_phase:
                # Clear boss spawned enemies
                enemies[:] = [e for e in enemies if not e.get("spawned_by_boss", False)]
            break

def update_protection():
    """Update protection system"""
    global protection_active, protection_start_time
    
    if protection_start_time and time.time() - protection_start_time > protection_duration:
        protection_active = False
        protection_start_time = None

def draw_protection_circle():
    """Draw protective circle around player"""
    if protection_active:
        circle_center = (player_pos.x + player_pos.width // 2 - camera_x_offset, 
                        player_pos.y + player_pos.height // 2)
        pygame.draw.circle(screen, RED, circle_center, 100, 3)

def draw_knight_fire_effect():
    """Draw fire effect around knight when entering boss mode"""
    global knight_fire_effect, knight_fire_start_time, knight_fire_flash_count
    
    if not knight_fire_effect:
        return
    
    current_time = time.time()
    elapsed_time = current_time - knight_fire_start_time
    
    # End effect after duration
    if elapsed_time >= knight_fire_duration:
        knight_fire_effect = False
        return
    
    # Calculate flash timing (flash 3 times)
    flash_cycle = elapsed_time / knight_fire_flash_interval
    flash_number = int(flash_cycle)
    flash_phase = flash_cycle - flash_number
    
    # Only show effect during first 3 flashes
    if flash_number < 6:  # 6 half-cycles = 3 full flashes
        # Show fire effect during "on" phase of flash
        if flash_phase < 0.5:  # First half of each cycle
            knight_center_x = player_pos.x + player_pos.width // 2 - camera_x_offset
            knight_center_y = player_pos.y + player_pos.height // 2
            
            # Draw multiple fire rings with different colors
            import random
            
            # Outer fire ring (orange/red)
            for i in range(12):  # 12 fire points around knight
                angle = (i * 30) + (elapsed_time * 200)  # Rotating fire
                distance = 80 + random.randint(-10, 10)
                fire_x = knight_center_x + distance * math.cos(math.radians(angle))
                fire_y = knight_center_y + distance * math.sin(math.radians(angle))
                
                # Fire colors
                fire_colors = [(255, 0, 0), (255, 69, 0), (255, 140, 0), (255, 165, 0)]
                fire_color = random.choice(fire_colors)
                fire_size = random.randint(8, 15)
                
                pygame.draw.circle(screen, fire_color, (int(fire_x), int(fire_y)), fire_size)
            
            # Inner fire ring (brighter)
            for i in range(8):  # 8 inner fire points
                angle = (i * 45) - (elapsed_time * 150)  # Counter-rotating
                distance = 60 + random.randint(-5, 5)
                fire_x = knight_center_x + distance * math.cos(math.radians(angle))
                fire_y = knight_center_y + distance * math.sin(math.radians(angle))
                
                fire_colors = [(255, 255, 0), (255, 200, 0), (255, 100, 0)]
                fire_color = random.choice(fire_colors)
                fire_size = random.randint(5, 10)
                
                pygame.draw.circle(screen, fire_color, (int(fire_x), int(fire_y)), fire_size)
            
            # Central glow around knight
            glow_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 100, 0, 50), (100, 100), 100)
            screen.blit(glow_surface, (knight_center_x - 100, knight_center_y - 100))

# Background music will start when gameplay begins
# Don't start lava sound during intro

# Main game loop
while running:
    dt = clock.tick(FPS)
    current_time = time.time()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Fly mode toggle (works in any game state except story)
            if event.key == pygame.K_f and game_state == "playing":
                fly_mode = not fly_mode
                if fly_mode:
                    player_vel_y = 0  # Stop falling when entering fly mode
            
            # Kill all aliens cheat (press 0)
            if event.key == pygame.K_0 and game_state == "playing":
                enemies.clear()  # Remove all enemies
                explosions.clear()  # Remove all explosions
                alien_counter = 0  # Set counter to 0
                cheat_message = "ALL ALIENS ELIMINATED!"
                cheat_message_timer = pygame.time.get_ticks()
                print("All aliens killed with cheat code!")
            
            if game_state == "story":
                # Check if ESC was pressed to skip
                if event.key == pygame.K_ESCAPE:
                    # Skip directly to game
                    game_state = "playing"
                else:
                    # Any other key shows full story
                    story_timer = 0
                    game_state = "story_playing"
    
    # Handle different game states
    if game_state == "story":
        # Play intro video with audio
        play_intro_video()
    
    elif game_state == "story_playing":
        # Show story for full duration, but allow skipping with numbers
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Allow skipping with ESC during story_playing
                if event.key == pygame.K_ESCAPE:
                    game_state = "playing"
                    break
        
        show_text_intro()
        story_timer += dt
        if story_timer >= 8000:  # 8 seconds
            game_state = "playing"
    
    elif game_state == "playing":
        # Stop intro music and start lava sound when gameplay begins (only once)
        if not pygame.mixer.Channel(sound_channels['lava']).get_busy():
            pygame.mixer.music.stop()  # Stop intro video music
            play_sound(lava_sound, 'lava', -1)
        
        # Check for boss phase transition
        if alien_counter <= 0 and not boss_phase:
            start_boss_phase()
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Movement (with fly mode speed boost)
        fly_speed_multiplier = 2.5 if fly_mode else 1.0
        if keys[pygame.K_LEFT]:
            player_vel_x = -5 * speed_multiplier * fly_speed_multiplier
            facing_right = False
        elif keys[pygame.K_RIGHT]:
            player_vel_x = 5 * speed_multiplier * fly_speed_multiplier
            facing_right = True
        else:
            player_vel_x = 0
        
        # Fly mode movement (up/down)
        if fly_mode:
            if keys[pygame.K_UP]:
                player_vel_y = -5 * speed_multiplier * fly_speed_multiplier  # Fly up faster
            elif keys[pygame.K_DOWN]:
                player_vel_y = 5 * speed_multiplier * fly_speed_multiplier   # Fly down faster
            else:
                player_vel_y = 0  # Hover in place
        else:
            # Normal jumping (only when not in fly mode)
            if keys[pygame.K_UP] and on_ground:
                # Higher jump in boss phase
                boss_jump_boost = 1.2 if boss_phase else 1.0
                player_vel_y = jump_power * boss_jump_boost
                on_ground = False
            
            # Falling through platforms (only when not in fly mode)
            falling_through = keys[pygame.K_DOWN]
        
        # Apply gravity (only when not in fly mode)
        if not fly_mode:
            player_vel_y += gravity
        
        # Update player position
        player_pos.x += player_vel_x
        player_pos.y += player_vel_y
        
        # Platform collision (only when not in fly mode)
        if not fly_mode:
            on_ground = False
            active_platforms = boss_platforms if boss_phase else platforms
            
            for platform in active_platforms:
                platform_rect = platform["rect"] if boss_phase else platform
                if (player_pos.colliderect(platform_rect) and player_vel_y >= 0 and 
                    not falling_through and player_pos.bottom - player_vel_y <= platform_rect.top + 10):
                    player_pos.bottom = platform_rect.top
                    player_vel_y = 0
                    on_ground = True
                    break
        
        # Attack handling
        if keys[pygame.K_SPACE] and attack_state == "ready" and stamina >= stamina_max:
            attack_state = "active"
            attack_timer = attack_duration
            stamina = 0
            play_sound(slash_sound, 'attack')
        
        # Attack handling with faster speed in boss phase
        if keys[pygame.K_SPACE] and attack_state == "ready" and stamina >= stamina_max:
            attack_state = "active"
            # 15% faster attack during boss phase
            boss_attack_speed = 0.85 if boss_phase else 1.0  # 15% faster = 85% of normal duration
            attack_timer = int(attack_duration * boss_attack_speed)
            attack_progress = 0.0
            stamina = 0
            play_sound(slash_sound, 'attack')
        
        # Update attack state with half-circle sword movement in front of knight
        if attack_state == "active":
            # Calculate slash progress (0.0 = start position, 1.0 = end position)
            attack_progress = 1.0 - (attack_timer / attack_duration)
            
            import math
            
            # Hilt position stays at knight's shoulder/hand
            hilt_offset_x = 10 if facing_right else -10  # Slightly forward from center
            hilt_offset_y = -15  # At shoulder height
            hilt_x = player_pos.x + player_pos.width // 2 + hilt_offset_x
            hilt_y = player_pos.y + player_pos.height // 2 + hilt_offset_y
            
            # Half-circle movement parameters in front of knight
            sword_length = 100  # Increased from 75 - LONGER sword reach!
            
            # Half-circle arc in front of the knight
            t = attack_progress
            
            # Sword slash: START at bottom → move UP to middle (SAME for both directions)
            # Start pointing down (-90°) and sweep UP to horizontal front (0° for both)
            start_angle = -math.pi / 2      # -90 degrees (straight down - BOTTOM position)
            end_angle = 0                   # 0 degrees (horizontal front - MIDDLE position)
            current_angle = start_angle + (end_angle - start_angle) * t  # Same arc for both directions
            
            # Calculate tip position (adjust X direction based on facing)
            tip_offset_x = sword_length * math.cos(current_angle)
            tip_offset_y = -sword_length * math.sin(current_angle)
            
            # Apply direction to X position only
            if facing_right:
                tip_x = hilt_x + tip_offset_x
            else:
                tip_x = hilt_x - tip_offset_x  # Mirror X position for left-facing
            tip_y = hilt_y + tip_offset_y
            
            # Calculate hitbox at the sword tip area
            if boss_phase:
                hitbox_width = 120
                hitbox_height = 90
            else:
                hitbox_width = 100
                hitbox_height = 70
            
            attack_hitbox = pygame.Rect(tip_x - hitbox_width//2, tip_y - hitbox_height//2, 
                                       hitbox_width, hitbox_height)
            
            attack_timer -= 1
            if attack_timer <= 0:
                attack_state = "cooldown"
                attack_timer = attack_cooldown
                attack_hitbox = None
                attack_progress = 0.0
        
        elif attack_state == "cooldown":
            attack_timer -= 1
            # Much faster stamina regen during boss phase (2x faster)
            boss_stamina_boost = 2.0 if boss_phase else 1.0
            stamina += stamina_regen_rate * boss_stamina_boost
            if stamina >= stamina_max:
                stamina = stamina_max
                attack_state = "ready"
        
        # Update camera
        camera_x_offset = player_pos.x - 100
        
        # Update game systems
        update_protection()
        update_enemies()
        handle_collisions()
        handle_explosions()
        
        # Boss spawning system
        if boss_phase and boss_active:
            # Move boss up and down
            boss_position_y += boss_speed * boss_direction
            if boss_position_y <= 100 or boss_position_y >= HEIGHT - 400:
                boss_direction *= -1
            
            # Spawn boss minions periodically (more frequent)
            if random.randint(1, 90) == 1:  # Roughly every 1.5 seconds at 60 FPS (more frequent)
                minion_rect = pygame.Rect(WIDTH + 100, boss_position_y + 200, 73, 73)
                enemies.append({
                    "rect": minion_rect,
                    "direction": -1,
                    "speed": 12,  # Faster speed
                    "sound_played": False,
                    "spawned_by_boss": True
                })
        
        # Check death condition
        if player_pos.y > HEIGHT:
            lives -= 1
            reset_player_position()
        
        # Check game over
        if lives <= 0:
            game_state = "game_over"
        
        # Check victory
        if boss_phase and boss_health <= 0:
            game_state = "victory"
        
        # Draw everything
        if boss_phase:
            # Boss phase flashing effect
            if current_time - boss_phase_start_time < boss_flash_duration:
                if int((current_time - boss_phase_start_time) / boss_flash_interval) % 2 == 0:
                    screen.fill(WHITE)
                else:
                    screen.fill(BLACK)
            else:
                # Draw boss background
                screen.blit(boss_background_image, (0, 0))
                
                # Draw boss
                screen.blit(boss_image, (WIDTH - 400, boss_position_y))
                
                # Draw boss health bar
                health_bar_y = boss_position_y - 30
                health_bar_width = 35
                health_bar_spacing = 40
                
                for i in range(boss_health):
                    x_pos = WIDTH - 410 + i * health_bar_spacing
                    pygame.draw.rect(screen, PINK, (x_pos, health_bar_y, health_bar_width, 20))
                
                for i in range(boss_max_health - boss_health):
                    x_pos = WIDTH - 410 + (boss_health + i) * health_bar_spacing
                    pygame.draw.rect(screen, RED, (x_pos, health_bar_y, health_bar_width, 20))
                
                # Draw "ALIEN BOSS" text
                boss_text = boss_font.render("ALIEN BOSS", True, PINK)
                boss_text_outline = boss_font.render("ALIEN BOSS", True, BLACK)
                text_x = WIDTH // 2 - boss_text.get_width() // 2
                screen.blit(boss_text_outline, (text_x - 2, 18))
                screen.blit(boss_text_outline, (text_x + 2, 18))
                screen.blit(boss_text_outline, (text_x, 16))
                screen.blit(boss_text_outline, (text_x, 20))
                screen.blit(boss_text, (text_x, 18))
        else:
            # Regular background
            screen.blit(background_image, (0, 0))
            
            # Draw lava
            for i in range((WIDTH // 50) + 2):
                lava_x = (i * 50) - (camera_x_offset % 50)
                screen.blit(lava_image, (lava_x, ground_level))
        
        # Draw platforms
        active_platforms = boss_platforms if boss_phase else platforms
        for platform in active_platforms:
            platform_rect = platform["rect"] if boss_phase else platform
            draw_rect = platform_rect.move(-camera_x_offset, 0)
            if boss_phase:
                # Semi-transparent boss platforms
                platform_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                platform_surface.fill(BLACK_TRANSPARENT)
                screen.blit(platform_surface, draw_rect.topleft)
            else:
                pygame.draw.rect(screen, BLACK, draw_rect)
        
        # Draw player
        character_display = pygame.transform.flip(character_image, not facing_right, False)
        screen.blit(character_display, player_pos.move(-camera_x_offset, 0))
        
        # Draw protection circle
        draw_protection_circle()
        
        # Draw knight fire effect when entering boss mode
        draw_knight_fire_effect()
        
        # Draw enemies
        for enemy in enemies:
            enemy_pos = enemy["rect"].move(-camera_x_offset, 0)
            screen.blit(enemy_image, enemy_pos)
            
            # Draw special indicator for last 10 enemies
            if enemy.get("is_special", False):
                # Check if this is the first enhanced alien seen on screen when counter hits exactly 10
                if not first_enhanced_alien_seen and not aliens_enraged and alien_counter == 10:
                    # Check if enemy is visible on screen
                    if 0 <= enemy_pos.x <= WIDTH and 0 <= enemy_pos.y <= HEIGHT:
                        first_enhanced_alien_seen = True
                        aliens_enraged = True
                        enraged_flash_start = time.time()
                        enraged_message_timer = pygame.time.get_ticks()
                        print("ALIENS HAVE BEEN ENRAGED!")
                
                # Draw a red glow around special enemies
                pygame.draw.circle(screen, RED, 
                                 (enemy_pos.x + enemy_pos.width // 2, 
                                  enemy_pos.y + enemy_pos.height // 2), 
                                 40, 2)
        
        # Draw explosions
        for explosion in explosions:
            screen.blit(boom_image, explosion["rect"].move(-camera_x_offset, 0))
        
        # Draw attack with half-circle sword movement in front of knight
        if attack_state == "active" and attack_hitbox:
            import math
            
            # Hilt position (at knight's shoulder/hand)
            hilt_offset_x = 10 if facing_right else -10  # Slightly forward
            hilt_offset_y = -15  # At shoulder height
            hilt_x = player_pos.x + player_pos.width // 2 + hilt_offset_x - camera_x_offset
            hilt_y = player_pos.y + player_pos.height // 2 + hilt_offset_y
            
            # Calculate tip position for half-circle movement in front
            t = attack_progress
            sword_length = 100  # LONGER sword - increased from 75
            
            # Sword motion: START at bottom → move UP to middle (SAME animation for both directions)
            start_angle = -math.pi / 2      # -90 degrees (straight down - BOTTOM)
            end_angle = 0                   # 0 degrees (horizontal front - MIDDLE)
            current_angle = start_angle + (end_angle - start_angle) * t
            
            # Calculate tip position (same arc, different X direction)
            tip_offset_x = sword_length * math.cos(current_angle)
            tip_offset_y = -sword_length * math.sin(current_angle)
            
            # Apply direction to X position only
            if facing_right:
                tip_x = hilt_x + tip_offset_x
            else:
                tip_x = hilt_x - tip_offset_x  # Mirror for left-facing
            tip_y = hilt_y + tip_offset_y
            
            # Calculate sword rotation based on hilt-to-tip direction
            dx = tip_x - hilt_x
            dy = tip_y - hilt_y
            rotation_degrees = math.degrees(math.atan2(dy, dx))
            
            # Fix upside-down sword when facing left by flipping 180 degrees
            if not facing_right:
                rotation_degrees += 180  # Flip 180 degrees for left-facing
            
            # Choose sword image and apply effects
            sword_img = sword_image_right if facing_right else sword_image_left
            half_circle_sword = pygame.transform.scale(sword_img, (121, 83))  # 10% bigger (was 110x75, now 121x83)
            
            # Red burning effect during boss phase (FIXED - only one sword)
            if boss_phase:
                red_sword = half_circle_sword.copy()
                red_overlay = pygame.Surface(red_sword.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 50, 50, 100))
                red_sword.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
                
                rotated_sword = pygame.transform.rotate(red_sword, rotation_degrees)
                
                # Position sword so hilt stays at knight's hand (NO GLOW SWORD - just one sword)
                sword_rect = rotated_sword.get_rect()
                if facing_right:
                    sword_pos_x = hilt_x - 15  # Hilt at hand position
                    sword_pos_y = hilt_y - sword_rect.height // 2
                else:
                    sword_pos_x = hilt_x - sword_rect.width + 15
                    sword_pos_y = hilt_y - sword_rect.height // 2
                
                screen.blit(rotated_sword, (sword_pos_x, sword_pos_y))  # Only draw ONE sword
            else:
                # Normal half-circle sword
                rotated_sword = pygame.transform.rotate(half_circle_sword, rotation_degrees)
                sword_rect = rotated_sword.get_rect()
                
                # Position so hilt stays at knight's hand
                if facing_right:
                    sword_pos_x = hilt_x - 15  # Hilt at hand
                    sword_pos_y = hilt_y - sword_rect.height // 2
                else:
                    sword_pos_x = hilt_x - sword_rect.width + 15
                    sword_pos_y = hilt_y - sword_rect.height // 2
                
                screen.blit(rotated_sword, (sword_pos_x, sword_pos_y))
        
        # Draw UI
        # Lives
        for i in range(lives):
            screen.blit(heart_image, (10 + i * 50, 10))
        
        # Stamina bar
        stamina_ratio = max(0, min(1, stamina / stamina_max))
        stamina_length = int(stamina_bar_width * stamina_ratio)
        pygame.draw.rect(screen, STAMINA_COLOR, (10, 70, stamina_length, stamina_bar_height))
        pygame.draw.rect(screen, BLACK, (10, 70, stamina_bar_width, stamina_bar_height), 2)
        
        # Fly mode indicator
        if fly_mode:
            fly_text = font.render("FLY MODE - Press F to disable", True, WHITE)
            fly_text_outline = font.render("FLY MODE - Press F to disable", True, BLACK)
            # Draw outline
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                screen.blit(fly_text_outline, (10 + dx, 100 + dy))
            screen.blit(fly_text, (10, 100))
        
        # Red flash effect when aliens are enraged
        if enraged_flash_start and time.time() - enraged_flash_start < 1.0:  # Flash for 1 second
            elapsed_flash = time.time() - enraged_flash_start
            # Flash red 2 times (0-0.25s: red, 0.25-0.5s: normal, 0.5-0.75s: red, 0.75-1s: normal)
            if (0 <= elapsed_flash < 0.25) or (0.5 <= elapsed_flash < 0.75):
                red_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                red_overlay.fill((255, 0, 0, 100))  # Semi-transparent red
                screen.blit(red_overlay, (0, 0))
        
        # Show "ALIENS ENRAGED" message at top of screen
        if enraged_message_timer > 0 and pygame.time.get_ticks() - enraged_message_timer < 3000:  # Show for 3 seconds
            enraged_text = game_over_font.render("THE ALIENS HAVE BEEN ENRAGED!", True, RED)
            enraged_outline = game_over_font.render("THE ALIENS HAVE BEEN ENRAGED!", True, BLACK)
            msg_x = WIDTH // 2 - enraged_text.get_width() // 2
            msg_y = 50  # Top of screen instead of center
            # Draw outline
            for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                screen.blit(enraged_outline, (msg_x + dx, msg_y + dy))
            screen.blit(enraged_text, (msg_x, msg_y))
        elif pygame.time.get_ticks() - enraged_message_timer >= 3000:
            enraged_message_timer = 0
        
        # Show cheat message
        if cheat_message and pygame.time.get_ticks() - cheat_message_timer < 3000:  # Show for 3 seconds
            cheat_msg_text = game_over_font.render(cheat_message, True, RED)
            cheat_msg_outline = game_over_font.render(cheat_message, True, BLACK)
            msg_x = WIDTH // 2 - cheat_msg_text.get_width() // 2
            msg_y = HEIGHT // 2 - 100
            # Draw outline
            for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                screen.blit(cheat_msg_outline, (msg_x + dx, msg_y + dy))
            screen.blit(cheat_msg_text, (msg_x, msg_y))
        elif pygame.time.get_ticks() - cheat_message_timer >= 3000:
            cheat_message = ""
        
        # Cheat code indicator (small text at bottom)
        cheat_text = font.render("Cheats: F=Fly Mode, 0=Kill All Aliens", True, WHITE)
        cheat_outline = font.render("Cheats: F=Fly Mode, 0=Kill All Aliens", True, BLACK)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            screen.blit(cheat_outline, (10 + dx, HEIGHT - 25 + dy))
        screen.blit(cheat_text, (10, HEIGHT - 25))
        
        # Alien counter
        counter_color = PINK if boss_phase else ALIEN_COUNTER_COLOR
        counter_text = counter_font.render(str(alien_counter), True, counter_color)
        counter_outline = counter_font.render(str(alien_counter), True, BLACK)
        counter_x, counter_y = WIDTH - 120, 30
        
        # Draw outline
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            screen.blit(counter_outline, (counter_x + dx, counter_y + dy))
        screen.blit(counter_text, (counter_x, counter_y))
        
        # Alien icon
        alien_icon = pygame.transform.scale(enemy_image, (50, 50))
        screen.blit(alien_icon, (counter_x - 60, counter_y))
    
    elif game_state == "game_over":
        stop_sound('boss_music')
        stop_sound('lava')
        screen.blit(game_over_screen_image, (0, 0))
        pygame.display.flip()  # Make sure screen updates
        pygame.time.wait(4000)  # 4 seconds as requested
        running = False
    
    elif game_state == "victory":
        stop_sound('boss_music')
        stop_sound('lava')
        
        # Victory explosion sequence with bigger explosions
        for i in range(5):
            play_sound(boom_sound, 'explosion')
            screen.fill(BLACK)
            
            # Draw random BIG explosions
            for _ in range(30):  # More explosions
                boom_x = random.randint(0, WIDTH - 200)  # Account for bigger size
                boom_y = random.randint(0, HEIGHT - 200)
                
                # Scale explosion to be much bigger (3x size)
                big_boom = pygame.transform.scale(boom_image, (200, 200))
                screen.blit(big_boom, (boom_x, boom_y))
                
                # Add some medium sized explosions for variety
                if random.randint(1, 3) == 1:  # 33% chance
                    medium_boom_x = random.randint(0, WIDTH - 120)
                    medium_boom_y = random.randint(0, HEIGHT - 120)
                    medium_boom = pygame.transform.scale(boom_image, (120, 120))
                    screen.blit(medium_boom, (medium_boom_x, medium_boom_y))
            
            pygame.display.flip()
            pygame.time.wait(500)
        
        # Show victory screen
        screen.blit(finish_screen_image, (0, 0))
        play_sound(victory_sound, 'sfx')
        pygame.display.flip()  # Ensure screen updates
        pygame.time.wait(5000)  # 5 seconds as requested
        running = False
    
    # Only update display if we're still running
    if running:
        pygame.display.flip()

# Cleanup
pygame.mixer.stop()
pygame.quit()