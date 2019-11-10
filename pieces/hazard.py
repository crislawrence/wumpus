import random
from collections import namedtuple

from status_message import StatusMessage

Hazard_Perimeter = namedtuple("Hazard_Perimeter", ["warning", "included_caves"])


class Hazard:
    """
    A generic version of a hazard from which all game hazards descend.
    """

    hazard_cave_ids = []

    def __init__(self, cavern_system, cave_id):
        """
        Initialization of a generic hazard.  All hazards have at least a cave id and specific hazard subclasses must
        supply a hazard perimeter named tuple.
        :param cavern_system:  the layout of the cavern system
        :param cave_id: the id of the cave the hazard is currently found in.
        """
        self.cave = cavern_system.get_cave(cave_id)
        self.cavern_system = cavern_system
        self.hazard_type = "UNKNOWN"
        self.hazard_perimeter = None
        Hazard.hazard_cave_ids.append(cave_id)

    def issue_warning(self, hunter_cave_id):
        """
        Each hazard contains a Hazard_Perimeter named tuple that identified what caves are sufficiently proximate to
        the hazard to warrant a warning.
        :param hunter_cave_id: the hunter's location
        :return: hazard warning if the hunter is within range of the hazard and None otherwise.
        """
        if hunter_cave_id in self.hazard_perimeter.included_caves:
            return self.hazard_perimeter.warning

    def check_encounter(self, hunter, hazards=None):
        """
        Each hazard implements what transpires when the hunter and the hazard occupy the same cave.  Note that the
        list of hazards is necessary for encounters with bat colonies.
        :param hunter: the hunter object
        :param hazards: the list of hazards
        """
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__} in cave {self.cave.id}." \
               f"  Hazard perimeter: {self.hazard_perimeter.included_caves}."

    def to_json(self):
        """
        In general, only the cave id is needed to supply a jsonified version of the hazard
        :return: the id of the cave currently occupied by the hazard
        """
        return self.cave.id

    @classmethod
    def from_json(cls, cavern_system, json):
        """
        The cavern system and the json object containing the cave id is all that is needed to reconstitute the basic
        hazard in the proper state.
        :param cavern_system: the layout of the cavern system
        :param json: essentially, the id of the cave which the hazard currently occupies.
        :return: the reconstituted Hazard object
        """
        return cls(cavern_system, json)


class BottomlessPit(Hazard):
    """
    The bottomless pit is a deadly hazard.  The hunter is made aware of the danger when s/he is no more than one
    cave removed from it.
    """

    def __init__(self, cavern_system, cave_id):
        super().__init__(cavern_system, cave_id)
        self.hazard_type = 'BOTTOMLESS_PIT'
        self.hazard_perimeter = Hazard_Perimeter(
            [StatusMessage('WARNING', self.hazard_type, "You feel a draft")],
            self.cave.neighboring_caves)

    def check_encounter(self, hunter, hazards=None):
        """
        Determines whether the hunter has succumbed to this deadly hazard.  Kill of the hunter and report such if that
        is the case.
        :param hunter: the hunter object
        :param hazards: lising of game hazards (not relevant here)
        :return: list of status messages possibly noting the demise of the hunter.
        """
        messages = []
        if hunter.cave.id == self.cave.id:
            messages.extend(
                [StatusMessage('TERMINAL', self.hazard_type, "You fell into a bottomless pit!")])
            messages.extend(hunter.killed())
        return messages


class BatColony(Hazard):
    """
    The bat colony is not itself a deadly hazard.  But the bat colony will transport the hunter to a cave which may
    itself contain a deadly hazard.  So it is something to be avoided.  The hunter is made aware of the danger when
    s/he is no more than one cave removed from it.
    """

    def __init__(self, cavern_system, cave_id):
        super().__init__(cavern_system, cave_id)
        self.hazard_type = 'BAT_COLONY'
        self.hazard_perimeter = Hazard_Perimeter(
            [StatusMessage('WARNING', self.hazard_type, "You hear the flapping of wings")],
            self.cave.neighboring_caves)

    def check_encounter(self, hunter, hazards=None):
        """
        Determines whether the hunter has stepped into a cave containing a bat colony.  The bat colony will lift the
        hunter and deposit him/her into another cave of the colony's choosing (not necessarily an adjoining cave since
        bats fly).  Since this is an equivalent to the hunter entering a new cave, we call that method on the hunter
        :param hunter: the hunter object
        :param hazards: listing of game hazards (needed here)
        :return: listing of status messages indicating the confrontation with the bats and the outcome of being
        ferried to another cave.
        """
        messages = []
        if hunter.cave.id == self.cave.id:
            hunter_cave_id_options = [item for item in list(range(1, 21)) if item != self.cave.id]
            new_cave_id = random.choice(hunter_cave_id_options)
            messages.extend(
                [StatusMessage('INFO', self.hazard_type,
                               "You've stumbled into a bat colony.  "
                               "Some of the bats are carrying you into another cave!")])
            updated_status, _ = hunter.enter(new_cave_id, hazards, via_bat=True)
            messages.extend(updated_status)
        return messages
