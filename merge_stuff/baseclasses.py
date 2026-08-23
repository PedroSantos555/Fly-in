from typing import List, Dict, Literal, Optional, Any
from pydantic import BaseModel, Field, model_validator
from pydantic import ValidationError, ConfigDict
import pygame


class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.zoom = 1

    def world_to_screen(self, world_pos) -> pygame.Vector2:
        return (world_pos - self.offset) * self.zoom

    def move(self, x, y) -> None:
        self.offset.x += x
        self.offset.y += y


HUB_COLORS = {
    "red": (255, 90, 90),
    "darkred": (210, 70, 70),
    "maroon": (190, 70, 70),
    "crimson": (255, 100, 130),
    "salmon": (255, 170, 155),

    "pink": (255, 210, 220),
    "hotpink": (255, 150, 205),
    "lightpink": (255, 215, 225),

    "orange": (255, 195, 90),
    "darkorange": (255, 180, 80),
    "coral": (255, 175, 145),
    "tomato": (255, 150, 125),

    "yellow": (255, 255, 100),
    "gold": (255, 235, 100),
    "khaki": (250, 245, 170),
    "lemon": (255, 255, 120),

    "green": (100, 190, 100),
    "lime": (120, 255, 120),
    "darkgreen": (80, 170, 80),
    "forestgreen": (90, 190, 110),
    "seagreen": (100, 190, 145),
    "olive": (180, 180, 80),
    "mint": (180, 255, 190),

    "blue": (90, 150, 255),
    "darkblue": (80, 100, 210),
    "navy": (80, 100, 190),
    "steelblue": (120, 175, 215),
    "skyblue": (160, 220, 255),
    "lightblue": (190, 230, 255),
    "midnightblue": (80, 90, 180),

    "cyan": (100, 255, 255),
    "darkcyan": (80, 190, 190),
    "teal": (80, 190, 180),
    "turquoise": (110, 240, 225),

    "purple": (180, 100, 210),
    "violet": (230, 160, 245),
    "indigo": (130, 100, 200),
    "plum": (235, 175, 225),
    "magenta": (255, 100, 255),
    "fuchsia": (255, 100, 255),

    "brown": (200, 110, 100),
    "chocolate": (235, 155, 90),
    "tan": (235, 205, 165),

    "black": (0, 0, 0),
    "gray": (180, 180, 180),
    "grey": (180, 180, 180),
    "silver": (215, 215, 215),
    "lightgray": (225, 225, 225),
    "lightgrey": (225, 225, 225),

    "white": (255, 255, 255),
    "snow": (255, 252, 252),
    "ivory": (255, 255, 245),
    "beige": (255, 245, 210),

    "transparent": (0, 0, 0),
}


def recolor_surface(surface, old_color, new_color):
    result = surface.copy()

    pixels = pygame.PixelArray(result)
    pixels.replace(old_color, new_color)
    del pixels

    return result


class sprite_hub(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color: str, type: str) -> None:
        super().__init__()
        self.world_pos = pygame.Vector2(
            128*x + 64,
            360 + 128*y
        )

        self.color = HUB_COLORS.get(color, (255, 0, 255))

        if type == "restricted":
            self.smallfile = "./assets/padRestricted_Small.png"
            self.mediumfile = "./assets/padRestricted_Medium.png"
            self.largefile = "./assets/padRestricted_Large.png"
        elif type == "blocked":
            self.smallfile = "./assets/padBlocked_Small.png"
            self.mediumfile = "./assets/padBlocked_Medium.png"
            self.largefile = "./assets/padBlocked_Large.png"
        elif type == "priority":
            self.smallfile = "./assets/padPrio_Small.png"
            self.mediumfile = "./assets/padPrio_Medium.png"
            self.largefile = "./assets/padPrio_Large.png"
        else:
            self.smallfile = "./assets/pad_Small.png"
            self.mediumfile = "./assets/pad_Medium.png"
            self.largefile = "./assets/pad_Large.png"

        image = pygame.image.load(
            self.mediumfile
            ).convert_alpha()

        self.image = recolor_surface(
            image,
            (180, 180, 180),
            self.color
        )
        self.rect = self.image.get_rect()
        self.size = 1

    def medium(self) -> None:
        image = pygame.image.load(
            self.mediumfile
            ).convert_alpha()

        self.image = recolor_surface(
            image,
            (180, 180, 180),
            self.color
        )

        self.rect = self.image.get_rect()
        self.size = 1

    def big(self) -> None:

        image = pygame.image.load(
            self.largefile
            ).convert_alpha()

        self.image = recolor_surface(
            image,
            (180, 180, 180),
            self.color
        )

        self.rect = self.image.get_rect()
        self.size = 2

    def mini(self) -> None:

        image = pygame.image.load(
                    self.smallfile
                    ).convert_alpha()

        self.image = recolor_surface(
            image,
            (180, 180, 180),
            self.color
        )

        self.rect = self.image.get_rect()
        self.size = 0.5

    def draw(self, surface: Any, camera: Camera) -> None:

        screen_pos = camera.world_to_screen(self.world_pos)
        self.rect.center = screen_pos
        surface.blit(self.image, self.rect)


