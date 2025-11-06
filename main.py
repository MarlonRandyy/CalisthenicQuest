import pygame
import sys
import os
import time

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Calisthenic Quest")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
LIGHT_BLUE = (100, 180, 255)
GREEN = (0, 180, 0)
RED = (220, 60, 60)
GOLD = (255, 215, 0)
PURPLE = (180, 80, 220)

# Rutas
ASSETS_DIR = "assets"

def load_image(name, scale=None):
    """Cargar imagen con opción de escalado"""
    try:
        img = pygame.image.load(os.path.join(ASSETS_DIR, name))
        if scale:
            img = pygame.transform.scale(img, scale)
        return img.convert_alpha()
    except:
        print(f"[ADVERTENCIA] Imagen no encontrada: {name}")
        # Crear una imagen de reemplazo
        surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(surf, PURPLE, (0, 0, 200, 200), border_radius=20)
        pygame.draw.rect(surf, (200, 150, 255), (20, 20, 160, 160), border_radius=15)
        return surf

def load_sound(name):
    """Cargar sonido con manejo de errores"""
    path = os.path.join(ASSETS_DIR, name)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    else:
        print(f"[ADVERTENCIA] Sonido no encontrado: {name}")
        return None

# Cargar imágenes
background_img = load_image("fondo.png", (WIDTH, HEIGHT))
title_img = load_image("titulo.png", (500, 120))  # Tamaño ajustado
win_img = load_image("win.png", (350, 175))  # Tamaño ajustado
lose_img = load_image("lose.png", (350, 175))  # Tamaño ajustado

# Cargar sonidos
bg_music = load_sound("musicadefondo.mp3")
menu_music = load_sound("menu.mp3")
push_sound = load_sound("sonidopush.mp3")
level_up_sound = load_sound("levelcompleto.mp3")
gameover_sound = load_sound("gameover.mp3")
win_sound = load_sound("win.mp3")

# Ejercicios por nivel
levels = [
    {"name": "PUSH UPS", "up_img": "push up.png", "down_img": "push up down.png", "goal": 10,
     "tip": "Ningún alimento engorda, pero el consumo excesivo sí."},
    {"name": "DIPS", "up_img": "deep.png", "down_img": "deep down.png", "goal": 8,
     "tip": "El superávit calórico es clave para ganar músculo."},
    {"name": "PULL UPS", "up_img": "pull up.png", "down_img": "pull up down.png", "goal": 6,
     "tip": "Lo importante es incluir actividad física diaria, aunque sea 30 min."}
]

# Pre-cargar imágenes de ejercicios
for level in levels:
    # Para pull-ups, invertimos las imágenes si es necesario
    if level["name"] == "PULL UPS":
        level["up_image"] = load_image(level["down_img"], (200, 200))  # Invertido
        level["down_image"] = load_image(level["up_img"], (200, 200))  # Invertido
    else:
        level["up_image"] = load_image(level["up_img"], (200, 200))
        level["down_image"] = load_image(level["down_img"], (200, 200))

# Fuente
title_font = pygame.font.SysFont("Arial", 60, bold=True)
font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 32)
tip_font = pygame.font.SysFont("Arial", 36, italic=True)
button_font = pygame.font.SysFont("Arial", 36)

# Variables de juego
current_level = 0
reps = 0
energy = 100
max_energy = 100
energy_decrease = 5
energy_recover = 0.8
last_press_time = 0
min_press_delay = 0.5  # segundos

# Estados
game_active = False
show_help = False
game_over = False
game_win = False
is_pushing = False
show_tip = False

# FPS
clock = pygame.time.Clock()

def draw_text_center(text, y, font_obj, color=WHITE, max_width=None):
    """Dibujar texto centrado horizontalmente con ajuste automático"""
    # Dividir texto en líneas si es necesario
    lines = []
    if max_width:
        words = text.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            # Calcular ancho del texto
            text_width = font_obj.size(test_line)[0]
            if text_width < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
    else:
        lines = [text]
    
    # Dibujar cada línea centrada
    total_height = len(lines) * font_obj.get_height()
    start_y = y - total_height // 2
    
    for i, line in enumerate(lines):
        text_surf = font_obj.render(line, True, color)
        screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, start_y + i * font_obj.get_height()))
    
    return text_surf

