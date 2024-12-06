import pygame
import random
import sys
import os

# Inicializar Pygame
pygame.init()

# Configurar la pantalla
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lluvia Espacial")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Configuración de niveles
class GameLevel:
    def __init__(self, max_meteors, meteor_min_speed, meteor_max_speed, music_file, num_astronauts, num_enemies):
        self.max_meteors = max_meteors
        self.meteor_min_speed = meteor_min_speed
        self.meteor_max_speed = meteor_max_speed
        self.music_file = music_file
        self.num_astronauts = num_astronauts
        self.num_enemies = num_enemies

# Definir niveles
LEVELS = [
    GameLevel(6, 2, 8, "Orbital_Colossus.mp3", 1, 2),
    GameLevel(8, 3, 9, "8bit-sample-69080.mp3", 2, 3),
    GameLevel(10, 4, 10, "paft-drunk-sunglasses-synthwave-atari-early-80x27s-mix-210339.mp3", 3, 4),
    GameLevel(12, 5, 11, "retro-wave-style-track-59892.mp3", 4, 5)
]

# Sonidos
PIXEL_DEATH_SOUND = "pixel-death.mp3"
GAME_DEATH_SOUND = "game-death.mp3"
RESCUE_SOUND = "8-bit-game.mp3"
VICTORY_SOUND = "victory-sound.mp3"

# Función para cargar imágenes de manera segura
def load_image(name, size=None):
    try:
        image = pygame.image.load(name).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"No se pudo cargar la imagen {name}: {e}")
        surf = pygame.Surface(size if size else (50, 50))
        surf.fill(RED)
        return surf

# Función para cargar sonidos de manera segura
def load_sound(name):
    try:
        sound = pygame.mixer.Sound(name)
        return sound
    except pygame.error as e:
        print(f"No se pudo cargar el sonido {name}: {e}")
        return None

# Función para cambiar la música
def change_music(music_file):
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"No se pudo cargar la música {music_file}: {e}")

# Jugador
player_width = 50  # Rectángulo de colisión más pequeño
player_height = 50
player = pygame.Rect(WIDTH // 2 - player_width // 2,
                    HEIGHT - player_height - 10,
                    player_width, player_height)

# Cargar y escalar imágenes
player_size = (70, 70)  # Tamaño visual más grande que la colisión
meteor_size = (50, 50)
astronaut_size = (50, 50)
enemy_size = (50, 50)
station_size = (50, 50)
player_img = load_image("nave.png", player_size)
meteor_img = load_image("meteoro.png", meteor_size)
astronaut_img = load_image("astronaut.png", astronaut_size)
enemy_img = load_image("ship.png", enemy_size)
station_img = load_image("station.png", station_size)
background_img = load_image("space.png", (WIDTH, HEIGHT))
launch_img = load_image("launch4.jpeg", (WIDTH, HEIGHT))

# Cargar sonidos
pixel_death_sound = load_sound(PIXEL_DEATH_SOUND)
game_death_sound = load_sound(GAME_DEATH_SOUND)
rescue_sound = load_sound(RESCUE_SOUND)
victory_sound = load_sound(VICTORY_SOUND)

# Meteoritos
meteor_width = 20  # Rectángulo de colisión más pequeño
meteor_height = 20
meteors = []

# Astronautas
astronauts = []

# Enemigos
enemies = []

