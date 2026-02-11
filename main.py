import pygame, sys, random, serial
from game import Game
from laser import Laser # <--- Importante para que el disparo funcione

# --- INICIO BLOQUE ARDUINO ---
try:
    # Ajusta 'COM3' al puerto que veas en tu IDE de Arduino
    arduino = serial.Serial('COM3', 9600, timeout=0.1)
except:
    arduino = None
# --- FIN BLOQUE ARDUINO ---

pygame.init()

# Resolución
screen_width = 1024
screen_height = 768
offset = 50

ui_color = (0, 180, 0)

# Textos
font = pygame.font.Font("font/monogram.ttf", 50)
game_over = font.render("MISION FALLIDA", False, ui_color)
score_text = font.render("PUNTOS", False, ui_color)
highscore_text = font.render("RECORD", False, ui_color)

screen = pygame.display.set_mode([screen_width + offset, screen_height + 2*offset])

pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()

game = Game(screen_width, screen_height, offset)
name_input = ""
small_font = pygame.font.Font("font/monogram.ttf", 30)
app_state = 'menu'  # 'menu', 'playing', 'highscores'
paused = False

mission_surface = font.render("MISION COMPLETADA", False, ui_color)
congrats_surface = small_font.render("¡FELICIDADES! Completaste la mision.", False, ui_color)

shoot_laser = pygame.USEREVENT
pygame.time.set_timer(shoot_laser, 400)

extra_point_alien = pygame.USEREVENT + 1
pygame.time.set_timer(extra_point_alien, random.randint(4000, 8000))

