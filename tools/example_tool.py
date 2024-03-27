from pytower.suitebro import Suitebro
from pytower.selection import RegexSelector

TOOL_NAME = 'ExampleTool'

def main(suitebro: Suitebro, args):
    #TODO not the right place for this, should be a generic message
    #print(f'Running {TOOL_NAME} with arguments {args}...')
    objects = suitebro.objects
    selection = RegexSelector('Canvas.*')
    canvases = selection.select(objects)
    for obj in canvases:
        pass

