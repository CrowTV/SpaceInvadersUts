import pygame, random, json, os
from spaceship import Spaceship
from shield import Shield
from alien import Alien, ExtraPointAlien
from laser import Laser

class Game:
    def __init__(self, screen_width, screen_height, offset):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset = offset
        self.level = 1
        self.spaceship_group = pygame.sprite.GroupSingle()
        self.spaceship_group.add(Spaceship(self.screen_width, self.screen_height, self.offset))
        self.shields_group = pygame.sprite.Group()
        self.create_shields()
        self.aliens_group = pygame.sprite.Group()
        self.create_aliens()
        self.aliens_direction = 1
        self.alien_lasers_group = pygame.sprite.Group()
        self.extra_point_group = pygame.sprite.GroupSingle()
        self.max_lives = 3
        self.lives = self.max_lives
        self.heart = pygame.image.load("sprites/vida.png")
        self.no_heart = pygame.image.load("sprites/novida.png")
        self.run = True
        self.score = 0
        self.highscore = 0
        self.high_scores_file = "highscores.json"
        self.await_highscore = False
        self.mission_completed = False
        self.playing_music = False
        self.player_hit_sound = pygame.mixer.Sound("sounds/player_hit.ogg")
        self.enemy_killed = pygame.mixer.Sound("sounds/explosion.ogg")
        self.extra_points = pygame.mixer.Sound("sounds/extra_point.ogg")
        self.cooldown = 600

        # Cargar highscore desde el archivo al iniciar
        try:
            scores = self.load_highscores()
            if scores:
                self.highscore = scores[0].get("score", 0)
        except Exception:
            self.highscore = 0

    # Método para crear los aliens
    def create_aliens(self):
        # Creación de formaciones por nivel
        if self.level == 1:
            rows = 5
            columns = 11
            x_start = self.screen_width // 5.5
            x_spacing = 60
            y_start = 100

            for row in range(rows):
                for column in range(columns):
                    x = x_start + (column * x_spacing)
                    y = y_start + (row * 60)

                    if row == 0:
                        alien_type = 3
                    elif row in (1,2):
                        alien_type = 2
                    else:
                        alien_type = 1

                    alien = Alien(alien_type, x + self.offset / 2, y)
                    self.aliens_group.add(alien)

        elif self.level == 2:
            # Nivel 2: formación en rejilla escalonada (filas desplazadas)
            rows = 6
            columns = 10
            x_start = self.screen_width // 5
            x_spacing = 60
            y_start = 80

            for row in range(rows):
                row_offset = (row % 2) * (x_spacing // 2)
                for column in range(columns):
                    x = x_start + row_offset + (column * x_spacing)
                    y = y_start + (row * 55)

                    if row < 2:
                        alien_type = 3
                    elif row < 4:
                        alien_type = 2
                    else:
                        alien_type = 1

                    alien = Alien(alien_type, x + self.offset / 2, y)
                    self.aliens_group.add(alien)

        elif self.level == 3:
            # Nivel 3: formación en pirámide
            rows = 6
            base_columns = 11
            x_spacing = 60
            y_start = 100

            for row in range(rows):
                columns = base_columns - row * 2
                row_x_start = (self.screen_width + self.offset - (columns * x_spacing)) // 2
                for column in range(columns):
                    x = row_x_start + (column * x_spacing)
                    y = y_start + (row * 60)

                    if row == 0:
                        alien_type = 3
                    elif row <= 2:
                        alien_type = 2
                    else:
                        alien_type = 1

                    alien = Alien(alien_type, x + self.offset / 2, y)
                    self.aliens_group.add(alien)

        elif self.level == 4:
            # Nivel 4: rombo/diamante
            rows = 7
            max_columns = 7
            x_spacing = 60
            y_start = 70
            mid = rows // 2

            for row in range(rows):
                if row <= mid:
                    columns = 1 + row * 2
                else:
                    columns = 1 + (rows - row - 1) * 2

                row_width = columns * x_spacing
                row_x_start = (self.screen_width + self.offset - row_width) // 2
                for column in range(columns):
                    x = row_x_start + (column * x_spacing)
                    y = y_start + (row * 50)

                    if row < 2:
                        alien_type = 3
                    elif row < 4:
                        alien_type = 2
                    else:
                        alien_type = 1

                    alien = Alien(alien_type, x + self.offset / 2, y)
                    self.aliens_group.add(alien)

        elif self.level == 5:
            # Nivel 5: filas anchas y rápidas (desafío final)
            rows = 3
            columns = 13
            x_start = self.offset + 20
            x_spacing = 70
            y_start = 120

            for row in range(rows):
                for column in range(columns):
                    x = x_start + (column * x_spacing)
                    y = y_start + (row * 60)

                    # Hacer el centro más fuerte
                    center = columns // 2
                    distance_from_center = abs(column - center)
                    if distance_from_center < 2 and row == 0:
                        alien_type = 3
                    elif row == 0 or row == 1:
                        alien_type = 2
                    else:
                        alien_type = 1

                    alien = Alien(alien_type, x + self.offset / 2, y)
                    self.aliens_group.add(alien)

        else:
            # Fallback: nivel 1
            rows = 5
            columns = 11
            x_start = self.screen_width // 5.5
            x_spacing = 60
            y_start = 100

            for row in range(rows):
                for column in range(columns):
                    x = x_start + (column * x_spacing)
                    y = y_start + (row * 60)

                    if row == 0:
                        alien_type = 3
                    elif row in (1, 2):
                        alien_type = 2
                    else:
                        alien_type = 1

                    alien = Alien(alien_type, x + self.offset / 2, y)
                    self.aliens_group.add(alien)

    # Método para mover los aliens de un lado a otro cuando llegan a los bordes de la ventana
    def move_aliens(self):
        # Velocidad horizontal aumentada según nivel
        speed = int(self.aliens_direction * (1 + (self.level - 1) * 0.6))
        if speed == 0:
            speed = self.aliens_direction
        self.aliens_group.update(speed)

        alien_sprites = self.aliens_group.sprites()
        for alien in alien_sprites:
            if alien.rect.right >= self.screen_width + self.offset / 2:
                self.aliens_direction = -1
                self.alien_move_down(2 + (self.level - 1))
            elif alien.rect.left <= self.offset / 2:
                self.aliens_direction = 1
                self.alien_move_down(2 + (self.level - 1))

    # Metodo para mover los aliens hacia abajo
    def alien_move_down(self, distance):
        if self.aliens_group:
            for alien in self.aliens_group.sprites():
                alien.rect.y += distance

    # Método del disparo de los aliens
    def alien_shoot_laser(self):
        if self.aliens_group.sprites():
            random_alien = random.choice(self.aliens_group.sprites())
            laser_sprite = Laser(random_alien.rect.center, -6, 200, 0, 0, self.screen_height)
            self.alien_lasers_group.add(laser_sprite)

    # Método para crear los escudos espaciados
    def create_shields(self):
        cantidad = 6
        y = self.screen_height - self.screen_height // 5

        temp_shield = Shield(0, 0)
        shield_width = temp_shield.image.get_width()

        temp_shield.kill()

        espacio_total = self.screen_width + self.offset - cantidad * shield_width
        espacio_entre = espacio_total // (cantidad + 1)

        for i in range(cantidad):
            x = espacio_entre + i * (shield_width + espacio_entre)
            self.shields_group.add(Shield(x, y))

    def create_extra_point(self):
        self.extra_point_group.add(ExtraPointAlien(self.screen_width, self.offset))

    def check_for_collisions(self):
        # Colisiones de la nave
        if self.spaceship_group.sprite.lasers_group:
            for laser_sprite in self.spaceship_group.sprite.lasers_group:

                aliens_hit = pygame.sprite.spritecollide(laser_sprite, self.aliens_group, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.type * 100
                        self.enemy_killed.play()
                        self.check_for_highscore()
                        laser_sprite.kill()

                if pygame.sprite.spritecollide(laser_sprite, self.extra_point_group, True):
                    self.score += 500
                    self.extra_points.play()
                    self.check_for_highscore()
                    laser_sprite.kill()

                hits = pygame.sprite.spritecollide(
                    laser_sprite,
                    self.shields_group,
                    False
                )

                for shield in hits:
                    shield.destroy_shield()
                    laser_sprite.kill()
                
        #Colisiones de Alien
        if self.alien_lasers_group:
            for laser_sprite in self.alien_lasers_group:
                if pygame.sprite.spritecollide(laser_sprite, self.spaceship_group, False):
                    self.player_hit_sound.play()
                    laser_sprite.kill()
                    print(f"Jugador golpeado")
                    self.lives -= 1
                    if self.lives == 0:
                        self.game_over()
                
                hits = pygame.sprite.spritecollide(
                    laser_sprite,
                    self.shields_group,
                    False
                )

                for shield in hits:
                    shield.destroy_shield()
                    laser_sprite.kill()

        if self.aliens_group:
            for alien in self.aliens_group:
                pygame.sprite.spritecollide(alien, self.shields_group, True)

                if pygame.sprite.spritecollide(alien, self.spaceship_group, False):
                    print(f"Jugador golpeado por alien")
                    self.game_over()

        # Si no quedan aliens, pasa al siguiente nivel
        if not self.aliens_group:
            self.next_level()

    def game_over(self):
        self.run = False
        self.await_highscore = True
        print("Game over - awaiting highscore name input")

    def reset(self):
        self.run = True
        self.lives = 3
        self.spaceship_group.sprite.reset()
        self.aliens_group.empty()
        self.alien_lasers_group.empty()
        self.level = 1
        self.create_aliens()
        self.extra_point_group.empty()
        self.create_shields()
        self.score = 0
        self.await_highscore = False
        self.mission_completed = False
    def check_for_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score

    def load_highscores(self):
        if os.path.exists(self.high_scores_file):
            try:
                with open(self.high_scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_highscores(self, scores):
        try:
            with open(self.high_scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving highscores: {e}")

    def add_score(self, name):
        name = (name or "ANON").strip()[:10]
        scores = self.load_highscores()
        scores.append({"name": name, "score": self.score})
        scores = sorted(scores, key=lambda s: s.get("score", 0), reverse=True)[:10]
        self.save_highscores(scores)
        # update in-memory highscore
        if scores:
            self.highscore = scores[0].get("score", 0)
        self.await_highscore = False

    def next_level(self):
        # Avanza de nivel hasta 5 y genera una nueva formación
        if self.level < 5:
            self.level += 1
            self.aliens_group.empty()
            self.alien_lasers_group.empty()
            self.extra_point_group.empty()
            self.create_shields()
            self.create_aliens()
        else:
            # Nivel 5 completado -> misión completada
            self.mission_completed = True
            self.run = False
            # Pedimos nombre de highscore al completar la misión
            self.await_highscore = True