# Game loop
running = True
while running:
    # --- LECTURA DE COMANDOS ARDUINO ---
    if arduino and arduino.in_waiting > 0:
        try:
            comando = arduino.readline().decode('utf-8').strip()
            if app_state == 'playing' and game.run and not paused:
                nave = game.spaceship_group.sprite
                
                # Movimiento lateral
                if comando == "L":
                    nave.rect.x -= 10
                elif comando == "R":
                    nave.rect.x += 10
                
                # DISPARO (Lógica integrada de spaceship.py)
                elif comando == "F":
                    if nave.laser_ready:
                        nave.laser_ready = False
                        # Creamos el láser usando los parámetros de tus amigos
                        laser = Laser(nave.rect.center, 5, 255, 255, 255, nave.screen_height)
                        nave.lasers_group.add(laser)
                        nave.laser_time = pygame.time.get_ticks()
                
                # Mantener dentro de bordes
                if nave.rect.left < offset:
                    nave.rect.left = offset
                if nave.rect.right > screen_width:
                    nave.rect.right = screen_width
        except:
            pass
    # ----------------------------------
    for event in pygame.event.get():

        # Overlay oscuro para resaltar menus
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        if event.type == pygame.QUIT:
            running = False

        # Timers: solo aplican mientras jugamos
        if event.type == shoot_laser and game.run and app_state == 'playing' and not paused:
            game.alien_shoot_laser()

        if event.type == extra_point_alien and game.run and app_state == 'playing' and not paused:
            game.create_extra_point()
            pygame.time.set_timer(extra_point_alien, random.randint(4000, 8000))

        # Mouse clicks: manejar botones del menú y otros
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if app_state == 'menu':
                # Botones centrados
                start_rect = pygame.Rect(362, 260, 300, 60)
                highs_rect = pygame.Rect(362, 340, 300, 60)
                quit_rect = pygame.Rect(362, 420, 300, 60)
                if start_rect.collidepoint(mx, my):
                    #Empezar música
                    pygame.mixer.music.load("sounds/music.ogg")
                    pygame.mixer.music.play(-1)
                    game.reset()
                    app_state = 'playing'
                elif highs_rect.collidepoint(mx, my):
                    app_state = 'highscores'
                elif quit_rect.collidepoint(mx, my):
                    running = False
            elif app_state == 'highscores':
                back_rect = pygame.Rect(900, 720, 100, 40)
                if back_rect.collidepoint(mx, my):
                    app_state = 'menu'
            elif app_state == 'playing' and not game.run:
                # Cuando murio y ya guardo el nombre, mostrar volver al menu
                menu_rect = pygame.Rect(400, 500, 300, 60)
                if menu_rect.collidepoint(mx, my) and not game.await_highscore:
                    game.reset()
                    app_state = 'menu'

        # Input para nombre de highscore cuando se perdió el juego
        if event.type == pygame.KEYDOWN and not game.run and game.await_highscore:
            if event.key == pygame.K_RETURN:
                player_name = name_input.strip() or "ANON"
                game.add_score(player_name)
                name_input = ""
            elif event.key == pygame.K_BACKSPACE:
                name_input = name_input[:-1]
            else:
                if len(name_input) < 12 and event.unicode.isprintable():
                    name_input += event.unicode

        # Teclas generales: manejar KEYDOWN para evitar repeticiones al mantener la tecla
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if app_state == 'highscores':
                    app_state = 'menu'
                elif app_state == 'playing':
                    # Alternar pausa durante la partida
                    paused = not paused
                else:
                    running = False
            elif event.key == pygame.K_b and app_state == 'playing' and paused:
                # Reanudar con tecla 'b' (botón azul)
                paused = False
            elif event.key == pygame.K_SPACE and app_state == 'playing' and game.run == False and not game.await_highscore:
                # Reiniciar partida con SPACE cuando esté en pantalla de game over
                game.reset()
    
    if game.run and not paused:

        # Actualizar estados (no actualizar si estamos en pausa)
        game.spaceship_group.update()
        game.move_aliens()
        game.alien_lasers_group.update()
        game.extra_point_group.update()
        game.check_for_collisions()

    screen.fill((40, 40, 40))

    # Bordes de la UI
    pygame.draw.rect(screen, ui_color, (12, 10, 1050, 840), 2, 0, 60, 60, 60, 60)
    pygame.draw.line(screen, ui_color, (25, 770), (1045, 770), 3)

    if app_state == 'menu':
        # Botones
        start_rect = pygame.Rect(((screen_width + offset) - 320) // 2, 260, 320, 60)
        highs_rect = pygame.Rect(((screen_width + offset) - 320) // 2, 340, 320, 60)
        quit_rect = pygame.Rect(((screen_width + offset) - 320) // 2, 420, 320, 60)

        pygame.draw.rect(screen, ui_color, start_rect, 2)
        pygame.draw.rect(screen, ui_color, highs_rect, 2)
        pygame.draw.rect(screen, ui_color, quit_rect, 2)

        title = font.render("Space Invaders", False, ui_color)
        title_rect = title.get_rect(
            centerx=start_rect.centerx,
            bottom=start_rect.top - 30
        )
        screen.blit(title, title_rect)

        start_text = font.render("Nueva Partida", False, ui_color)
        highs_text = font.render("Mejores Puntajes", False, ui_color)
        quit_text  = font.render("Salir", False, ui_color)

        screen.blit(start_text, start_text.get_rect(center=start_rect.center))
        screen.blit(highs_text, highs_text.get_rect(center=highs_rect.center))
        screen.blit(quit_text,  quit_text.get_rect(center=quit_rect.center))

        # (Mini Top10 eliminado del menú — disponible solo en 'High Scores')

    elif app_state == 'highscores':
        title = font.render("Mejores Puntajes", False, ui_color)
        center_x = (screen_width + offset) // 2
        screen.blit(title, title.get_rect(center=(center_x, 80)))
        highs = game.load_highscores()[:10]
        for i, entry in enumerate(highs):
            line = small_font.render(f"{i+1}. {entry.get('name','')} - {entry.get('score',0)}", False, ui_color)
            screen.blit(line, line.get_rect(center=(center_x, 180 + i*40)))

        back_rect = pygame.Rect(900, 720, 100, 40)
        pygame.draw.rect(screen, ui_color, back_rect, 2)
        screen.blit(small_font.render("Volver", False, ui_color), (910, 730))

    elif app_state == 'playing':
        # Texto de nivel y game over
        if game.run:
            level_surface = font.render(f"NIVEL {game.level:02d}", False, ui_color)
            screen.blit(level_surface, (850, 785, 50, 50))
        else:
            if game.mission_completed:
                screen.blit(mission_surface, (300, 200))
                screen.blit(congrats_surface, (300, 270))
            else:
                screen.blit(game_over, (750, 785, 50, 50))
        # Si estamos esperando nombre, mostrar input
        if game.await_highscore:
            screen.blit(overlay, (0, 0))
            prompt = small_font.render("Ingresa nombre (ENTER para guardar):", False, ui_color)
            input_surf = small_font.render(name_input, False, ui_color)
            screen.blit(prompt, (50, 150))
            screen.blit(input_surf, (50, 190))
        else:
            # No mostrar top10 durante la partida; solo mostrar prompt o botón volver al menú
            pass

    # Texto y puntaje
    screen.blit(score_text, (50, 15, 50, 50))
    formatted_score = str(game.score).zfill(5)
    score_surface = font.render(formatted_score, False, ui_color)
    screen.blit(score_surface, (50, 40, 50, 50))

    # Texto y mayor puntaje
    screen.blit(highscore_text, (900, 15, 50, 50))
    formatted_highscore = str(game.highscore).zfill(5)
    highscore_surface = font.render(formatted_highscore, False, ui_color)
    screen.blit(highscore_surface, (900, 40, 50, 50))

    # Vidas
    heart_offset_x = 60
    heart_y = 785

    for i in range(game.max_lives):
        if i < game.lives:
            screen.blit(game.heart, (heart_offset_x, heart_y))
        else:
            screen.blit(game.no_heart, (heart_offset_x, heart_y))

        heart_offset_x += 60

    # Dibujar en la ventana los objetos (solo si estamos jugando)
    if app_state == 'playing':
        game.spaceship_group.draw(screen)
        game.spaceship_group.sprite.lasers_group.draw(screen)
        game.shields_group.draw(screen)
        game.aliens_group.draw(screen)
        game.alien_lasers_group.draw(screen)
        game.extra_point_group.draw(screen)

        # Si está en pausa, mostrar overlay y mensaje central
        if paused:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            paused_surf = font.render("PAUSADO", False, ui_color)
            subtitle = small_font.render("Preciona el boton azul para continuar", False, ui_color)
            screen.blit(paused_surf, paused_surf.get_rect(center=( (screen_width + offset)//2, (screen_height)//2 - 20 )))
            screen.blit(subtitle, subtitle.get_rect(center=( (screen_width + offset)//2, (screen_height)//2 + 30 )))

        # Si estamos muertos y esperando nombre, dibujar prompt
        if not game.run:
            # Detener música
            pygame.mixer.music.stop()
            if game.await_highscore:
                screen.blit(overlay, (0, 0))
                prompt = small_font.render("Ingresa nombre (ENTER para guardar):", False, ui_color)
                input_surf = small_font.render(name_input, False, ui_color)
                screen.blit(prompt, (50, 150))
                screen.blit(input_surf, (50, 190))
            else:
                # Mostrar botón volver al menu
                menu_rect = pygame.Rect(400, 500, 300, 60)
                pygame.draw.rect(screen, ui_color, menu_rect, 2)
                screen.blit(font.render("Volver al menu", False, ui_color), (420, 510))

    pygame.display.update()
    # FPS
    clock.tick(60)

if arduino:
    arduino.close()
pygame.quit()
