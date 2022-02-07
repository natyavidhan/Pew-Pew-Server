import random

class Player:
    def __init__(self, name):
        # name = tuple(name)
        # name = list(name)
        name = name.replace('(', '').replace(')', '').replace("'", '').replace(' ', '').split(',')
        print(name)
        self.name = f"{name[0]}:{name[1]}"
        self.x = random.randint(0, 800)
        self.y = random.randint(0, 600)
        self.id = random.randint(0, 100)
        self.health = 100
        self.rotation = 0