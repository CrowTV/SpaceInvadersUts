import pygame

class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("sprites/escudo.png")
        self.rect = self.image.get_rect(topleft = (x, y))
        self.health = 12

    def destroy_shield(self):
        print(f"Escudo golpeado")
        self.health -= 1
        if self.health <= 0:
            self.kill()