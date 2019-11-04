from collections import namedtuple
from pprint import pprint

from graphviz import Graph

from status_message import StatusMessage

Mapped_Site = namedtuple("Mapped_Site", ["cave", "warnings"])

class Notebook:

    def __init__(self, cave=None, cavern_map=None):
        if cavern_map:
            self.cavern_map = cavern_map
        else:
            self.cavern_map = []

    def consult_notebook(self, step):
        tunnels = self.find_tunnels()
        dot = Graph(comment='Your notebook - explored caves', format='svg')
        for mapped_cave in self.cavern_map:
            warning_sources = ""
            if mapped_cave.warnings:
                dot.attr('node',color='yellow')
                warning_sources = ",".join([warning.source for warning in mapped_cave.warnings])
            else:
                dot.attr('node', color='green')
            current_location = '*' if mapped_cave.cave.id == step else ''
            dot.node(f'{mapped_cave.cave.id}',
                     f'{mapped_cave.cave.id} {current_location}',
                     _attributes=[('tooltip',f'{warning_sources}')])
        for tunnel in tunnels:
            dot.attr('node', color='black')
            dot.edge(f'{tunnel[0]}', f'{tunnel[1]}')
        dot.render(f'notes/notebook_{step}.gv', view=False)

    def find_tunnels(self):
        tunnels = set()
        for mapped_site in self.cavern_map:
            for neighboring_cave in mapped_site.cave.neighboring_caves:
                tunnel = (mapped_site.cave.id, neighboring_cave)\
                    if mapped_site.cave.id < neighboring_cave else (neighboring_cave, mapped_site.cave.id)
                tunnels.add(tunnel)
        return tunnels

    def note_position(self, cave, warnings):
        # Avoid adding duplicates if the hunter backtracks
        if cave.id not in [mapped_site.cave.id for mapped_site in self.cavern_map]:
            self.cavern_map.append(Mapped_Site(cave, warnings))

    def to_json(self):
        json_array = []
        for mapped_site in self.cavern_map:
            json_object = {
                            "cave_id": mapped_site.cave.id,
                            "warnings": [
                                {"type": warning.type, "source": warning.source, "content": warning.content}
                                for warning in mapped_site.warnings
                            ]
                          }
            json_array.append(json_object)
        return json_array

    @staticmethod
    def from_json(cavern_system, json_array):
        cavern_map = []
        for json_object in json_array:
            cave = cavern_system.get_cave(json_object['cave_id'])
            status_messages = []
            for warning in json_object['warnings']:
                status_messages.append(StatusMessage(warning['type'], warning['source'], warning['content']))
            mapped_site = Mapped_Site(cave, status_messages)
            cavern_map.append(mapped_site)
        return cavern_map



