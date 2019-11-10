from datetime import datetime
import random

from pieces.cavern_system import CavernSystem, Cave
from pieces.hazard import BottomlessPit, BatColony, Hazard
from pieces.hunter import Hunter
from pieces.wumpus import Wumpus
from flask import current_app
from pprint import pformat


class Game:

    def __init__(self, cavern_system=None, wumpus=None, bottomless_pits=None, bats=None, hunter=None):
        """
        Initializes or reconstitutes the game state.  At the start of a game, the cavern system layout, the
        positions of the hazards and the location of the hunter are established essentially randomly.  At each
        subsequent turn of the game, the state is reconstituted from existing information.
        :param cavern_system: the layout of the cavern system
        :param wumpus: the Wumpus
        :param bottomless_pits: the bottomless pits
        :param bats: the bat colonies
        :param hunter: the hunter
        """

        # Use current cavern system or create a new cavern system.
        self.cavern_system = cavern_system or CavernSystem()

        # Hazard added to list in descending order from most pertinent and deadly
        self.hazards = []

        # Use current wumpus or create new wumpus
        self.wumpus = wumpus
        if not self.wumpus:
            wumpus_cave_id = random.choice(range(1, 21))
            self.wumpus = Wumpus(self.cavern_system, wumpus_cave_id)
        self.hazards.append(self.wumpus)

        # Use current bottomless pit or create new bottomless pits
        self.bottomless_pits = bottomless_pits or [BottomlessPit(self.cavern_system, cave_id)
                                                   for cave_id in random.sample(range(1, 21), 2)]
        self.hazards.extend(self.bottomless_pits)

        # Use current bat colonies or create new bat colonies
        self.bats = bats or [BatColony(self.cavern_system, cave_id)
                             for cave_id in random.sample(range(1, 21), 2)]
        self.hazards.extend(self.bats)

        # Use current hunter or create new hunter
        self.hunter = hunter
        if not self.hunter:
            hunter_cave_id_options = list(set(range(1, 21)) - set(Hazard.hazard_cave_ids))
            self.hunter = Hunter(self.cavern_system, random.choice(hunter_cave_id_options))

    def display_configuration(self):
        """
        Logs the cavern system layout and starting positions of all hazards.  Note that the wumpus will move about
        once awoken.
        :return:
        """
        current_app.logger.debug(pformat(self.cavern_system.cavern_system))
        for hazard in self.hazards:
            current_app.logger.debug(hazard)

    @staticmethod
    def start_up(seed=None):
        """
        The method runs only when a new game is begun.  Old cavern_map files are deleted from the notes folder and if
        no seed is provided the current timestamp is used instead to seed the randon number generator.
        :param seed: a provided seed for the random number generator.
        """

        # Create 'random' seed if no seed is provided
        seed = int(seed) if seed else datetime.now()
        current_app.logger.debug(f"Seed: {seed}")
        random.seed(seed)

    def to_json(self):
        return {
            "cavern_system": self.cavern_system.cavern_system,
            "wumpus": {
                "cave_id": self.wumpus.cave.id,
                "asleep": self.wumpus.asleep
            },
            "bottomless_pits": [bottomless_pit.to_json() for bottomless_pit in self.bottomless_pits],
            "bat_colonies": [bat_colony.to_json() for bat_colony in self.bats],
            "hunter": self.hunter.to_json()
        }

    @staticmethod
    def from_json(json):
        cavern_system_json = json.get("cavern_system")
        caves = [Cave(cave[0], cave[1]) for cave in cavern_system_json]
        cavern_system = CavernSystem(caves)
        hunter = Hunter.from_json(cavern_system, json.get("hunter"))
        wumpus = Wumpus.from_json(cavern_system, json.get("wumpus"))
        bottomless_pits = [BottomlessPit.from_json(cavern_system, bottomless_pit)
                           for bottomless_pit in json.get("bottomless_pits")]
        bats = [BatColony.from_json(cavern_system, bat_colony)
                for bat_colony in json.get("bat_colonies")]
        return Game(cavern_system=cavern_system,
                    wumpus=wumpus,
                    bottomless_pits=bottomless_pits,
                    bats=bats,
                    hunter=hunter)
