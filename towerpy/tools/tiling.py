from towerpy import tower
from towerpy.selection import GroupSelection, ItemSelection
from towerpy.suitebro import Suitebro, TowerObject

TOOL_NAME = 'Tiling'


def parse_inputs(tiling, offsets, group_id=-1):
    try:
        tiling_split = tiling.split(',')
        tile_x = int(tiling_split[0])
        tile_y = int(tiling_split[1])
        tile_z = int(tiling_split[2])
        offsets_split = offsets.split(',')
        offset_x = float(offsets_split[0])
        offset_y = float(offsets_split[1])
        offset_z = float(offsets_split[2])
        group_id = int(group_id)
        return tile_x, tile_y, tile_z, offset_x, offset_y, offset_z, group_id
    except Exception as e:
        print(f'Invalid input: {e}')
        return None


def main(suitebro: Suitebro, selection: list[TowerObject], args):
    if len(args) == 0:
        tiling = input('Type in tiling dimensions in x,y,z format: ')
        offsets = input('Type in tiling offset in x,y,z format: ')
        group = input('(Optional) Type in group id to tile (or leave blank for all):')
        if group is None or group == '':
            group = -1
        nx, ny, nz, dx, dy, dz, group_id = parse_inputs(tiling, offsets, group)
    else:
        if len(args) == 2:
            nx, ny, nz, dx, dy, dz, group_id = parse_inputs(args[0], args[1])
        elif len(args) >= 3:
            nx, ny, nz, dx, dy, dz, group_id = parse_inputs(args[0], args[1], args[2])
        else:
            print('Incorrect number of inputs')
            return

    print(f'Running Tiling tool with parameters: nx={nx}, ny={ny}, nz={nz}, dx={dx}, dy={dy}, dz={dz}, '
          f'group_id={group_id}')

    if group_id != -1:
        group_sel = GroupSelection(group_id)
        template_objects = group_sel.select(selection)
    else:
        template_objects = ItemSelection().select(selection)

    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                # Don't repeat the tiling source
                if x == 0 and y == 0 and z == 0:
                    continue

                copies = TowerObject.copy_group(template_objects)

                # Set position
                for obj in copies:
                    obj.item['position']['x'] += dx * x
                    obj.item['position']['y'] += dy * y
                    obj.item['position']['z'] += dz * z

                suitebro.add_objects(copies)


if __name__ == '__main__':
    tower.main('CondoData', main, args={'parameters': ['5,5,5', '70,70,70']})
