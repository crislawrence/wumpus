from collections import namedtuple

from graphviz import Graph

from status_message import StatusMessage

Mapped_Site = namedtuple("Mapped_Site", ["cave", "warnings"])


class Notebook:
    """
    This object captures the hunter's field notes, which essentially logs the caves the hunter has visited, what if any
    hazards were detected from therein and what additional caves were discovered on the periphery.
    """

    def __init__(self, cavern_map=None):
        if cavern_map:
            self.cavern_map = cavern_map
        else:
            self.cavern_map = []

    def consult_notebook(self, current_cave_id):
        """
        Produces an svg representation of the explored portions of the cavern system along with warnings relevant to
        certain caves.
        :param: current_cave_id - where the hunter is currently located.
        :return: string reprsentation of svg based cavern map (using graphviz)
        """
        tunnels = self.find_tunnels()
        dot = Graph(comment='Your notebook - explored caves')
        for mapped_cave in self.cavern_map:
            warning_sources = ""
            if mapped_cave.warnings:
                dot.attr('node', color='yellow')
                warning_sources = ",".join([warning.source for warning in mapped_cave.warnings])
            else:
                dot.attr('node', color='green')
            current_location = '*' if mapped_cave.cave.id == current_cave_id else ''
            dot.node(f'{mapped_cave.cave.id}',
                     f'{mapped_cave.cave.id} {current_location}',
                     _attributes=[('tooltip', f'{warning_sources}')])
        for tunnel in tunnels:
            dot.attr('node', color='black')
            dot.edge(f'{tunnel[0]}', f'{tunnel[1]}')
        svg_data = dot.pipe(format='svg')
        return "".join(chr(datum) for datum in svg_data)

    def find_tunnels(self):
        """
        Identifies the tunnels that exist between each cave and its three neighbors.  This will insure that even
        those caves that the hunter has discovered but not yet attempted to occupy are included in the map.
        :return: set of tuples containing the tunnel endpoints.
        """
        tunnels = set()
        for mapped_site in self.cavern_map:
            for neighboring_cave in mapped_site.cave.neighboring_caves:
                tunnel = (mapped_site.cave.id, neighboring_cave)\
                    if mapped_site.cave.id < neighboring_cave else (neighboring_cave, mapped_site.cave.id)
                tunnels.add(tunnel)
        return tunnels

    def note_position(self, cave, warnings, wumpus_moving=False):
        """
        With each turn the hunter takes, additions may be made to the cavern map.  If the hunter backtracks, we
        update the map rather than add to it.  Note that hazards regarding the wumpus are discarded for all but the
        hunter's current location when the wumpus is awake since it can and will move about.
        :param cave: the hunter's current location
        :param warnings: hazard warnings detected for the hunter's current location
        :param wumpus_moving: boolean indicating whether the wumpus is moving (i.e., awake).
        """

        # Previous indications of the presence of the wumpus are no longer reliable and potentially misleading since
        # the wumpus is now moving.
        if wumpus_moving:
            for mapped_site in self.cavern_map:
                old_wumpus_warning = [warning for warning in mapped_site.warnings if warning.source == 'WUMPUS']
                if old_wumpus_warning:
                    mapped_site.warnings.remove(old_wumpus_warning[0])

        # Avoid adding duplicates if the hunter backtracks.  If the wumpus is moving about the newer version of the
        # mapped site may contain a warning about the wumpus's proximity.  So we remove the original version in
        # favor of the newer version.
        for mapped_site in self.cavern_map:
            if cave.id == mapped_site.cave.id:
                self.cavern_map.remove(mapped_site)

        self.cavern_map.append(Mapped_Site(cave, warnings))

    def to_json(self):
        """
        Minimal json object needed to reconstitute the notebook game state
        :return: json compatible array containing json compatible dictionaries of the mapped site named tuples.
        """
        json_array = []
        for mapped_site in self.cavern_map:
            json_object = {
                            "cave_id": mapped_site.cave.id,
                            "warnings": [
                                warning.to_json()
                                for warning in mapped_site.warnings
                            ]
                          }
            json_array.append(json_object)
        return json_array

    @staticmethod
    def from_json(cavern_system, json_array):
        """
        Restores the notebook game state from a json array of mapped site json objects and the cavern system
        :param cavern_system: layout of cavern system
        :param json_array: jsonified array containing the mapped site named tuples that make of the cavern map
        :return: the reconstituted cavern map.
        """
        cavern_map = []
        for json_object in json_array:
            cave = cavern_system.get_cave(json_object['cave_id'])
            status_messages = []
            for warning in json_object['warnings']:
                status_messages.append(StatusMessage.from_json(warning))
            mapped_site = Mapped_Site(cave, status_messages)
            cavern_map.append(mapped_site)
        return cavern_map