# Estación
station = pygame.Rect(WIDTH // 2 - 25, 0, 50, 50)

# Puntuación y nivel
score = 0
high_score = 0
current_level_index = 0
font = pygame.font.Font(None, 36)

# Inicializar el mixer de Pygame
pygame.mixer.init()
change_music("game-music.mp3")

def show_level_up():
    level_font = pygame.font.Font(None, 74)
    level_text = level_font.render(f"¡Nivel {current_level_index + 1}!", True, WHITE)
    text_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Guardar el fondo actual
    background = screen.copy()

    # Mostrar animación de nivel
    alpha = 0
    text_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for i in range(60):  # 1 segundo de animación
        screen.blit(background, (0, 0))
        alpha = min(255, alpha + 8)
        text_surface.fill((0, 0, 0, 0))
        level_text.set_alpha(alpha)
        text_surface.blit(level_text, text_rect)
        screen.blit(text_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(16)

def show_game_over():
    try:
        game_over_sound = pygame.mixer.Sound(GAME_DEATH_SOUND)
        pygame.mixer.music.stop()
        game_over_sound.play()
    except pygame.error as e:
        print(f"No se pudo cargar el sonido de Game Over: {e}")

    game_over_font = pygame.font.Font(None, 74)
    game_over_text = game_over_font.render("Game Over", True, WHITE)
    score_text = font.render(f"Puntuación Final: {score}", True, WHITE)
    high_score_text = font.render(f"Mejor Puntuación: {high_score}", True, WHITE)
    restart_text = font.render("Presiona R para reiniciar", True, WHITE)

    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()

def show_victory():
    try:
        victory_sound.play()
    except pygame.error as e:
        print(f"No se pudo cargar el sonido de victoria: {e}")

    victory_font = pygame.font.Font(None, 74)
    victory_text = victory_font.render("¡VICTORIA!", True, GREEN)  # En verde para diferenciarlo
    score_text = font.render(f"Puntuación Final: {score}", True, WHITE)
    high_score_text = font.render(f"Mejor Puntuación: {high_score}", True, WHITE)
    restart_text = font.render("Presiona R para jugar de nuevo", True, WHITE)

    victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    # Crear un efecto de resplandor
    for i in range(30):  # Efecto de pulso
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))

        # Hacer que el texto parpadee
        if i % 2 == 0:
            screen.blit(victory_text, victory_rect)

        screen.blit(score_text, score_rect)
        screen.blit(high_score_text, high_score_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()
        pygame.time.wait(100)

    # Mostrar todo el texto de manera permanente
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))
    screen.blit(victory_text, victory_rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()

def reset_game():
    global score, meteors, player, game_over, current_level_index, astronauts, enemies
    score = 0
    meteors = []
    astronauts = []
    enemies = []
    player.x = WIDTH // 2 - player_width // 2
    player.y = HEIGHT - player_height - 10
    game_over = False
    current_level_index = 0
    change_music(LEVELS[0].music_file)

def show_start_screen():
    screen.blit(launch_img, (0, 0))

    title_font = pygame.font.Font(None, 74)
    menu_font = pygame.font.Font(None, 48)

    title_text = title_font.render("Lluvia Espacial", True, RED)
    play_text = menu_font.render("Play", True, RED)
    exit_text = menu_font.render("Salir", True, RED)
    about_text = menu_font.render("About", True, RED)

    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    about_rect = about_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    screen.blit(title_text, title_rect)
    screen.blit(play_text, play_rect)
    screen.blit(exit_text, exit_rect)
    screen.blit(about_text, about_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    return
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif about_rect.collidepoint(event.pos):
                    show_about_screen()
            elif event.type == pygame.MOUSEMOTION:
                if play_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play", True, GREEN)
                else:
                    play_text = menu_font.render("Play", True, RED)

                if exit_rect.collidepoint(event.pos):
                    exit_text = menu_font.render("Salir", True, GREEN)
                else:
                    exit_text = menu_font.render("Salir", True, RED)

                if about_rect.collidepoint(event.pos):
                    about_text = menu_font.render("About", True, GREEN)
                else:
                    about_text = menu_font.render("About", True, RED)

                screen.blit(launch_img, (0, 0))
                screen.blit(title_text, title_rect)
                screen.blit(play_text, play_rect)
                screen.blit(exit_text, exit_rect)
                screen.blit(about_text, about_rect)
                pygame.display.flip()

def show_about_screen():
    screen.fill(BLACK)
    about_font = pygame.font.Font(None, 36)
    about_text = about_font.render("Desarrollado por Jorge Ortiz Ceballos", True, WHITE)
    about_rect = about_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(about_text, about_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_start_screen()

# Bucle principal
running = True
game_over = False
clock = pygame.time.Clock()
last_level_index = 0
rescued_astronaut = None

show_start_screen()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        # Obtener nivel actual
        current_level = LEVELS[current_level_index]

        # Verificar cambio de nivel
        if current_level_index > last_level_index:
            show_level_up()
            change_music(current_level.music_file)
            last_level_index = current_level_index

        # Control del jugador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 5
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= 5
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
            player.y += 5

        # Generar meteoritos
        if len(meteors) < current_level.max_meteors:
            meteor = {
                'rect': pygame.Rect(random.randint(0, WIDTH - meteor_width), -meteor_height,
                                  meteor_width, meteor_height),
                'speed': random.uniform(current_level.meteor_min_speed, current_level.meteor_max_speed)
            }
            meteors.append(meteor)

        # Generar astronautas
        if len(astronauts) < current_level.num_astronauts:
            astronaut = pygame.Rect(random.randint(0, WIDTH - astronaut_size[0]), random.randint(0, HEIGHT - astronaut_size[1]),
                                   astronaut_size[0], astronaut_size[1])
            astronauts.append(astronaut)

        # Generar enemigos
        if len(enemies) < current_level.num_enemies:
            enemy = {
                'rect': pygame.Rect(random.randint(0, WIDTH - enemy_size[0]), random.randint(0, HEIGHT - enemy_size[1]),
                                    enemy_size[0], enemy_size[1]),
                'speed': random.uniform(1, 3)
            }
            enemies.append(enemy)

        # Actualizar meteoritos
        for meteor in meteors[:]:
            meteor['rect'].y += meteor['speed']
            if meteor['rect'].top > HEIGHT:
                meteors.remove(meteor)
                score += 1
                if score > high_score:
                    high_score = score

        # Actualizar enemigos
        for enemy in enemies[:]:
            dx = player.x - enemy['rect'].x
            dy = player.y - enemy['rect'].y
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:
                enemy['rect'].x += dx * enemy['speed'] / dist
                enemy['rect'].y += dy * enemy['speed'] / dist

        # Detectar colisiones
        if not game_over:
            for meteor in meteors:
                if player.colliderect(meteor['rect']):
                    if pixel_death_sound:
                        pixel_death_sound.play()
                    game_over = True
                    show_game_over()
                    break

            for enemy in enemies:
                if player.colliderect(enemy['rect']):
                    if game_death_sound:
                        game_death_sound.play()
                    game_over = True
                    show_game_over()
                    break

            for astronaut in astronauts[:]:
                if player.colliderect(astronaut):
                    if rescue_sound:
                        rescue_sound.play()
                    rescued_astronaut = astronaut
                    astronauts.remove(astronaut)
                    score += 10
                    if score > high_score:
                        high_score = score

            if rescued_astronaut and player.colliderect(station):
                if rescue_sound:
                    rescue_sound.play()
                rescued_astronaut = None
                if current_level_index < len(LEVELS) - 1:
                    current_level_index += 1
                    show_level_up()
                    change_music(LEVELS[current_level_index].music_file)
                    last_level_index = current_level_index
                else:
                    show_victory()
                    game_over = True

    # Dibujar
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))

    # Dibujar jugador centrado en su rectángulo de colisión
    player_visual_x = player.x - (player_size[0] - player_width) // 2
    player_visual_y = player.y - (player_size[1] - player_height) // 2
    screen.blit(player_img, (player_visual_x, player_visual_y))

    # Dibujar meteoritos centrados en sus rectángulos de colisión
    for meteor in meteors:
        meteor_visual_x = meteor['rect'].x - (meteor_size[0] - meteor_width) // 2
        meteor_visual_y = meteor['rect'].y - (meteor_size[1] - meteor_height) // 2
        screen.blit(meteor_img, (meteor_visual_x, meteor_visual_y))

    # Dibujar astronautas
    for astronaut in astronauts:
        screen.blit(astronaut_img, (astronaut.x, astronaut.y))

    # Dibujar enemigos
    for enemy in enemies:
        screen.blit(enemy_img, (enemy['rect'].x, enemy['rect'].y))

    # Dibujar estación
    screen.blit(station_img, (station.x, station.y))

    # Mostrar puntuación y nivel
    score_text = font.render(f"Puntuación: {score}", True, WHITE)
    level_text = font.render(f"Nivel: {current_level_index + 1}", True, WHITE)
    high_score_text = font.render(f"Mejor Puntuación: {high_score}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(high_score_text, (10, 90))

    if game_over:
        show_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
