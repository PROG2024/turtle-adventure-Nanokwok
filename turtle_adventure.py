import math
from turtle import RawTurtle
from gamelib import Game, GameElement


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elements related to the Turtle's Adventure game.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAdventureGame instance.
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x - 10, self.y - 10, self.x + 10, self.y + 10)
            self.canvas.coords(self.__id2, self.x - 10, self.y + 10, self.x + 10, self.y - 10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home.
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x - self.size / 2, self.x + self.size / 2
        y1, y2 = self.y - self.size / 2, self.y + self.size / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self, game: "TurtleAdventureGame", turtle: RawTurtle, speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game.
    """

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy.
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy.
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player.
        """
        return (
                (self.x - self.size / 2 < self.game.player.x < self.x + self.size / 2)
                and
                (self.y - self.size / 2 < self.game.player.y < self.y + self.size / 2)
        )


class ChasingEnemy(Enemy):
    """
    Define a chasing enemy.
    """

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__id = 0

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, outline=self.color, width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        if self.game.player is not None:

            player_x = self.game.player.x
            player_y = self.game.player.y

            distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)

            if distance < self.size:
                self.game.game_over_lose()
                return

            angle = math.atan2(player_y - self.y, player_x - self.x)

            speed = 3
            self.x += speed * math.cos(angle)
            self.y += speed * math.sin(angle)

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)


class FencingEnemy(Enemy):
    """
    Define a fencing enemy that walks around the home in a square-like pattern.
    """

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__id = 0
        self.__step = 0
        self.__home_x = game.home.x
        self.__home_y = game.home.y
        self.__step = 0
        self.__side_length = 100
        cn = 100 / 2
        self.__home_corner = [(self.__home_x - cn, self.__home_y - cn), (self.__home_x + cn, self.__home_y - cn),
                              (self.__home_x + cn, self.__home_y + cn), (self.__home_x - cn, self.__home_y + cn)]

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, outline=self.color, width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        if self.game.player is not None:
            if self.hits_player():
                self.game.game_over_lose()
                return

            speed = 2

            if self.__step == 0:
                self.x += speed
                if self.x >= self.__home_corner[1][0]:
                    self.__step += 1
            elif self.__step == 1:
                self.y += speed
                if self.y >= self.__home_corner[2][1]:
                    self.__step += 1
            elif self.__step == 2:
                self.x -= speed
                if self.x <= self.__home_corner[3][0]:
                    self.__step += 1
            elif self.__step == 3:
                self.y -= speed
                if self.y <= self.__home_corner[0][1]:
                    self.__step = 0

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)


class RandomEnemy(Enemy):
    """
    Define a random walk enemy.
    """

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__id = 0
        self.__angle = 45

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, outline=self.color, width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        if self.game.player is not None:
            if self.hits_player():
                self.game.game_over_lose()
                return

            speed = 3

            self.x += speed * math.cos(self.__angle)
            self.y += speed * math.sin(self.__angle)

            screen_width = self.game.screen_width
            screen_height = self.game.screen_height

            if self.x < 0 or self.x > screen_width:
                self.__angle = math.pi - self.__angle
            if self.y < 0 or self.y > screen_height:
                self.__angle = -self.__angle

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)


class FrontGateEnermy(Enemy):
    """enemy that walk randomly around the home"""
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__id = 0
        self.__angle = 45

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, outline=self.color, width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        if self.game.player is not None:
            if self.hits_player():
                self.game.game_over_lose()
                return

            speed = 3

            self.x += speed * math.cos(self.__angle)
            self.y += speed * math.sin(self.__angle)

            screen_width = self.game.screen_width
            screen_height = self.game.screen_height

            if self.x < screen_width - (screen_width // 4) or self.x > screen_width:
                self.__angle = math.pi - self.__angle
            if self.y < screen_height // 3 or self.y > screen_height - (screen_height // 3):
                self.__angle = -self.__angle

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int, screen_width: int, screen_height: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        self.__screen_width = screen_width
        self.__screen_height = screen_height

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance.
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level.
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level.
        """
        # new_enemy = ChasingEnemy(self.__game, 20, "red")
        random_enemy = RandomEnemy(self.__game, 20, "red")
        chasing_enemy = ChasingEnemy(self.__game, 20, "blue")
        fencing_enemy = FencingEnemy(self.__game, 20, "orange")
        front_gate_enemy = FrontGateEnermy(self.__game, 20, "pink")

        random_enemy.x = 100
        random_enemy.y = 100

        chasing_enemy.x = 200
        chasing_enemy.y = 200

        fencing_enemy.x = self.__screen_width - 150
        fencing_enemy.y = (self.__screen_height // 2) - 50

        front_gate_enemy.x = self.__screen_width - 100
        front_gate_enemy.y = self.__screen_height // 2

        self.game.add_element(random_enemy)
        self.game.add_element(chasing_enemy)
        self.game.add_element(fencing_enemy)
        self.game.add_element(front_gate_enemy)


class TurtleAdventureGame(Game):
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height - 1, self.screen_width - 1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width - 100, self.screen_height // 2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level, screen_width=self.screen_width,
                                              screen_height=self.screen_height)

        self.player.x = 50
        self.player.y = self.screen_height // 2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game.
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game.
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game.
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Lose",
                                font=font,
                                fill="red")

    def show_level(self, level: int):
        """show level"""
        font = ("Arial", 20, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                20,
                                text=f"Level {level}",
                                font=font,
                                fill="grey")
