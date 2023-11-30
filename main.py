from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from math import atan2
from random import randint
import json

size_x = 30
size_z = 30

inventory = {
    "wood": 0,
    "stone": 0,
    "grass": 0,
    "dirt": 0,
    "leaf": 0,
}

selected_item = "grass"

blocks = []

app = Ursina()

player = FirstPersonController()

sky = Sky(texture="textures/skybox/skybox.jpg")

def generate_block(position, texture, bt):
    blocks.append(Block(position = position, texture = texture, bt=bt))


def generate_position(origin):
    new_x = origin.x + randint(-5, 5)
    new_z = origin.z + randint(-5, 5)
    if new_x < 0:
        new_x = 0
    if new_z < 0:
        new_z = 0
    if new_x > size_x - 1:
        new_x = size_x - 1
    if new_z > size_z - 1:
        new_z = size_z - 1
    return (new_x, origin.y, new_z)

def load_structure(filename, x, y, z):
    path = "./structures/" + filename
    file = open(path, "r")
    data = json.load(file)
    for block in data:
        generate_block(position = (block["x"] + x, block["y"] + y, block["z"] + z), texture = block["texture"], bt=block["bt"])
    file.close()

class Block(Button):
    def __init__(self, position, texture, bt):
        super().__init__(
            model = "cube",
            parent = scene,
            position = position,
            origin_y = 0.5,
            texture = texture,
            color = color.white,
            highlight_color = color.blue,

            bt = bt
        )
    def input(self, key):
        if self.hovered:
            if key == "right mouse down":
                inventory[self.bt] += 1
                destroy(self)
            if key == "left mouse down":
                if inventory[selected_item] > 0:
                    inventory[selected_item] -= 1
                    generate_block(position = self.position + mouse.normal, texture = f"./textures/blocks/{selected_item}.png", bt = selected_item)

class Creature(Entity):
    def __init__(self, position, texture, scale):
        super().__init__(
            model = "quad",
            parent = scene,
            position = position,
            origin_y = 0.5,
            texture = texture,
            color = color.white,
            scale = scale,
            double_sided = True,

            waiting = False,
            time = 0
        )
    def update(self):
        angle_to_player = atan2(player.x - self.x, player.z - self.z)
        self.rotation_y = angle_to_player * (180 / pi)
        if self.waiting:
            self.time -= time.dt
            if self.time <= 0:
                self.waiting = False
                self.animate_position(generate_position(self.position), 4)
        else:
            self.time = randint(5, 10)
            self.waiting = True

def update():
    if held_keys["escape"]:
        quit()
    if player.position.y < -10:
        player.position = (size_x / 2, 0, size_z / 2)

for x in range(size_x):
    for z in range(size_z):
        generate_block(
            position = (x, 0, z),
            texture = "./textures/blocks/grass.png",
            bt = "grass"
        )
        if randint(1, 20) == 1 and x != 0 and z != 0:
            load_structure("tree.json", x, 1, z)
for x in range(size_x):
    for z in range(size_z):
        generate_block(
            position = (x, -1, z),
            texture = "./textures/blocks/dirt.png",
            bt = "dirt"
        )
for x in range(size_x):
    for z in range(size_z):
        generate_block(
            position = (x, -2, z),
            texture = "./textures/blocks/stone.png",
            bt = "stone"
        )

player.position = (size_x / 2, 0, size_z / 2)

#Creature((size_x / 2, 2, size_z / 2), "./textures/creatures/creature.png", (1, 2, 1))

app.run()