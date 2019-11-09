import random

from status_message import StatusMessage
from pieces.hazard import Hazard, Hazard_Perimeter
import itertools


class Wumpus(Hazard):
    """
    The dangerous creature that is the object of the hunt.
    """

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
        """
        Indicates that the Wumpus has been awakened.
        :return: list containing the status message that the Wumpus is awake and moving.
        """
        self.asleep = False
        return [StatusMessage('INFO', self.hazard_type, "Wumpus is awake and stiring!")]

    def move(self):
        """
        If the Wumpus is awake, it will enter one it the caves adjoining the one it is in which each turn taken.
        Otherwise the Wumpus stays put.
        """
        if not self.asleep:
            destination = random.choice(self.cave.neighboring_caves)
            self.cave = self.cavern_system.get_cave(destination)

    def check_encounter(self, hunter, hazards=None):
        """
        If the hunter stumbles into the cave containing the Wumpus, the Wumpus will awake if not already awake, and
        eat the hunter.
        :param hunter: the hunter object
        :param hazards: list of game hazards - not relevant for a Wumpus encounter
        :return: the status messages indicating the hunter's sad end.
        """
        messages = []
        if hunter.cave.id == self.cave.id:
            if self.asleep:
                messages.extend(self.awakened())
            messages.extend(
                [StatusMessage('TERMINAL', self.hazard_type,
                               "Uh oh!  You and the wumpus are occupying the same cave now.")])
            messages.extend(hunter.killed())
        return messages

    def react_to_shot(self, cave_id):
        """
        The Wumpus' reaction to an arrow being shot.  If the arrow is shot into the cave containing the Wumpus, the
        Wumpus is killed and the hunter has a new trophy.  If the arrow is shot into any other cave, the Wumpus awakens.
        :param cave_id: the id of the cave into which the arrow is shot
        :return: a list a status messages indicating the disposition of the Wumpus
        """
        messages = []
        if cave_id == self.cave.id:
            messages.extend(self.killed())
        elif self.asleep:
            messages.extend(self.awakened())
        return messages

    def killed(self):
        """
        Indicates whether the Wumpus has been killed.
        :return: list containing the status message that the Wumpus has been slain.
        """
        self.alive = False
        return [StatusMessage('TERMINAL', self.hazard_type, "You have slain the wumpus!")]

    def __str__(self):
        return super().__str__() + f" Wumpus is {'asleep' if self.asleep else 'awake'}"

    def to_json(self):
        """
        Jsonification containing minimal information needed to preserve the Wumpus' state between moves.
        :return: json object of Wumpus' state
        """
        return {
            "cave_id": self.cave.id,
            "asleep": self.asleep
        }

    @staticmethod
    def from_json(cavern_system, json):
        """
        Use of json object to reconstitute the Wumpus object and its current disposition.
        :param cavern_system: configuration of the cavern system
        :param json: json object containing current Wumpus state
        :return: Wumpus object in its current state
        """
        return Wumpus(cavern_system, json.get("cave_id"), json.get("asleep"))