class sprite_drone(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.world_pos = pygame.Vector2(
            128*x + 64,
            360 + 128*y
        )
        self.image = pygame.image.load("./assets/NewDrone_Medium.png")
        self.rect = self.image.get_rect()
        self.size = 1
        self.start_pos = self.world_pos.copy()
        self.target_pos = self.world_pos.copy()
        self.moving = False
        self.progress = 0.0
        self.speed = 0.0

    def medium(self) -> None:
        self.image = pygame.image.load("./assets/NewDrone_Medium.png")
        self.rect = self.image.get_rect()
        self.size = 1

    def big(self) -> None:

        self.image = pygame.image.load("./assets/NewDrone_Large.png")
        self.rect = self.image.get_rect()
        self.size = 2

    def mini(self) -> None:

        self.image = pygame.image.load("./assets/NewDrone_Small.png")
        self.rect = self.image.get_rect()
        self.size = 0.5

    def move(self, target_hub: Any) -> None:
        # HAVE TO CHANGE TO ALLOW FOR 2 TURN MOVES INTO RESTRICTED HUBS

        # WILL CHANGE TOWARDS A POSITION BASED SYSTEM
        # DRONES WILL CALCULATE AND THEN STORE THEIR WORLD_POS EACH TURN ACORDING TO THE SCHEDULE
        # AND THEN MOVE WILL WORK FROM THERE
        self.target_pos = pygame.Vector2(128*target_hub.x + 64,
                                         360 + 128*target_hub.y)
        self.progress = 0.0
        self.speed = self.start_pos.distance_to(self.target_pos)
        self.moving = True

    def draw(self, surface: Any, camera: Camera) -> None:
        screen_pos = camera.world_to_screen(self.world_pos)
        self.rect.center = screen_pos
        surface.blit(self.image, self.rect)

    def update(self, dt) -> None:

        if not self.moving:
            return

        distance = self.start_pos.distance_to(self.target_pos)

        self.progress += self.speed * self.size * dt / distance

        if self.progress >= 1:
            self.progress = 1
            self.moving = False

        self.world_pos = self.start_pos.lerp(self.target_pos,
                                             self.progress)


class Connection(BaseModel):
    start: str
    end: str
    max_links: Optional[int] = None
    reserve_timetable: Dict[int, int]

    @model_validator(mode="after")
    def valid_chk(self) -> None:
        if self.max_links < 0:
            raise ValidationError("max_links must be a positive int")

        return self


class Hub(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    kind: Literal["start_hub", "end_hub", "hub"] = "hub"
    name: str
    color: str = "none"
    x: int
    y: int
    max_drones: int = Field(default=1, ge=0)
    drones_landed: List[Any]
    status: Literal["normal", "restricted", "priority", "blocked"] = "normal"
    conects: List[Connection]
    reserve_timetable: Dict[int, int]
    sprite: sprite_hub


class Drone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: Hub
    sprite: sprite_drone
    move_request: list = Field(default_factory=list)

    @classmethod
    def from_hub(cls, hub: Hub) -> Any:
        return cls(
            position=hub,
            sprite=sprite_drone(hub.x, hub.y),
        )


class Set_Up(BaseModel):

    drones: List[Drone]
    hubs: Dict[str, Hub]
    connections: List[Connection]

    def structure_connections(self) -> None:

        for hub in self.hubs.values():
            for conetion in self.connections:
                if conetion.start == hub.name:
                    hub.conects.append(conetion)
                if conetion.end == hub.name:
                    hub.conects.append(conetion)

    @model_validator(mode="after")
    def valid_chk(self) -> None:
        starts = [h for h in self.hubs.values() if h.kind == "start_hub"]

        if len(starts) != 1:
            raise ValidationError("Expected exactly one start_hub")

        ends = [h for h in self.hubs.values() if h.kind == "end_hub"]

        if len(ends) != 1:
            raise ValidationError("Expected exactly one end_hub")

        coords = set()

        for hub in self.hubs.values():

            pos = (hub.x, hub.y)

            if pos in coords:
                raise ValidationError(
                    f"Duplicate coordinates {pos}"
                )

            coords.add(pos)
        return self
