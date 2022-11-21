import pygame

import settings

class PalleteImage(pygame.sprite.Sprite):
    def __init__(self, groups: list[pygame.sprite.Group], image: pygame.Surface, pos: tuple[float, float], i: int):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pygame.math.Vector2(pos)

        self.i = i
        self.index_text = pygame.font.Font(None, int(self.rect.height/3)).render(f"{i}", True, 'black')
        self.index_rect = self.index_text.get_rect()

    def draw(self, surface: pygame.Surface, scroll: float)  -> None:
        """draw pallete sprite to screen"""
        temp_rect = self.rect.copy()
        temp_rect.y += scroll
        surface.blit(self.image, temp_rect)

        self.index_rect.center = temp_rect.center
        surface.blit(self.index_text, self.index_rect)
    
    def update(self, scroll: float) -> bool:
        """called once per frame\n
        returns whether it's been clicked"""
        if not pygame.mouse.get_pressed()[0]: return False
        
        temp_rect = self.rect.copy()
        temp_rect.y += scroll
        return temp_rect.collidepoint(pygame.mouse.get_pos())

class GridTile(pygame.sprite.Sprite):
    def __init__(self, groups: list[pygame.sprite.Group], pos: tuple[float, float], tilesize: int):
        super().__init__(groups)
        self.rect = pygame.rect.Rect(pos[0], pos[1], tilesize, tilesize)
        self.pos = pygame.math.Vector2(pos)

        self.image = None
        self.index = None # index of tile image on current position
    
    def draw(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2) -> None:
        """draw grid tile to surface"""
        temp_rect = self.rect.copy()
        temp_rect.topleft += camera_offset
        pygame.draw.rect(surface, 'white', temp_rect, width=1)
        if self.image != None: surface.blit(self.image, self.pos+camera_offset)
    
    def update(self, active_tile_image: pygame.Surface, active_tile_index: int, camera_offset: pygame.math.Vector2()) -> None:
        """called once per frame"""
        temp_rect = self.rect.copy()
        temp_rect.topleft += camera_offset

        if pygame.mouse.get_pressed()[2]: # delete
            if temp_rect.collidepoint(pygame.mouse.get_pos()):
                self.image = None
                self.index = None

        if not pygame.mouse.get_pressed()[0]: return
        if not temp_rect.collidepoint(pygame.mouse.get_pos()): return

        self.index = active_tile_index
        self.image = active_tile_image