﻿from enum import Enum

soundManager = None
fontManager = None
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
project_path = None
start_event = None
quit_event = None

#UI font elements
score = 0
astroidCount = 0
player_health = 100

class Stages(Enum):
    one = 100
    two = 200
    three = 300
    four = 400