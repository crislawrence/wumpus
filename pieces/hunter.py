from status_message import StatusMessage
from pieces.notebook import Notebook


class Hunter:

    ARROW_COUNT = 5

    def __init__(self, cavern_system, cave_id, quiver=None, cavern_map=None, hazards=None):
        """
        Initialize the hunter.  Uses the cavern system to find the cave associated with the cave id.  The optional
        parameters are used when the hunter is being unmarshalled from the client-side session.
        :param cavern_system: the configuration of the caves
        :param cave_id: id of the cave the hunter is in
        :param quiver: contains a limited number of arrows the hunter may use to kill the wumpus
        :param cavern_map: a map of the known portions of the cavern system
        :param hazards: list of hazards
        """
        self.alive = True
        self.quiver = quiver if quiver else Hunter.ARROW_COUNT
        self.cavern_system = cavern_system
        self.cave = self.cavern_system.get_cave(cave_id)
        self.notebook = Notebook(cavern_map=cavern_map)
        if not cavern_map and hazards:
            warnings = self.check_for_hazards(hazards)
            self.notebook.note_position(self.cave, warnings)

    def start_up(self, hazards):
        status = [StatusMessage('INFO', 'GENERAL', f"You are starting in cave {self.cave.id}")]
        warnings = self.check_for_hazards(hazards)
        self.notebook.note_position(self.cave, warnings)
        status.extend(warnings)
        return status

    def enter(self, cave_id, hazards, via_bat=False):
        """
        Hunter enters a cave.  It is possible that the hunter was moved by a bat if the hunter had stumbled into
        a bad colony.
        :param hazards: list of game hazards
        :param cave_id: id of cave into which hunter enters (or is dropped)
        :param via_bat: true if the hunter was dropped into the cave via a bat and false otherwise
        :return: a tuple containing the game state and errors if any.  The error is a server side validation of the
        choice of cave to enter.
        """
        status = []
        errors = []

        # The hunter may only enter a cave adjoining the one s/he came from unless transported via a bat.
        if cave_id in self.cave.neighboring_caves or via_bat:

            # Identify the new cave
            self.cave = self.cavern_system.get_cave(cave_id)

            # Provide informational messages appropriate to the circumstance.
            if via_bat:
                status.extend([StatusMessage('INFO', 'BAT_COLONY',
                                             f"You are being dropped into cave {cave_id}")])
            else:
                status.extend([StatusMessage('INFO', 'GENERAL',
                                             f"You are moving into cave {cave_id}")])

            status.extend([StatusMessage('INFO', 'GENERAL', f"{self}")])

            wumpus = [hazard for hazard in hazards if hazard.hazard_type == 'WUMPUS'][0]
            wumpus.move()

            # Check to see if any hazards are encountered in this cave.  Which, in most cases, will result in the
            # demise of the hunter.
            dangers = self.check_for_encounters(hazards)
            status.extend(dangers)

            # Determine whether the hunter encountered a bat colony.  That doesn't preclude the hunter being
            # deceased since the wumpus map also be resident in the same cave.
            encountered_bat_colony = [danger for danger in dangers if danger.source == 'BAT_COLONY']

            # If the hunter remains alive and s/he wasn't ferried off by bats after entering the cave, check to see
            # if any hazards are proximate to this cave and note the discoveries in the notebook.
            if self.alive and not encountered_bat_colony:
                warnings = self.check_for_hazards(hazards)
                status.extend(warnings)
                self.notebook.note_position(self.cave, warnings, not wumpus.asleep)

        # In the unlikely event that the user called the ajax post directly with an invalid cave id selection.
        else:
            errors.append("The cave you specified does not adjoin the one you are in.")

        return status, errors

    def shoot(self, cave_id, hazards):
        status = []
        errors = []

        status.extend([StatusMessage('INFO', 'GENERAL', f"{self}")])

        if self.quiver > 0:

            wumpus = [hazard for hazard in hazards if hazard.hazard_type == 'WUMPUS'][0]

            self.quiver -= 1
            status.extend([StatusMessage('INFO', 'GENERAL',
                                         f"You've shot an arrow into {cave_id}.  "
                                         f"You have {self.quiver} arrows remaining.")])
            status.extend(wumpus.react_to_shot(cave_id))

            if wumpus.alive:

                wumpus = [hazard for hazard in hazards if hazard.hazard_type == 'WUMPUS'][0]
                wumpus.move()

                # Check to see if the wumpus has entered this cave, which will result in the demise of the hunter.
                dangers = self.check_for_encounters([wumpus])
                status.extend(dangers)

                # If the hunter remains alive, check to see if the wumpus is now proximate to this cave and note
                # that finding in the notebook.
                if self.alive:
                    warnings = self.check_for_hazards(hazards)
                    status.extend(warnings)
                    self.notebook.note_position(self.cave, warnings, not wumpus.asleep)
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
        """
        Iterate over the game's hazards to determine whether the hunter has had an unfortunate encounter.  The hazards
        are arranged in the list in decreasing order of lethality.  Consequently, the first encounter obviates the need
        to check for additional encounters.
        :param hazards: listing of game hazards
        :return: list of status messages
        """
        messages = []
        for hazard in hazards:
            encounter = hazard.check_encounter(self, hazards=hazards)
            if encounter:
                messages.extend(encounter)
                break
        return messages

    def __str__(self):
        return f"You are now in cave {self.cave.id}.  The adjoining caves are {self.cave.neighboring_caves}"

    def to_json(self):
        """
        Minimal json object needed to reconstitute the hunter game state
        :return: jsonified hunter
        """
        return {
            "cave_id": self.cave.id,
            "quiver": self.quiver,
            "cavern_map": self.notebook.to_json()
        }

    @staticmethod
    def from_json(cavern_system, json):
        """
        Restores the hunter game state from a json object and the cavern system
        :param cavern_system: layout of cavern system
        :param json: jsonified hunter
        :return: reconstituted hunter object
        """
        return Hunter(cavern_system=cavern_system,
                      cave_id=json.get("cave_id"),
                      quiver=json.get("quiver"),
                      cavern_map=Notebook.from_json(cavern_system, json.get("cavern_map")),
                      hazards=None)
