import os
from os import walk
import pygame

from tile_types import PalleteImage, GridTile
from text_box import TextBox
import settings

class TilemapMaker:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("tilemap maker by costott")
        self.clock = pygame.time.Clock()

        self.tilesize: int = None
        self.columns: int = None 
        self.rows: int = None

        self.get_tile_images()

        # ERRORS    
        self.main_error_text = pygame.font.Font(None, 75).render("NO IMAGES IN TILE_IMAGES", True, "white")
        self.main_error_rect = self.main_error_text.get_rect(midbottom = (settings.WIDTH/2, settings.HEIGHT/2))
        self.minor_error_text = pygame.font.Font(None, 40).render("add your tiles to the 'tile_images' folder", True, "white")
        self.minor_error_rect = self.minor_error_text.get_rect(midtop = self.main_error_rect.midbottom)

        self.tilesize_text_box = TextBox("Enter your tilesize (for display purposes only): ", (settings.WIDTH/2, settings.HEIGHT/2))
        self.columns_text_box = TextBox("Enter the number of tiles of the width: ", (settings.WIDTH/2, settings.HEIGHT/2))
        self.rows_text_box = TextBox("Enter the number of tiles of the height: ", (settings.WIDTH/2, settings.HEIGHT/2))

        # ACTIVE TILE
        self.active_index = None
        self.active_tile_image = None # active tile selected to be put on the screen
        self.clicked = False
        
        # TILE PALLETE
        self.tile_pallete_y_offset = 0
        self.tile_pallete_y_offset_scroll_speed = 10_000
    
    def get_tile_images(self) -> None:
        """gets the tile images out of th tile_images folder"""
        self.images = [[pygame.image.load(f"tile_images/{img}").convert_alpha() 
                        for img in images]
                        for _, __, images in walk("tile_images")][0]
    
    def run(self) -> None:
        """run the maker"""
        while 1:
            self.update()
            self.clock.tick(settings.TARGET_FPS)
    
    def update(self) -> None:
        """called once per frame"""
        for event in pygame.event.get(exclude=pygame.KEYDOWN):
            if event.type == pygame.QUIT:
                self.exit_tilemap_maker()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.tile_pallete_y_offset += self.tile_pallete_y_offset_scroll_speed * 1/self.clock.get_fps()
                if event.button == 5:
                    self.tile_pallete_y_offset -= self.tile_pallete_y_offset_scroll_speed * 1/self.clock.get_fps()
                
                self.tile_pallete_y_offset = min(self.tile_pallete_y_offset, 0)

        self.screen.fill('black')

        if len(self.images) == 0:
            self.screen.blit(self.main_error_text, self.main_error_rect)
            self.screen.blit(self.minor_error_text, self.minor_error_rect)
            pygame.display.update()
            return
        
        #  SETUP
        if self.tilesize == None:
            if self.tilesize_text_box.update():
                self.tilesize = int(self.tilesize_text_box.input_content)
                self.images = [pygame.transform.scale(image, (self.tilesize, self.tilesize)) for image in self.images]
                self.make_pallete_sprites()
            pygame.display.update()
            return
        if self.columns == None:
            if self.columns_text_box.update():
                self.columns = int(self.columns_text_box.input_content)
            pygame.display.update()
            return
        if self.rows == None:
            if self.rows_text_box.update():
                self.rows = int(self.rows_text_box.input_content)
                self.make_grid()
                pygame.display.set_caption("tilemap maker by costott - exit to generate tilemap (stored at tilemap.txt)")
            pygame.display.update()
            return
        
        # ACTUAL THING
        # draw and update grid
        self.grid_sprites.update(self.screen, self.clock, self.active_tile_image, self.active_index)

        # draw pallete
        pygame.draw.rect(self.screen, settings.BLUE, (settings.TILE_PALLETE_X, 0, settings.WIDTH-settings.TILE_PALLETE_X, settings.HEIGHT))
        for sprite in self.pallete_sprites: sprite.draw(self.screen, self.tile_pallete_y_offset)


        # CHANGING ACTIVE 
        self.change_active_tile()

        # draw active image
        if self.active_tile_image != None:
            self.active_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.active_tile_image, self.active_rect)

        pygame.display.update()

    def change_active_tile(self):
        if not self.clicked:
            # check for new pallete clicked
            for i, sprite in enumerate(self.pallete_sprites):
                if i == self.active_index: continue
                if sprite.update(self.tile_pallete_y_offset):
                    self.active_index = i
                    self.active_tile_image = self.images[i]
                    self.active_rect = self.active_tile_image.get_rect()
                    self.clicked = True
                    break
        if self.clicked and not pygame.mouse.get_pressed()[0]: self.clicked = False
    
    def make_pallete_sprites(self) -> None:
        """makes the sprites for the pallete"""
        self.pallete_sprites = pygame.sprite.Group()
        gap = self.tilesize * settings.IMAGE_GAP_SCALE
        tiles_per_row = int((settings.WIDTH-settings.TILE_PALLETE_X)/(self.tilesize+gap))
        row = 0
        col = 0
        for i, image in enumerate(self.images):
            x = settings.TILE_PALLETE_X + gap + col*(self.tilesize+gap)
            y = gap + row*(self.tilesize+gap)
            PalleteImage([self.pallete_sprites], image, (x,y), i)

            col += 1
            if col >= tiles_per_row: 
                col = 0
                row += 1

    def make_grid(self) -> None:
        """makes the grid for sprites to be on"""
        self.grid_sprites = GridSpriteGroup(self.rows, self.columns, self.tilesize)
        for i in range(self.rows):
            for j in range(self.columns):
                x = settings.PADDING + j*self.tilesize
                y = settings.PADDING + i*self.tilesize
                GridTile([self.grid_sprites], (x,y), self.tilesize)
    
    def exit_tilemap_maker(self) -> None:
        """exits the tilemap maker"""
        if self.rows == None: exit()

        with open("tilemap.txt", "w+") as f:
            current_row_count = 0
            row_string = ""
            for _, tile in enumerate(self.grid_sprites):
                if tile.index == None: row_string += "-1"
                else: row_string += str(tile.index)
                row_string += ", "

                current_row_count += 1
                if current_row_count == self.columns:
                    f.write(row_string + "\n")
                    row_string = ""
                    current_row_count = 0
            
        exit()

