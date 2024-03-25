from towerpy import tower
from towerpy.suitebro import Suitebro, TowerObject

TOOL_NAME = 'Rescale'


def main(suitebro: Suitebro, selection: list[TowerObject], args):
    if len(args) == 0:
        scaling_factor = input('Type in scaling factor: ')
        try:
            scaling_factor = float(scaling_factor)
        except Exception as e:
            print(f'Invalid scaling factor: {e}')
            return
    else:
        scaling_factor = args[0]

    for obj in suitebro.items():
        obj.item['position']['x'] *= scaling_factor
        obj.item['position']['y'] *= scaling_factor
        obj.item['position']['z'] *= scaling_factor
        obj.item['scale']['x'] *= scaling_factor
        obj.item['scale']['y'] *= scaling_factor
        obj.item['scale']['z'] *= scaling_factor


if __name__ == '__main__':
    tower.main('CondoData', main, args={'parameters': [2]})
