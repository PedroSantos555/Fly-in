from typing import List, Dict, Literal, Optional, Any, Tuple
from pydantic import BaseModel, Field, model_validator
from pydantic import ConfigDict
import pygame


class Camera:
    """2D camera with a pan offset and zoom factor."""
    def __init__(self) -> None:
        """Create a camera at the origin with zoom 1."""
        self.offset = pygame.Vector2(0, 0)
        self.zoom = 1.0

    def world_to_screen(self, world_pos: pygame.Vector2) -> pygame.Vector2:
        """Convert a world position to screen coordinates.

        Args:
            world_pos: Position in world space.

        Returns:
            The matching position on screen.
        """
        return ((world_pos - self.offset) * self.zoom)

    def move(self, x: float, y: float) -> None:
        """Pan the camera.

        Args:
            x: Horizontal offset to add.
            y: Vertical offset to add.
        """
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

}


def recolor_surface(surface: Any,
                    old_color: Tuple[int, int, int],
                    new_color:  Tuple[int, int, int]) -> Any:
    """Return a copy of a surface with one color replaced.

    Args:
        surface: Source pygame surface.
        old_color: Color to replace.
        new_color: Replacement color.

    Returns:
        The recolored copy.
    """
    result = surface.copy()

    pixels = pygame.PixelArray(result)
    pixels.replace(old_color, new_color)
    del pixels

    return result


class sprite_hub(pygame.sprite.Sprite):
    """Graphical sprite of a hub, styled by its zone type."""
    def __init__(self, x: int, y: int, color: str, type: str) -> None:
        """Load the hub image for a zone type and color.

        Args:
            x: Hub grid x coordinate.
            y: Hub grid y coordinate.
            color: Color name from HUB_COLORS.
            type: Zone type (normal, restricted, priority, blocked).
        """
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
        self.size: float = 1.0

    def medium(self) -> None:
        """Switch to the medium (zoom 1) image."""
        image = pygame.image.load(
            self.mediumfile
            ).convert_alpha()

        self.image = recolor_surface(
            image,
            (180, 180, 180),
            self.color
        )

        self.rect = self.image.get_rect()
        self.size = 1.0

    def big(self) -> None:
        """Switch to the large (zoom 2) image."""

        image = pygame.image.load(
            self.largefile
            ).convert_alpha()

        self.image = recolor_surface(
            image,
            (180, 180, 180),
            self.color
        )

        self.rect = self.image.get_rect()
        self.size = 2.0

    def mini(self) -> None:
        """Switch to the small (zoom 0.5) image."""

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
        """Draw the hub on a surface.

        Args:
            surface: Target pygame surface.
            camera: Camera used for the world-to-screen mapping.
        """

        screen_pos = camera.world_to_screen(self.world_pos)
        if self.rect is not None:
            self.rect.center = (round(screen_pos.x), round(screen_pos.y))
        surface.blit(self.image, self.rect)


class sprite_drone(pygame.sprite.Sprite):
    """Graphical sprite of a drone with smooth movement."""
    def __init__(self, x: int, y: int) -> None:
        """Place a drone sprite on a hub.

        Args:
            x: Grid x coordinate.
            y: Grid y coordinate.
        """
        super().__init__()
        self.world_pos = pygame.Vector2(
            128*x + 64,
            360 + 128*y
        )
        self.image = pygame.image.load("./assets/NewDrone_Medium.png")
        self.rect = self.image.get_rect()
        self.size: float = 1.0
        self.start_pos = self.world_pos.copy()
        self.target_pos = self.world_pos.copy()
        self.moving = False
        self.progress = 0.0
        self.speed = 0.0

    def medium(self) -> None:
        """Switch to the medium (zoom 1) image."""
        self.image = pygame.image.load("./assets/NewDrone_Medium.png")
        self.rect = self.image.get_rect()
        self.size = 1

    def big(self) -> None:
        """Switch to the large (zoom 2) image."""

        self.image = pygame.image.load("./assets/NewDrone_Large.png")
        self.rect = self.image.get_rect()
        self.size = 2

    def mini(self) -> None:
        """Switch to the small (zoom 0.5) image."""

        self.image = pygame.image.load("./assets/NewDrone_Small.png")
        self.rect = self.image.get_rect()
        self.size = 0.5

    def teleport(self, x: float, y: float) -> None:
        """Move the drone instantly to a grid position.

        Args:
            x: Target grid x coordinate.
            y: Target grid y coordinate.
        """

        self.world_pos = pygame.Vector2(128*x + 64,
                                        360 + 128*y)
        self.start_pos = self.world_pos
        self.moving = False
        self.progress = 0

    def move(self, x: float, y: float) -> None:
        """Start an animated move to a grid position.

        Args:
            x: Target grid x coordinate.
            y: Target grid y coordinate.
        """

        self.target_pos = pygame.Vector2(128*x + 64,
                                         360 + 128*y)
        self.progress = 0.0
        self.speed = self.start_pos.distance_to(self.target_pos)
        self.moving = True

    def draw(self, surface: Any, camera: Camera) -> None:
        """Draw the drone on a surface.

        Args:
            surface: Target pygame surface.
            camera: Camera used for the world-to-screen mapping.
        """
        screen_pos = camera.world_to_screen(self.world_pos)
        if self.rect is not None:
            self.rect.center = (round(screen_pos.x), round(screen_pos.y))
        surface.blit(self.image, self.rect)

    def update(self, fps: int) -> None:
        """Advance the movement animation by one frame.
        """

        if not self.moving:
            return

        distance = self.start_pos.distance_to(self.target_pos)

        if distance == 0:
            return

        self.progress += 1/fps

        if self.progress >= 1:
            self.progress = 1
            self.start_pos = self.target_pos
            self.moving = False

        self.world_pos = self.start_pos.lerp(self.target_pos,
                                             self.progress)


class Connection(BaseModel):
    """Bidirectional link between two hubs with a capacity."""
    start: str
    end: str
    max_links: Optional[int] = None
    reserve_timetable: Dict[int, int]


class Hub(BaseModel):
    """Zone of the network, with its capacity, links and schedule."""

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
    """Drone with its current hub, sprite and per-turn script."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    position: Hub
    sprite: sprite_drone
    script: Dict[int, Tuple[float, float, str]]


class Set_Up(BaseModel):
    """Complete simulation state: drones, hubs and connections."""

    drones: List[Drone]
    hubs: Dict[str, Hub]
    connections: List[Connection]

    def structure_connections(self) -> None:
        """Attach each connection to the hubs at both ends."""

        for hub in self.hubs.values():
            for conetion in self.connections:
                if conetion.start == hub.name:
                    hub.conects.append(conetion)
                if conetion.end == hub.name:
                    hub.conects.append(conetion)

    @model_validator(mode="after")
    def valid_chk(self) -> "Set_Up":
        """Check for one start hub, one end hub, unique coordinates.

        Raises:
            ValueError: If any of these rules is broken.

        Returns:
            The validated setup.
        """
        starts = [h for h in self.hubs.values() if h.kind == "start_hub"]

        if len(starts) != 1:
            raise ValueError("Expected exactly one start_hub")

        ends = [h for h in self.hubs.values() if h.kind == "end_hub"]

        if len(ends) != 1:
            raise ValueError("Expected exactly one end_hub")

        coords = set()

        for hub in self.hubs.values():

            pos = (hub.x, hub.y)

            if pos in coords:
                raise ValueError(
                    f"Duplicate coordinates {pos}"
                )

            coords.add(pos)
        return self
