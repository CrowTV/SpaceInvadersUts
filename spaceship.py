import pygame
from laser import Laser

# Clase de la nave
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, offset):
        super().__init__()
        # Valores de la nave
        self.offset = offset
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = pygame.image.load("sprites/nave.png")
        self.original_image = self.image.copy()
        # Invulnerabilidad / parpadeo
        self.invulnerable = False
        self.invulnerable_start = 0
        self.invulnerable_duration = 1000  # ms
        self.blink_interval = 120  # ms
        self.visible = True
        self.rect = self.image.get_rect(midbottom = ((self.screen_width + self.offset) / 2, self.screen_height))
        self.speed = 6
        self.lasers_group = pygame.sprite.Group()
        self.laser_ready = True
        self.laser_time = 0
        self.laser_delay = 500
        self.laser_sound = pygame.mixer.Sound("sounds/laser.ogg")

    # Método para obtener los inputs del jugador
    def get_user_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.laser_ready:
            self.laser_ready = False
            laser = Laser(self.rect.center, 5, 255, 255, 255, self.screen_height)
            self.lasers_group.add(laser)
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    # Método para actualizar todos los estados de la nave
    def update(self):
        self.get_user_input()
        self.constrain_movement()
        self.lasers_group.update()
        self.recharge_laser()
        # Manejar parpadeo si está invulnerable
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.invulnerable_start
            if elapsed >= self.invulnerable_duration:
                # Termina invulnerabilidad
                self.invulnerable = False
                self.visible = True
                self.image = self.original_image
            else:
                # Alternar visibilidad según intervalo
                show = ((elapsed // self.blink_interval) % 2) == 0
                if show and not self.visible:
                    self.visible = True
                    self.image = self.original_image
                elif not show and self.visible:
                    self.visible = False
                    # Imagen transparente del mismo tamaño
                    blank = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
                    self.image = blank

    # Método para mantener la nave dentro de los límites de la ventana
    def constrain_movement(self):
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        
        if self.rect.left < self.offset:
            self.rect.left = self.offset

    def recharge_laser(self):
        if not self.laser_ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_delay:
                self.laser_ready = True

    def reset(self):
        self.rect = self.original_image.get_rect(midbottom = ((self.screen_width + self.offset) / 2, self.screen_height))
        self.lasers_group.empty()
        # Reset invulnerability
        self.invulnerable = False
        self.visible = True
        self.image = self.original_image

    def start_invulnerability(self):
        self.invulnerable = True
        self.invulnerable_start = pygame.time.get_ticks()
        self.visible = True