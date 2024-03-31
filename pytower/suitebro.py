from .selection import Selection
from .object import TowerObject


class Suitebro:
    def __init__(self, data: dict):
        self.data: dict = data

        # Parse objects
        prop_section = self.data['properties']
        item_section = self.data['items']
        self.objects: list[TowerObject | None] = [None] * len(prop_section)

        item_idx = 0
        for x in range(len(prop_section)):
            p = prop_section[x]
            i = item_section[item_idx]
            if p['name'].startswith(i['name']):
                self.objects[x] = TowerObject(self, item=i, properties=p)
                item_idx += 1
            else:
                self.objects[x] = TowerObject(self, item=None, properties=p)

    def add_object(self, obj):
        self.objects += [obj]

    def add_objects(self, objs):
        self.objects += objs

    def find_item(self, name: str) -> TowerObject | None:
        for obj in self.objects:
            if obj.matches_name(name):
                return obj
        return None

    def get_groups_meta(self):
        return self.data['groups']

    # TODO Definitely a better way to do this
    def get_max_groupid(self):
        sel = Selection(self.objects)
        # Get the max group_id tuple in group and get its id (first slot of tuple)
        return max(sel.groups(), key=lambda group_data: group_data[0])[0]

    def update_groups_meta(self):
        sel = Selection(self.objects)
        group_data = []
        for group_id, group in sel.groups():
            group_data.append({'group_id': group_id, 'item_count': len(group)})
        self.data['groups'] = group_data

    # Returns all non-property TowerObjects
    def items(self) -> list[TowerObject]:
        return [obj for obj in self.objects if obj.item is not None]

    # Convert item list back into a dict
    def to_dict(self):
        new_dict = {}

        # Update groups based on group ids and info
        self.update_groups_meta()

        for k, v in self.data.items():
            if k != 'items' and k != 'properties':
                new_dict[k] = v

        self.objects.sort()

        num_obj = len(self.objects)
        item_arr = [None] * num_obj
        prop_arr = [None] * num_obj

        item_idx = 0
        prop_idx = 0

        last_name = None
        last_num = 0
        for obj in self.objects:
            if obj.item is not None:
                item_arr[item_idx] = obj.item
                item_idx += 1
            if obj.properties is not None:
                # Name fuckery TODO determine if the naming even matters
                if obj.item is not None:
                    name_split = obj.properties['name'].split('_')
                    root_name = '_'.join(name_split[:-1])

                    if last_name == root_name:
                        last_num += 1
                    else:
                        last_num = 0

                    obj.properties['name'] = root_name + '_' + str(last_num)

                    last_name = root_name

                # Now actually add to prop_arr
                prop_arr[prop_idx] = obj.properties
                prop_idx += 1

        item_arr = item_arr[:item_idx]
        prop_arr = prop_arr[:prop_idx]

        # Finally set new dictionary and return
        new_dict['items'] = item_arr
        new_dict['properties'] = prop_arr
        return new_dict

    def __repl__(self):
        return f'Suitebro({self.data}, {self.objects})'

    def __iter__(self):
        for obj in self.objects:
            yield obj