class GridSpriteGroup(pygame.sprite.Group):
    """sprite group for grid sprites"""
    def __init__(self, rows: int, columns: int, tilesize: int):
        super().__init__()

        self.rows = rows
        self.columns = columns
        self.tilesize = tilesize

        self.camera_offset = pygame.math.Vector2(0,0)
        self.camera_move_speed = 100
    
    def update(self, screen: pygame.Surface, clock: pygame.time.Clock, active_tile_image: pygame.Surface, active_index: int) -> None:
        """draws+updates grid sprites"""
        self.move_camera(clock)
        for sprite in self.sprites():
            sprite.update(active_tile_image, active_index, self.camera_offset)
            sprite.draw(screen, self.camera_offset)
    
    def move_camera(self, clock: pygame.time.Clock) -> None:
        """Moves camera based on WASD movement"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.camera_offset.y += self.camera_move_speed * 1/clock.get_fps()
        if keys[pygame.K_s]:
            self.camera_offset.y -= self.camera_move_speed * 1/clock.get_fps()
        if keys[pygame.K_a]:
            self.camera_offset.x += self.camera_move_speed * 1/clock.get_fps()
        if keys[pygame.K_d]:
            self.camera_offset.x -= self.camera_move_speed * 1/clock.get_fps()
        
        self.camera_offset.x = min(self.camera_offset.x, 0)
        self.camera_offset.x = max(self.camera_offset.x, -(self.tilesize*self.columns - (settings.TILE_PALLETE_X-settings.PADDING*2)))
        self.camera_offset.y = min(self.camera_offset.y, 0)
        self.camera_offset.y = max(self.camera_offset.y, -(self.tilesize*self.rows - (settings.HEIGHT-settings.PADDING*2)))

def main():
    TilemapMaker().run()

if __name__ == "__main__":
    main()