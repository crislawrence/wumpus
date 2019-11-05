import random

from status_message import StatusMessage
from pieces.hazard import Hazard, Hazard_Perimeter
import itertools


class Wumpus(Hazard):

    def __init__(self, cavern_system, cave_id, asleep=True):
        super().__init__(cavern_system, cave_id)
        self.hazard_type = 'WUMPUS'
        self.asleep = asleep
        self.alive = True
        self.establish_hazard_perimeter()

    def establish_hazard_perimeter(self):
        surrounding_caves = [self.cavern_system.get_cave(cave_id) for cave_id in self.cave.neighboring_caves]
        surrounding_cave_ids = list(itertools.chain(*[cave.neighboring_caves for cave in surrounding_caves]))
        surrounding_cave_ids.extend(self.cave.neighboring_caves)
        self.hazard_perimeter = Hazard_Perimeter(
            [StatusMessage('WARNING', self.hazard_type, "You smell a wumpus (ick!)")],
            set(surrounding_cave_ids))

    def awakened(self):
        self.asleep = False
        return [StatusMessage('INFO', self.hazard_type, "Wumpus is awake and stiring!")]

    def move(self):
        status = []
        if not self.asleep:
            destination = random.choice(self.cave.neighboring_caves)
            self.cave = self.cavern_system.get_cave(destination)
        return status


    def check_encounter(self, hunter, hazards):
        status = []
        if hunter.cave.id == self.cave.id:
            status.extend(
                [StatusMessage('TERMINAL', self.hazard_type,
                              "Uh oh!  You and the wumpus are occupying the same cave now.")])
            if self.asleep:
                status.extend(self.awakened())
            status.extend(hunter.killed())
        return status

    def react_to_shot(self, cave_id):
        status = []
        if cave_id == self.cave.id:
            status.extend(self.killed())
        elif self.asleep:
            status.extend(self.awakened())
        return status

    def killed(self):
        self.alive = False
        return [StatusMessage('TERMINAL', self.hazard_type, "You have slain the wumpus!")]

    def __str__(self):
        return super().__str__() + f" Wumpus is {'asleep' if self.asleep else 'awake'}"