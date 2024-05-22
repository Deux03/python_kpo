import random
import pygame
import os


class Fruit:
    images = {}

    def __init__(self, name, speed, resolution):
        self.name = name
        self._x_pos = random.randint(100, resolution[0] - 100)
        self._y_pos = resolution[1]
        self.speed = speed
        if name not in Fruit.images:
            img_path = os.path.join('fruits', name + '.png')
            img = pygame.image.load(img_path).convert_alpha()
            Fruit.images[name] = pygame.transform.scale(img, (100, 100))
        self.img = Fruit.images[name]
        self.img_pos = [self._x_pos, self._y_pos]

    @property
    def x_pos(self):
        return self._x_pos

    @property
    def y_pos(self):
        return self._y_pos

    @x_pos.setter
    def x_pos(self, value):
        self._x_pos = value

    @y_pos.setter
    def y_pos(self, value):
        self._y_pos = value

    @property
    def img_pos(self):
        return self._img_pos

    @img_pos.setter
    def img_pos(self, pos_x_y):
        self._img_pos = pos_x_y
