import pygame
import settings

class TextBox:
    """input text box to enter text"""
    def __init__(self, prompt: str, center_pos: tuple[float, float]):
        self.screen = pygame.display.get_surface() # main screen for easy access

        self.rect = pygame.Rect(0,0,settings.WIDTH/settings.TEXT_BOX_WIDTH_SCALE,
                                settings.HEIGHT/settings.TEXT_BOX_HEIGHT_SCALE) # main input bar
        self.rect.center = center_pos

        font = pygame.font.Font(None, settings.TEXT_BOX_FONT_SIZE)
        self.prompt_text = font.render(prompt, True, settings.BLUE)          # text image
        self.prompt_rect = self.prompt_text.get_rect(bottomleft=self.rect.topleft) # text container
        self.prompt_rect.y -= settings.TEXT_BOX_TEXT_OFFSET

        self.input_font = pygame.font.Font(None, 50)
        self.input_content = ""  # player input string
    
    def update(self) -> bool:
        """draws and updates text box\n
        returns if a valid tilesize has been entered"""
        pygame.draw.rect(self.screen, settings.BLUE, self.rect.inflate(settings.TEXT_BOX_BORDER_WIDTH,
                                                                                  settings.TEXT_BOX_BORDER_WIDTH))
        pygame.draw.rect(self.screen, "white", self.rect)    # draw main input box
        self.screen.blit(self.prompt_text, self.prompt_rect) # draw box title

        # draw player input
        input_text = self.input_font.render(self.input_content, True, settings.BLUE)
        input_rect = input_text.get_rect(midleft=self.rect.midleft)
        input_rect.x += settings.TEXT_BOX_INPUT_OFFSET
        self.screen.blit(input_text, input_rect)

        if self.user_input(): # user pressed enter
            return self.input_content.isnumeric()
    
    def user_input(self) -> str:
        """user interaction with the text box"""        
        if not pygame.key.get_focused(): # no keys pressed
            return False

        for event in pygame.event.get(eventtype=pygame.KEYDOWN):
            if event.key == pygame.K_BACKSPACE:
                self.input_content = self.input_content[0:len(self.input_content)-1]
                continue
            elif event.key == pygame.K_SPACE:
                continue # ignore space bar
            elif event.key == pygame.K_RETURN:
                return True
            
            self.input_content += event.unicode
        
        return False