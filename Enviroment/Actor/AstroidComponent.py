﻿import random
from DesignPatterns.ComponentPattern import Component
from Scripts.GameObject import GameObject



class Astroid(Component):

    def __init__(self, owner_go: GameObject):
        super().__init__(owner_go)
        self.owner = owner_go
        self.w = self.owner.image.get_width()
        self.h = self.owner.image.get_height()

        # gets initial position
        self.x = owner_go.transform.position.x
        self.y = owner_go.transform.position.y

        # set astroid direction based on initial spawn position
        if owner_go.tag is not "Asteroid_Split":
            if self.x < 1920 // 2:
                self.xdir = 1
            else:
                self.xdir = -1
            if self.y < 1080 // 2:
                self.ydir = 1
            else:
                self.ydir = -1
        else:
            self.xdir = [-1,1][random.randrange(2)]
            self.ydir = [-1,1][random.randrange(2)]

        self.xv = self.xdir * random.randrange(1, 3)
        self.yv = self.ydir * random.randrange(1, 3)

    def update(self):
        self.owner.transform.translate(self.y//500, self.x//500)






