import random
from collections import namedtuple

from status_message import StatusMessage

Hazard_Perimeter = namedtuple("Hazard_Perimeter", ["warning", "included_caves"])

class Hazard:

    hazard_cave_ids = []

    def __init__(self, cavern_system, cave_id, hazard_perimeter=None):
        self.cave = cavern_system.get_cave(cave_id)
        self.cavern_system = cavern_system
        self.hazard_perimeter = hazard_perimeter
        Hazard.hazard_cave_ids.append(cave_id)

    def issue_warning(self, hunter_cave_id):
        if hunter_cave_id in self.hazard_perimeter.included_caves:
            return self.hazard_perimeter.warning

    def __str__(self):
         return f"{self.__class__.__name__} in cave {self.cave.id}." \
                f"  Hazard perimeter: {self.hazard_perimeter.included_caves}."


class BottomlessPit(Hazard):

    def __init__(self, cavern_system, cave_id):
        super().__init__(cavern_system, cave_id)
        self.hazard_perimeter = Hazard_Perimeter(
            [StatusMessage('WARNING', 'BOTTOMLESS_PIT', "You feel a draft")],
            self.cave.neighboring_caves)

    def check_encounter(self, hunter, hazards=None):
        status = []
        if hunter.cave.id == self.cave.id:
            status.extend(
                [StatusMessage('TERMINAL', 'BOTTOMLESS_PIT', "You fell into a bottomless pit!")])
            status.extend(hunter.killed())
        return status

class BatColony(Hazard):

    def __init__(self, cavern_system, cave_id):
        super().__init__(cavern_system, cave_id)
        self.hazard_perimeter = Hazard_Perimeter(
            [StatusMessage('WARNING', 'BAT_COLONY', "You hear the flapping of wings")],
            self.cave.neighboring_caves)

    def check_encounter(self, hunter, hazards):
        status = []
        if hunter.cave.id == self.cave.id:
            hunter_cave_id_options = [item for item in list(range(1,21)) if item != self.cave.id]
            hunter.cave_id = random.choice(hunter_cave_id_options)
            status.extend(
                [StatusMessage('INFO', 'BAT_COLONY',
                              "You've stumbled into a bat colony.  "
                              "Some of the bats are carrying you into another cave!")])
            updated_status, _ = hunter.move(hazards, hunter.cave_id, via_bat=True)
            status.extend(updated_status)
        return status
