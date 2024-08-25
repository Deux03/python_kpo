import random
import pygame
import os


class Fruit:
    """
    Represents a fruit in the game with a specific type, position, and speed.

    The Fruit class handles loading and displaying fruit images, setting positions, and managing
    the fruit's movement within the game.
    """
    images = {}

    def __init__(self, name, speed, resolution):
        """
                Initialize a new Fruit object.

                :param name: The name of the fruit, used to load the corresponding image file.
                :type name: str
                :param speed: The speed at which the fruit moves on the screen.
                :type speed: int or float
                :param resolution: The screen resolution, used to set initial positions.
                :type resolution: tuple
                """
        self.name = name
        self._x_pos = random.randint(100, resolution[0] - 100)
        self._y_pos = resolution[1]
        self.speed = speed
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, 'fruits', name + '.png')

        if name not in Fruit.images:
            try:
                img = pygame.image.load(img_path).convert_alpha()
                Fruit.images[name] = pygame.transform.scale(img, (100, 100))
            except FileNotFoundError:
                print(f"Error: Image file '{img_path}' not found.")
                Fruit.images[name] = pygame.Surface((100, 100))

        self.img = Fruit.images[name]
        self.img_pos = [self._x_pos, self._y_pos]

    @property
    def x_pos(self):
        """
               Get the current x-coordinate of the fruit.

               :return: The x-coordinate of the fruit.
               :rtype: int
               """
        return self._x_pos

    @property
    def y_pos(self):
        """
                Get the current y-coordinate of the fruit.

                :return: The y-coordinate of the fruit.
                :rtype: int
                """
        return self._y_pos

    @x_pos.setter
    def x_pos(self, value):
        """
                Set the x-coordinate of the fruit.

                :param value: The new x-coordinate value to set.
                :type value: int
                """
        self._x_pos = value

    @y_pos.setter
    def y_pos(self, value):
        """
                Set the y-coordinate of the fruit.

                :param value: The new y-coordinate value to set.
                :type value: int
                """
        self._y_pos = value

    @property
    def img_pos(self):
        """
                Get the current position of the fruit's image.

                :return: The position of the fruit's image as a list [x, y].
                :rtype: list
                """
        return self._img_pos

    @img_pos.setter
    def img_pos(self, pos_x_y):
        """
                Set the position of the fruit's image.

                :param pos_x_y: The new position of the fruit's image as a list [x, y].
                :type pos_x_y: list
                """
        self._img_pos = pos_x_y
