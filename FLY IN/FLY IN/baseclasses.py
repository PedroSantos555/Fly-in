from typing import List, Dict, Literal, Optional, Any
from pydantic import BaseModel, Field, model_validator
from pydantic import ValidationError, ConfigDict
import pygame


class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.zoom = 1

    def world_to_screen(self, world_pos):
        return (world_pos - self.offset) * self.zoom

    def move(self, x, y):
        self.offset.x += x
        self.offset.y += y


class sprite_hub(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.world_pos = pygame.Vector2(
            128*x + 64,
            360 + 128*y
        )
        self.image = pygame.image.load("./assets/drone_pad_medium.png")
        self.rect = self.image.get_rect()
        self.size = 1

    def medium(self) -> None:
        self.image = pygame.image.load("./assets/drone_pad_medium.png")
        self.rect = self.image.get_rect()
        self.size = 1

    def big(self) -> None:

        self.image = pygame.image.load("./assets/drone_pad_large.png")
        self.rect = self.image.get_rect()
        self.size = 2

    def mini(self) -> None:

        self.image = pygame.image.load("./assets/drone_pad.png")
        self.rect = self.image.get_rect()
        self.size = 0.5

    def draw(self, surface: Any, camera: Camera) -> None:
        screen_pos = camera.world_to_screen(self.world_pos)
        self.rect.center = screen_pos
        surface.blit(self.image, self.rect)


class sprite_drone(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.world_pos = pygame.Vector2(
            128*x + 64,
            360 + 128*y
        )
        self.image = pygame.image.load("./assets/Drone_Medium.png")
        self.rect = self.image.get_rect()
        self.size = 1
        self.start_pos = self.world_pos.copy()
        self.target_pos = self.world_pos.copy()
        self.moving = False
        self.progress = 0.0

    def medium(self) -> None:
        self.image = pygame.image.load("./assets/Drone_Medium.png")
        self.rect = self.image.get_rect()
        self.size = 1

    def big(self) -> None:

        self.image = pygame.image.load("./assets/Drone_Large.png")
        self.rect = self.image.get_rect()
        self.size = 2

    def mini(self) -> None:

        self.image = pygame.image.load("./assets/Drone_Small.png")
        self.rect = self.image.get_rect()
        self.size = 0.5

    def move(self, target_hub: Any):
        self.target_pos = pygame.Vector2(128*target_hub.x + 64,
                                         360 + 128*target_hub.y)
        self.progress = 0.0
        self.moving = True

    def draw(self, surface: Any, camera: Camera) -> None:
        screen_pos = camera.world_to_screen(self.world_pos)
        self.rect.center = screen_pos
        surface.blit(self.image, self.rect)

    def update(self, dt):

        if not self.moving:
            return

        distance = self.start_pos.distance_to(self.target_pos)

        self.progress += 250 * self.size * dt / distance

        if self.progress >= 1:
            self.progress = 1
            self.moving = False

        self.world_pos = self.start_pos.lerp(self.target_pos,
                                             self.progress)


class Connection(BaseModel):
    start: str
    end: str
    max_links: Optional[int] = None

    @model_validator(mode="after")
    def valid_chk(self):
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
    sprite: sprite_hub


class Drone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: Hub
    sprite: sprite_drone
    move_request: list = Field(default_factory=list)

    @classmethod
    def from_hub(cls, hub: Hub):
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

    @model_validator(mode="after")
    def valid_chk(self):
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
