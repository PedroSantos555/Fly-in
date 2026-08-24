import pygame
import sys
import pygame.locals as loc
from typing import Any, List
from fly_parser import parser_file
from baseclasses import Set_Up, Camera, Drone
from collections import Counter

from scheduler import *

def replace_color_in_square(surface, old_color, new_color,
                            x, y, width, height):

    img_copy = surface.copy()

    # 1. Define o quadrado/área restrita dentro do sprite
    target_rect = pygame.Rect(x, y, width, height)

    # 2. Cria uma subsuperfície que partilha os píxeis da cópia,
    # mas isola a área
    sub_surface = img_copy.subsurface(target_rect)

    # 3. Aplica o PixelArray apenas nesta subsuperfície
    pixel_array = pygame.PixelArray(sub_surface)
    pixel_array.replace(old_color, new_color)

    # 4. Liberta o array para aplicar as alterações na imagem final
    del pixel_array

    return img_copy


def execute_turn(drones: List[Drone], n_turn: int) -> None:

    for drone in drones:
        if drone.script.get(n_turn) is not None:
            new_pos = drone.script.get(n_turn)
            drone.sprite.move(new_pos[0], new_pos[1])


class Display:

    drone_sprites = []
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

        camera = Camera()
        self.setup = setup
        show_connections = False
        FPS = 60
        pygame.font.init()
        FramePerSec = pygame.time.Clock()
        pygame.display.set_caption("Fly-in")
        width = 1920
        height = 1080
        pygame.init()
        disp_surface = pygame.display.set_mode((width, height))
        disp_surface.fill(self.oblue)
        fps = pygame.time.Clock()
        fps.tick(60)
        turn = 0

        for hub in setup.hubs.values():
            hub.sprite.draw(disp_surface, camera)
            self.hub_sprites.append(hub.sprite)

        for drone in setup.drones:
            self.drone_sprites.append(drone.sprite)

        while (True):

            for event in pygame.event.get():
                if event.type == loc.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_n:
                        execute_turn(setup.drones, turn)
                        turn += 1

                    if event.key == pygame.K_p:

                        show_connections = not show_connections

                    if event.key == pygame.K_1:
                        for sprite in self.hub_sprites:
                            if sprite.size != 0.5:
                                sprite.mini()

                        for drone in self.drone_sprites:
                            if drone.size != 0.5:
                                drone.mini()
                        camera.zoom = 0.5
                    if event.key == pygame.K_2:
                        for sprite in self.hub_sprites:
                            if sprite.size != 1:
                                sprite.medium()

                        for drone in self.drone_sprites:
                            if drone.size != 1:
                                drone.medium()

                        camera.zoom = 1

                    if event.key == pygame.K_3:
                        for sprite in self.hub_sprites:
                            if sprite.size != 2:
                                sprite.big()

                        for drone in self.drone_sprites:
                            if drone.size != 2:
                                drone.big()

                            camera.zoom = 2

            pressed_keys = pygame.key.get_pressed()

            if any([pressed_keys[loc.K_UP], pressed_keys[loc.K_DOWN],
                   pressed_keys[loc.K_RIGHT], pressed_keys[loc.K_LEFT]]):

                offset = [0, 0]

                
                if pressed_keys[loc.K_UP]:
                    offset[1] += 16
                if pressed_keys[loc.K_DOWN]:
                    offset[1] += -16
                if pressed_keys[loc.K_LEFT]:
                    offset[0] += 16
                if pressed_keys[loc.K_RIGHT]:
                    offset[0] += -16

                camera.move(-offset[0], -offset[1])

            disp_surface.fill(self.oblue)

            for sprite in self.hub_sprites:
                sprite.draw(disp_surface, camera)

            for sprite in self.drone_sprites:
                sprite.update(1/FPS)

            positions = Counter((drone.world_pos.x, drone.world_pos.y)
                                for drone in self.drone_sprites)

            for coords, count in positions.items():
                drone = next(d for d in self.drone_sprites
                             if d.world_pos.x == coords[0]
                             and d.world_pos.y == coords[1])

                drone.draw(disp_surface, camera)

                font = pygame.font.Font(None, int(36 * camera.zoom))
                text = font.render(str(count), True,
                                   (255, 255, 255))
                disp_surface.blit(text, drone.rect)

            if show_connections:
                self.draw_connections(disp_surface)
            
            

            pygame.display.update()
            FramePerSec.tick(FPS)
            
    
    
if __name__ == "__main__":

    setup = parser_file("01_the_impossible_dream.txt")
    # print(setup)
    # setup.drones[1].sprite.move(setup.hubs["final_torture5"])
    dsp = Display()
    dist, prev = shortest_path_calc(setup.hubs, setup.hubs["start"])
    schedule = Schedule(setup)
    schedule.schedule_drones()
    dsp.start_display(setup=setup)
    setup = parser_file("01_basic_capacity.txt")
    # print(setup)
    dsp = Display()
    dsp.start_display(setup=setup)
