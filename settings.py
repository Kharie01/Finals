import os
# Must be set BEFORE pygame.init()
os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
import pygame
from pytmx.util_pygame import load_pygame
from os.path import join
from random import randint, uniform
import math
import json
import sys

TILE_SIZE = 32