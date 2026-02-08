import pygame

# Clase de los láseres
class Laser(pygame.sprite.Sprite):
    def __init__(self, position, speed, r, g, b, screen_height):
        super().__init__()
        # Valores de los láseres
        self.image = pygame.Surface((4, 15))
        self.image.fill((r, g, b))
        self.rect = self.image.get_rect(center = position)
        self.speed = speed
        self.screen_height = screen_height

    # Método para actualizar el movimiento de los láseres
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y > self.screen_height + 15 or self.rect.y < -10:
            # Print en la consola para testear que se eliminen los láseres correctamente al salir de la pantalla
            print("Killed")
            self.kill()