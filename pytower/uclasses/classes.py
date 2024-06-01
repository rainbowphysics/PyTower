from typing import Annotated

from .primitives import Colorable
from .properties import FloatProperty, SerializedName, StructProperty, TUObjectPropertyCollection, suitebro_dataclass

@suitebro_dataclass
class InventoryItem(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class ActorComponent(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class CondoSettings(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class Actor(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseTimeCycler(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class StaticMeshActor(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseDrivable_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class Stairs_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class FloatingTextSign_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseAquarium_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseSeatColorable_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class InventoryItemIO(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class IOModuleBase_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseGWProxy_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseSeat_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseFileSaveObject(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class BaseItemCurrency_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class NightclubMediaPlayer_C(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class PhysicalMediaShelf_C(InventoryItem):
    spacer_multiplier: Annotated[float, FloatProperty(), SerializedName('SpacerMultiplier')]

@suitebro_dataclass
class CondoEditableSurface_C(TUObjectPropertyCollection):
    surface_colorable: Annotated[Colorable, StructProperty(Colorable), SerializedName('SurfaceColorable')]

@suitebro_dataclass
class WeatherManifestEntry(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class GuitarChordPalette(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class LaserExpressionPreset(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class LaserProjectionIndex(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class LocationInfo(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class LocationRules(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class SplineSaveData(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class WorkshopFile(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class NPCWearables(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class PhysicalMediaShelfData(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class PostProcessVolumeSettings(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class FogVolumeSettings(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class SkyVolumeSettings(TUObjectPropertyCollection):
    pass

@suitebro_dataclass
class PlayerTrustSaveData(TUObjectPropertyCollection):
    pass