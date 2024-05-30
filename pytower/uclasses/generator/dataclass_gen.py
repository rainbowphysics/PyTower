import builtins
from collections import OrderedDict, deque
from dataclasses import dataclass
import itertools
import os
from typing import TYPE_CHECKING, Any, Callable, Concatenate, Generic, Iterable, Iterator, Optional, ParamSpec, Protocol, Reversible, Sequence, TypeAlias, TypeVar, TypeVarTuple, TypedDict, Union, cast, overload
import json
import io
import functools
import re

from pytower.uclasses.generator.topo_sort import DAG

class _ArrayOfType(TypedDict):
    ArrayOfPropertyName: str
    Type: str
    StructType: Optional[str]
    ObjectClass: Optional[str]

class Property(TypedDict):
    Name: str
    Type: str
    StructType: Optional[str]
    ArrayOfType: Optional[_ArrayOfType]
    EnumType: Optional[str]
    ObjectClass: Optional[str]

class UClass(TypedDict):
    Name: str
    SuperName: str
    Properties: list[Property]

# https://stackoverflow.com/a/1176023
pattern = re.compile(
    r"""
        (?<=[a-z])      # preceded by lowercase
        (?=[A-Z])       # followed by uppercase
        |               #   OR
        (?<=[A-Z])       # preceded by lowercase
        (?=[A-Z][a-z])  # followed by uppercase, then lowercase
    """,
    re.X,
)
pattern2 = re.compile(r"^[^a-z]$")
def camel_to_snake(s: str):
    if pattern2.match(s): # if is all uppercase
        return s.lower()

    s = s.replace('URLs', '_urls')
    s = s.replace(' ', '_') # remove spaces
    s = pattern.sub('_', s) # other stuff
    s = s.replace('__', '_') # remove dupe undesrcores
    return s.lower()

T = TypeVar('T')
def uniq(iterable: Iterable[T]) -> list[T]:
    return list(OrderedDict.fromkeys(iterable))

if __name__ == '__main__':
    with io.open(r"E:\TempStuff\uextract\bin\Debug\net8.0\output.json", 'r') as f:
        classes = cast(list[UClass], json.load(f))

    code = '''
from typing import Annotated
from .properties import ArrayProperty, BoolProperty, ByteProperty, StrProperty, StructProperty, TextProperty, EnumProperty, FloatProperty, IntProperty, NameProperty, ObjectProperty, SerializedName, Name, Object, UEnum, suitebro_dataclass
from .primitives import Colorable, Guid, LinearColor, Rotator, Transform, Vector
from .classes import \\
    ActorComponent, \\
    CondoSettings, \\
    Actor, \\
    BaseTimeCycler, \\
    InventoryItem, \\
    PlayerTrustSaveData, \\
    StaticMeshActor, \\
    BaseDrivable_C, \\
    Stairs_C, \\
    FloatingTextSign_C, \\
    BaseAquarium_C, \\
    BaseSeatColorable_C, \\
    InventoryItemIO, \\
    IOModuleBase_C, \\
    BaseGWProxy_C, \\
    BaseSeat_C, \\
    BaseFileSaveObject, \\
    BaseItemCurrency_C, \\
    NightclubMediaPlayer_C, \\
    WeatherManifestEntry, \\
    GuitarChordPalette, \\
    LaserExpressionPreset, \\
    LaserProjectionIndex, \\
    LocationInfo, \\
    LocationRules, \\
    SplineSaveData, \\
    WorkshopFile, \\
    NPCWearables, \\
    PhysicalMediaShelfData, \\
    PostProcessVolumeSettings, \\
    FogVolumeSettings, \\
    SkyVolumeSettings

'''.lstrip()

    #classes_keyed = itertools.groupby(classes, lambda x: x['SuperName'])

    class_set = list(set([c['SuperName'] for c in classes] + [c['Name'] for c in classes]))
    class_set.sort()
    class_set = list(reversed(class_set))

    classes = dict((v['Name'], v) for v in classes)

    dag = DAG(len(class_set))
    for i, k in enumerate(class_set):
        if k in classes:
            cls = classes[k]
            dag.add_edge(class_set.index(cls['SuperName']), i)
    class_indices = dag.topological_sort()


    for i in class_indices:
        k = class_set[i]
        if k not in classes:
#            code += f'''
#@suitebro_dataclass
#class {k}(TUObjectPropertyCollection):
#    pass
#'''
            print(k)
            continue

        cls = classes[k]

        code += f'''
@suitebro_dataclass
class {re.sub(r'[^a-zA-Z_0-9]', '', cls['Name'])}({cls['SuperName']}):
'''

        props = cls['Properties']

        for fld in props:
            py_name = camel_to_snake(fld['Name'])

            match fld['Type']:
                case 'Struct':
                    code += f"    {py_name}: Annotated[{fld['StructType']}, StructProperty({fld['StructType']}), SerializedName(\'{fld['Name']}\')]\n"
                case 'Bool':
                    code += f"    {py_name}: Annotated[bool, BoolProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Int':
                    code += f"    {py_name}: Annotated[int, IntProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Float':
                    code += f"    {py_name}: Annotated[float, FloatProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Str':
                    code += f"    {py_name}: Annotated[str, StrProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Byte':
                    code += f"    {py_name}: Annotated[int, ByteProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Object':
                    code += f"    {py_name}: Annotated[Object, ObjectProperty(\'{fld['ObjectClass']}\'), SerializedName(\'{fld['Name']}\')]\n"
                case 'Name':
                    code += f"    {py_name}: Annotated[Name, NameProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Enum':
                    code += f"    {py_name}: Annotated[UEnum, EnumProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Text':
                    code += f"    {py_name}: Annotated[str, TextProperty(), SerializedName(\'{fld['Name']}\')]\n"
                case 'Array':
                    if 'ArrayOfType' not in fld or not fld['ArrayOfType']: raise SyntaxError('FUCK')

                    aot = fld['ArrayOfType']

                    match aot['Type']:
                        case 'Struct':
                            code += f"    {py_name}: Annotated[list[{aot['StructType']}], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', StructProperty({aot['StructType']})), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Bool':
                            code += f"    {py_name}: Annotated[list[bool], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', BoolProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Int':
                            code += f"    {py_name}: Annotated[list[int], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', IntProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Float':
                            code += f"    {py_name}: Annotated[list[float], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', FloatProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Str':
                            code += f"    {py_name}: Annotated[list[str], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', StrProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Byte':
                            code += f"    {py_name}: Annotated[list[int], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', ByteProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Object':
                            code += f"    {py_name}: Annotated[list[Object], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', ObjectProperty(\'{aot['ObjectClass']}\')), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Name':
                            code += f"    {py_name}: Annotated[list[Name], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', NameProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Enum':
                            code += f"    {py_name}: Annotated[list[UEnum], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', EnumProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case 'Text':
                            code += f"    {py_name}: Annotated[list[str], ArrayProperty(\'{aot['ArrayOfPropertyName']}\', TextProperty()), SerializedName(\'{fld['Name']}\')]\n"
                        case _:
                            raise SyntaxError('FUCK')
                case _:
                    raise SyntaxError('FUCK')

    with io.open(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'generated_classes.py')), 'w') as f:
        f.write(code)