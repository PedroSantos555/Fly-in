import pygame
import sys
import pygame.locals as loc
from typing import Any
from parser import parser_file
from baseclasses import Set_Up


def replace_color_in_square(surface, old_color, new_color,
                            x, y, width, height):

    img_copy = surface.copy()

    # 1. Define o quadrado/área restrita dentro do sprite
    target_rect = pygame.Rect(x, y, width, height)

    # 2. Cria uma subsuperfície que partilha os píxeis da cópia, mas isola a área
    sub_surface = img_copy.subsurface(target_rect)

    # 3. Aplica o PixelArray apenas nesta subsuperfície
    pixel_array = pygame.PixelArray(sub_surface)
    pixel_array.replace(old_color, new_color)

    # 4. Liberta o array para aplicar as alterações na imagem final
    del pixel_array

    return img_copy


class Display:

    hub_sprites = []
    white = (255, 255, 255)
    black = (0, 0, 0)
    oblue = (0, 119, 190)
    mygrey = (180, 180, 180)
    setup = None

    def draw_connections(self, surface: Any):
        if setup is None:
            return

        for hub in setup.hubs.values():
            start = hub.sprite.rect.center
            for connection in hub.conects:
                end = setup.hubs[connection.end].sprite.rect.center

                pygame.draw.line(surface=surface,
                                 start_pos=start,
                                 end_pos=end,
                                 width=2,
                                 color=self.black)

    def start_display(self, setup: Set_Up) -> None:

        self.setup = setup
        FPS = 60
        FramePerSec = pygame.time.Clock()
        pygame.display.set_caption("Fly-in")
        width = 1920
        height = 1080
        pygame.init()
        disp_surface = pygame.display.set_mode((width, height))
        disp_surface.fill(self.oblue)
        fps = pygame.time.Clock()
        fps.tick(60)

        for hub in setup.hubs.values():
            hub.sprite.draw(disp_surface)
            self.hub_sprites.append(hub.sprite)
            self.draw_connections(disp_surface)
        while (True):

            for event in pygame.event.get():
                if event.type == loc.QUIT:
                    pygame.quit()
                    sys.exit()
            pressed_keys = pygame.key.get_pressed()

            if any([pressed_keys[loc.K_UP], pressed_keys[loc.K_DOWN],
                   pressed_keys[loc.K_RIGHT], pressed_keys[loc.K_LEFT],
                   pressed_keys[loc.K_1], pressed_keys[loc.K_2],
                   pressed_keys[loc.K_3]]):

                disp_surface.fill(self.oblue)
                offset = [0, 0]

                if pressed_keys[loc.K_UP]:
                    offset[1] += 16
                if pressed_keys[loc.K_DOWN]:
                    offset[1] += -16
                if pressed_keys[loc.K_LEFT]:
                    offset[0] += 16
                if pressed_keys[loc.K_RIGHT]:
                    offset[0] += -16

                if pressed_keys[loc.K_1]:
                    for sprite in self.hub_sprites:
                        if sprite.size != 0.5:
                            sprite.mini()

                if pressed_keys[loc.K_2]:
                    for sprite in self.hub_sprites:
                        if sprite.size != 1:
                            sprite.medium()

                if pressed_keys[loc.K_3]:
                    for sprite in self.hub_sprites:
                        if sprite.size != 2:
                            sprite.big()

                for sprite in self.hub_sprites:
                    sprite.rect.move_ip(offset[0]*sprite.size,
                                        offset[1]*sprite.size)
                    sprite.draw(disp_surface)

            self.draw_connections(disp_surface)
            pygame.display.update()
            FramePerSec.tick(FPS)



if __name__ == "__main__":

    setup = parser_file("01_the_impossible_dream.txt")
    # print(setup)
    dsp = Display()
    dsp.start_display(setup=setup)
