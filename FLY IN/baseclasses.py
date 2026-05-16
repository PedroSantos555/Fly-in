from typing import List, Dict, Literal, Optional, Any
from pydantic import BaseModel, Field, model_validator
from pydantic import ValidationError, ConfigDict
import pygame


class Connection(BaseModel):
    start: str
    end: str
    max_links: Optional[int] = None

    @model_validator(mode="after")
    def valid_chk(self):
        if self.max_links < 0:
            raise ValidationError("max_links must be a positive int")

        return self


class sprite_hub(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.image.load("./assets/drone_pad_medium.png")
        self.rect = self.image.get_rect()
        self.rect.center = (128*x + 64, 360 + 128*y)
        self.size = 1

    def medium(self) -> None:
        self.image = pygame.image.load("./assets/drone_pad_medium.png")
        self.rect = self.image.get_rect()
        self.rect.center = (128*self.x + 64, 360 + 128*self.y)
        self.size = 1

    def big(self) -> None:

        self.image = pygame.image.load("./assets/drone_pad_large.png")
        self.rect = self.image.get_rect()
        self.rect.center = (258*self.x + 128, 360 + 258*self.y)
        self.size = 2

    def mini(self) -> None:

        self.image = pygame.image.load("./assets/drone_pad.png")
        self.rect = self.image.get_rect()
        self.rect.center = (64*self.x + 32, 360 + 64*self.y)
        self.size = 0.5

    def draw(self, surface: Any) -> None:
        surface.blit(self.image, self.rect)


class Hub(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    kind: Literal["start_hub", "end_hub", "hub"] = "hub"
    name: str
    color: str = "none"
    x: int
    y: int
    max_drones: int = Field(default=1, ge=0)
    status: Literal["normal", "restricted", "priority", "blocked"] = "normal"
    conects: List[Connection]
    sprite: sprite_hub


class Set_Up(BaseModel):
    nb_drones: int = Field(ge=0)
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