def draw_button(text, y, width=300, height=60, color=GREEN, text_color=WHITE):
    """Dibujar un botón con texto centrado"""
    btn_rect = pygame.Rect(WIDTH//2 - width//2, y, width, height)
    pygame.draw.rect(screen, color, btn_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, btn_rect, 2, border_radius=10)
    
    # Dibujar texto centrado en el botón
    text_surf = button_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=btn_rect.center)
    screen.blit(text_surf, text_rect)
    
    return btn_rect

def draw_menu():
    """Dibujar pantalla de menú principal"""
    # Fondo con efecto de movimiento
    screen.blit(background_img, (0, 0))
    
    # Título centrado y ajustado
    title_rect = title_img.get_rect(center=(WIDTH//2, 100))
    screen.blit(title_img, title_rect)
    
    # Botones
    start_btn = draw_button("INICIAR", 300, 300, 60, GREEN)
    help_btn = draw_button("AYUDA", 380, 300, 60, LIGHT_BLUE)
    exit_btn = draw_button("SALIR", 460, 300, 60, RED)
    
    # Texto informativo
    draw_text_center("¡Completa los 3 niveles para ganar!", 550, small_font, (200, 200, 255))
    
    return start_btn, help_btn, exit_btn

def draw_help():
    """Dibujar pantalla de ayuda"""
    # Fondo semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Panel de ayuda
    help_panel = pygame.Surface((650, 450), pygame.SRCALPHA)
    help_panel.fill((30, 30, 50, 230))
    pygame.draw.rect(help_panel, LIGHT_BLUE, (0, 0, 650, 450), 3, border_radius=15)
    screen.blit(help_panel, (WIDTH//2 - 325, HEIGHT//2 - 225))
    
    # Título
    draw_text_center("INSTRUCCIONES", HEIGHT//2 - 200, title_font, GOLD)
    
    # Contenido
    instructions = [
        "- Presiona ESPACIO para hacer repeticiones",
        "- Mantén un ritmo constante para no perder energía",
        "- Cada nivel tiene un objetivo de repeticiones",
        "- Si la energía llega a 0, pierdes",
        "- Completa los 3 niveles para ganar",
        "",
        "CONSEJOS:",
        "- No presiones demasiado rápido para evitar penalización",
        "- Descansa entre repeticiones para recuperar energía"
    ]
    
    y_pos = HEIGHT//2 - 150
    for instruction in instructions:
        draw_text_center(instruction, y_pos, small_font, WHITE)
        y_pos += 40
    
    # Instrucción para volver
    draw_text_center("Presiona ESC para volver al menú", HEIGHT - 80, small_font, (200, 200, 200))

def draw_game():
    """Dibujar pantalla de juego principal"""
    screen.blit(background_img, (0, 0))
    level = levels[current_level]
    
    # Dibujar barra de progreso
    pygame.draw.rect(screen, DARK_GRAY, (100, 30, 600, 40), border_radius=20)
    pygame.draw.rect(screen, LIGHT_BLUE, (100, 30, 600 * reps / level["goal"], 40), border_radius=20)
    pygame.draw.rect(screen, WHITE, (100, 30, 600, 40), 2, border_radius=20)
    
    # Dibujar texto de progreso
    progress_text = f"{reps}/{level['goal']} {level['name']}"
    draw_text_center(progress_text, 32, small_font, WHITE)
    
    # Dibujar barra de energía
    pygame.draw.rect(screen, DARK_GRAY, (100, 80, 600, 25), border_radius=12)
    energy_color = GREEN if energy > 50 else (255, 200, 0) if energy > 20 else RED
    pygame.draw.rect(screen, energy_color, (100, 80, 600 * energy / max_energy, 25), border_radius=12)
    pygame.draw.rect(screen, WHITE, (100, 80, 600, 25), 2, border_radius=12)
    
    # Dibujar texto de energía
    energy_text = f"ENERGÍA: {int(energy)}%"
    draw_text_center(energy_text, 80, small_font, WHITE)
    
    # Dibujar personaje más abajo y centrado
    player_img = level["down_image"] if is_pushing else level["up_image"]
    player_rect = player_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))  # Bajado 80px
    screen.blit(player_img, player_rect)
    
    # Instrucciones
    draw_text_center("ESPACIO: Ejercicio   |   ESC: Menú", HEIGHT - 40, small_font, (200, 200, 200))

def draw_tip():
    """Dibujar pantalla de consejo nutricional"""
    # Fondo semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 50, 200))
    screen.blit(overlay, (0, 0))
    
    # Panel de consejo
    tip_panel = pygame.Surface((650, 300), pygame.SRCALPHA)
    tip_panel.fill((30, 30, 70, 220))
    pygame.draw.rect(tip_panel, LIGHT_BLUE, (0, 0, 650, 300), 3, border_radius=15)
    screen.blit(tip_panel, (WIDTH//2 - 325, HEIGHT//2 - 150))
    
    # Título
    draw_text_center("CONSEJO NUTRICIONAL", HEIGHT//2 - 130, font, GOLD)
    
    # Texto del consejo con ajuste automático
    tip_text = levels[current_level]['tip']
    draw_text_center(tip_text, HEIGHT//2 - 40, tip_font, WHITE, max_width=600)
    
    # Instrucción para continuar
    draw_text_center("Presiona ESPACIO para continuar", HEIGHT - 80, small_font, (200, 200, 200))

def draw_end_screen(win):
    """Dibujar pantalla final (victoria o derrota)"""
    # Fondo semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Imagen de resultado (tamaño ajustado)
    img = win_img if win else lose_img
    img_rect = img.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    screen.blit(img, img_rect)
    
    # Texto de resultado
    result_text = "¡FELICIDADES, GANASTE!" if win else "¡GAME OVER!"
    result_color = GOLD if win else RED
    draw_text_center(result_text, 100, title_font, result_color)
    
    # Mensaje adicional
    message = "Has completado todos los niveles" if win else "Inténtalo de nuevo"
    draw_text_center(message, 180, font)
    
    # Instrucción para volver
    draw_text_center("Presiona ESC para volver al menú", HEIGHT - 80, small_font, (200, 200, 200))

# Reproducción de música
def play_music(sound, loop=True):
    """Reproducir música con manejo de errores"""
    if sound:
        try:
            sound.play(-1 if loop else 0)
        except:
            print("Error al reproducir música")

def stop_music():
    """Detener toda la música"""
    pygame.mixer.stop()

# Bucle principal
if menu_music:
    play_music(menu_music)

running = True
while running:
    screen.fill(BLACK)
    mouse_pos = pygame.mouse.get_pos()
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_active and not show_tip and not game_over and not game_win:
                if event.key == pygame.K_SPACE:
                    now = time.time()
                    if now - last_press_time < min_press_delay:
                        energy -= energy_decrease * 2  # penalización por spam
                    else:
                        energy -= energy_decrease
                        reps += 1
                        if push_sound:
                            push_sound.play()
                    last_press_time = now
                    is_pushing = True

                    if reps >= levels[current_level]['goal']:
                        stop_music()
                        if level_up_sound:
                            level_up_sound.play()
                        show_tip = True

                    if energy <= 0:
                        stop_music()
                        game_over = True

                elif event.key == pygame.K_ESCAPE:
                    stop_music()
                    game_active = False
                    play_music(menu_music)

            elif show_tip:
                if event.key == pygame.K_SPACE:
                    show_tip = False
                    current_level += 1
                    reps = 0
                    energy = max_energy
                    if current_level >= len(levels):
                        stop_music()
                        game_win = True
                    else:
                        play_music(bg_music)

            elif game_over or game_win:
                if event.key == pygame.K_ESCAPE:
                    game_over = False
                    game_win = False
                    game_active = False
                    current_level = 0
                    reps = 0
                    energy = max_energy
                    play_music(menu_music)

            elif show_help and event.key == pygame.K_ESCAPE:
                show_help = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not game_active and not show_help:
            # Manejo de clic en botones del menú
            if start_btn.collidepoint(mouse_pos):
                game_active = True
                stop_music()
                play_music(bg_music)
                reps = 0
                energy = max_energy
            elif help_btn.collidepoint(mouse_pos):
                show_help = True
            elif exit_btn.collidepoint(mouse_pos):
                running = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                is_pushing = False

    # Recuperar energía si no se está presionando espacio
    if game_active and not is_pushing and not show_tip and not game_over and not game_win:
        energy = min(energy + energy_recover, max_energy)

    # Dibujar pantalla actual
    if game_active:
        if show_tip:
            draw_tip()
        elif game_over:
            draw_end_screen(False)
        elif game_win:
            draw_end_screen(True)
        else:
            draw_game()
    elif show_help:
        draw_help()
    else:
        start_btn, help_btn, exit_btn = draw_menu()
        # Resaltar botones al pasar el mouse
        for btn, color in [(start_btn, (0, 180, 0)), (help_btn, (80, 160, 255)), (exit_btn, (240, 80, 80))]:
            if btn.collidepoint(mouse_pos):
                pygame.draw.rect(screen, color, btn, 3, border_radius=10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()