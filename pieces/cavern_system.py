import random
from graphviz import Graph
import pprint
from collections import namedtuple

Cave = namedtuple("Cave", ["id", "neighboring_caves"])

class CavernSystem:
    """
    Essentially the game board for Hunt the Wumpus.  The construction of a instance of this class provides the cavern
    system into which the hazards and the hunter will be deposited.
    """

    CAVE_COUNT = 20
    CAVES = tuple(range(1, CAVE_COUNT + 1))
    NEIGHBORING_CAVE_COUNT = 3

    def __init__(self, cavern_system=None):
        """
        Initializes the cavern system for the game using a random seed.  The cavern system is converted from
        a dictionary into a list and named tuples since the cavern arrangement does not change over the course of
        the game.
        """
        self.cavern_system = cavern_system if cavern_system else [Cave(cave_id, neighboring_caves)
                              for cave_id, neighboring_caves
                              in CavernSystem.create_cavern_system().items()]
        #self.tunnels = self.find_tunnels()

    def __str__(self):
        return [cave for cave in self.cavern_system]


    @staticmethod
    def create_cavern_system():
        """
        Creates a cavern system containing CAVE_COUNT caves and exactly NEIGHBORING_CAVE_COUNT neighboring caves each.
        Cave ids are randomly determined.  No cave will have duplicated neighboring caves or itself as a neighboring
        cave.
        :return: a dictionary of the cavern system in which the keys represent the caves and the values, a list of the
        three interconnected caves.
        """

        # Prepopulate cavern system with 20 unlinked caves to start with and start a list of caves available for
        # linking as neighbors.
        caverns = {cave: [] for cave in CavernSystem.CAVES}
        available_caves = list(CavernSystem.CAVES)

        # All caves in the cavern system must be linked to exactly NEIGHBORING_CAVE_COUNT neighboring caves.
        while(any([len(neighboring_caves) < CavernSystem.NEIGHBORING_CAVE_COUNT
                   for neighboring_caves
                   in caverns.values()])):

            # Iterate over all the caves in the cavern system
            for cave in CavernSystem.CAVES:

                # Identify how many neighboring caves are needed to complete the given cave and create those
                # neighboring caves
                missing_neighboring_caves = CavernSystem.NEIGHBORING_CAVE_COUNT - len(caverns[cave])
                if missing_neighboring_caves:

                    # Insure that the cave itself is not selected as a neighboring cave
                    candidate_neighboring_caves = [available_cave for available_cave
                                                   in available_caves if available_cave != cave]

                    # Only find as many missing neighboring caves as there are caves available.  If no caves are
                    # available, swap this cave with a random neighboring cave of a different, randomly selected cave.
                    missing_neighboring_caves = min(missing_neighboring_caves, len(candidate_neighboring_caves))
                    if not missing_neighboring_caves:
                        CavernSystem.swap_neighboring_caves(cave, caverns, available_caves)

                    # Otherwise get as many neighboring caves as possible up to the number needed to populate the
                    # neighbors for the current cave.
                    else:
                        selected_neighboring_caves = random.sample(candidate_neighboring_caves,
                                                                   missing_neighboring_caves)

                        # Iterate over the selected neighboring caves
                        for selected_neighboring_cave in selected_neighboring_caves:

                            # Add the selected neighboring cave as a neighboring cave to the cave being populated.
                            # Likewise, add the cave being populated as a neighbor to the selected neighboring cave.
                            caverns[cave].append(selected_neighboring_cave)
                            caverns[selected_neighboring_cave].append(cave)

                            # If the cave being populated is still in the list of available caves but now has a full
                            # complement of neighbors, remove it from the available caves list.
                            if cave in available_caves \
                                    and len(caverns[cave]) >= CavernSystem.NEIGHBORING_CAVE_COUNT:
                                available_caves.remove(cave)

                            # If the cave selected to be a neighbor now has a full complement of neighbors, remove
                            # it from the available caves list.
                            if len(caverns[selected_neighboring_cave]) >= CavernSystem.NEIGHBORING_CAVE_COUNT:
                                available_caves.remove(selected_neighboring_cave)
        return caverns

    @staticmethod
    def swap_neighboring_caves(cave_to_populate, caverns, available_caves):
        """
        It is possible that the last cave to be populated will encounter an empty list of available caves aside from
        itself.  In that case, we switch its id with that of a cave that is already serving as a neighboring cave
        elsewhere in the cavern and we use the neighboring cave obtained in this way as a neighboring cave for our
        under-populated cave.  This way happen multiple times for the same cave (i.e., the cave have one than one
        neighboring cave absent).
        :param cave_to_populate: cave that still requires at least one neighboring cave
        :param caverns: the current arrangement of caves
        :param available_caves: list of caves available for use as neighboring caves.  This should probably only
        contain this under-populated cave at this point.
        """

        # Identify those caves we might use as a neighboring cave.  Avoid choosing the cave we are to populate
        # with neighbors or one that already serves as a neighboring cave to the cave we are to populate.
        candidate_neighboring_caves = [cave for cave in CavernSystem.CAVES
                                       if cave != cave_to_populate
                                       and cave not in caverns[cave_to_populate]]

        # Randomly selected a neighboring cave from the candidate caves
        selected_cave = random.sample(candidate_neighboring_caves, 1)[0]

        # Iterate over all the caves in the cavern system to find the first case where the selected neighboring
        # cave is used as such.  Also make sure that the cave possessing this neighboring cave does not also have
        # the cave to populate as a neighbor.
        for cave, neighboring_caves in caverns.items():
            if selected_cave in neighboring_caves and cave_to_populate not in neighboring_caves:

                # Swap the cave to populate in place of the selected neighboring cave in the cave originally housing it
                # and add the neighboring cave to the list of neighboring caves of the cave to populate.
                neighboring_caves[neighboring_caves.index(selected_cave)] = cave_to_populate
                caverns[cave_to_populate].append(selected_cave)

                # The the cave to populate now has a full complement of neighboring caves, drop it from the list of
                # available caves.
                if len(caverns[cave_to_populate]) >= CavernSystem.NEIGHBORING_CAVE_COUNT:
                    available_caves.remove(cave_to_populate)
                break

    @staticmethod
    def find_tunnels(cavern_system):
        tunnels = set()
        for cave in cavern_system:
            for neighboring_cave in cave.neighboring_caves:
                tunnel = (cave.id, neighboring_cave) if cave.id < neighboring_cave else (neighboring_cave, cave.id)
                tunnels.add(tunnel)
        return tunnels

    @staticmethod
    def create_diagram(cavern_system, step):
        tunnels = CavernSystem.find_tunnels(cavern_system)
        dot = Graph(comment='The Caverns')
        for cave in cavern_system:
            dot.node(f'{cave.id}', f'{cave.id}')
        for tunnel in tunnels:
            dot.edge(f'{tunnel[0]}', f'{tunnel[1]}')
        dot.render(f'caverns_{step}.gv', view=True)

    def get_cave(self, cave_id):
        if not (1 <= cave_id <= 20):
            return None
        return [Cave for Cave in self.cavern_system if Cave.id == cave_id][0]

if __name__ == "__main__":
    # Direct call for debugging.
    random.seed(20)
    cavern_system = CavernSystem()
    pprint.pprint(cavern_system.__str__())
    pprint.pprint(cavern_system.tunnels)
    cavern_system.show_diagram()
