from pprint import pprint

from status_message import StatusMessage
from pieces.cavern_system import CavernSystem
from pieces.notebook import Notebook

class Hunter:

    ARROW_COUNT = 5

    def __init__(self, cavern_system, cave_id, quiver=None, cavern_map=None, hazards=None):
        self.alive = True
        self.quiver = quiver if quiver else Hunter.ARROW_COUNT
        self.cavern_system = cavern_system
        self.cave = self.cavern_system.get_cave(cave_id)
        self.notebook = Notebook(cavern_map=cavern_map)
        if not cavern_map and hazards:
            status = self.check_for_hazards(hazards)
            self.notebook.note_position(self.cave, status)

    def start_up(self, hazards):
        status = [StatusMessage('INFO', 'GENERAL', f"You are starting in cave {self.cave.id}")]
        warnings = self.check_for_hazards(hazards)
        self.notebook.note_position(self.cave, warnings)
        status.extend(warnings)
        return status

    def move(self, hazards, cave_id, via_bat=False):
        status = []
        errors = []
        if cave_id in self.cave.neighboring_caves or via_bat:
            if via_bat:
                status.extend([StatusMessage('INFO', 'BAT_COLONY',
                                             f"You are being dropped into cave {cave_id}")])
            else:
                status.extend([StatusMessage('INFO', 'GENERAL',
                                             f"You are moving into cave {cave_id}")])
            self.cave = self.cavern_system.get_cave(cave_id)
            status.extend([StatusMessage('INFO', 'GENERAL', f"{self}")])
            status.extend(self.check_for_encounters(hazards))

            if self.alive:
                warnings = self.check_for_hazards(hazards)
                status.extend(warnings)
                self.notebook.note_position(self.cave, warnings)
        else:
            errors.append("The cave you specified does not adjoin the one you are in.")
        return status, errors

    def shoot(self, wumpus, cave_id, hazards):
        status = []
        errors = []
        if self.quiver > 0:
            self.quiver -= 1
            status.extend([StatusMessage('INFO', 'GENERAL',
                                        f"You've shot an arrow into {cave_id}.  "
                                        f"You have {self.quiver} arrows remaining.")])
            status.extend(wumpus.react_to_shot(cave_id, self, hazards))
        else:
            status.extend([StatusMessage('WARNING', 'GENERAL',
                                        "You have no arrows left.  All you can do is avoid the wumpus.")])
        return status, errors


    def killed(self):
        self.alive = False
        return [StatusMessage('TERMINAL', 'GENERAL', "You've been killed.  Sorry.")]

    def check_for_hazards(self, hazards):
        status = []
        for hazard in hazards:
            warning = hazard.issue_warning(self.cave.id)
            # Some potential hazards too far removed yet for a warning.
            if warning:
                status.extend(warning)
        return status

    def check_for_encounters(self, hazards):
        status = []
        for hazard in hazards:
            encounter = hazard.check_encounter(self, hazards=hazards)
            if encounter:
                status.extend(encounter)
                break
        return status

    def __str__(self):
        return f"You are now in cave {self.cave.id}.  The adjoining caves are {self.cave.neighboring_caves}"
