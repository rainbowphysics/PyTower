from typing import Annotated
from .properties import ArrayProperty, BoolProperty, ByteProperty, StrProperty, StructProperty, TextProperty, EnumProperty, FloatProperty, IntProperty, NameProperty, ObjectProperty, SerializedName, Name, Object, UEnum, suitebro_dataclass
from .primitives import Colorable, Guid, LinearColor, Rotator, Transform, Vector
from .classes import \
    ActorComponent, \
    CondoSettings, \
    Actor, \
    BaseTimeCycler, \
    InventoryItem, \
    PlayerTrustSaveData, \
    StaticMeshActor, \
    BaseDrivable_C, \
    Stairs_C, \
    FloatingTextSign_C, \
    BaseAquarium_C, \
    BaseSeatColorable_C, \
    InventoryItemIO, \
    IOModuleBase_C, \
    BaseGWProxy_C, \
    BaseSeat_C, \
    BaseFileSaveObject, \
    BaseItemCurrency_C, \
    NightclubMediaPlayer_C, \
    WeatherManifestEntry, \
    GuitarChordPalette, \
    LaserExpressionPreset, \
    LaserProjectionIndex, \
    LocationInfo, \
    LocationRules, \
    SplineSaveData, \
    WorkshopFile, \
    NPCWearables, \
    PhysicalMediaShelfData, \
    PostProcessVolumeSettings, \
    FogVolumeSettings, \
    SkyVolumeSettings


@suitebro_dataclass
class AquariumLarge_C(BaseAquarium_C):
    decorations_visibility: Annotated[bool, BoolProperty(), SerializedName('Decorations_Visibility')]

@suitebro_dataclass
class AquariumShelf_C(BaseAquarium_C):
    decorations_visibility: Annotated[bool, BoolProperty(), SerializedName('Decorations_Visibility')]

@suitebro_dataclass
class Aquarium_C(BaseAquarium_C):
    decorations_visibility: Annotated[bool, BoolProperty(), SerializedName('Decorations_Visibility')]

@suitebro_dataclass
class BaseHouseDoor_C(Actor):
    opened: Annotated[bool, BoolProperty(), SerializedName('Opened')]

@suitebro_dataclass
class BaseInstrument_C(BaseDrivable_C):
    scale_affects_pitch: Annotated[bool, BoolProperty(), SerializedName('ScaleAffectsPitch')]
    sound_variation_id: Annotated[int, IntProperty(), SerializedName('SoundVariationID')]
    volume: Annotated[float, FloatProperty(), SerializedName('Volume')]

@suitebro_dataclass
class AlwaysLuckySlotMachine_C(BaseItemCurrency_C):
    has_glow: Annotated[bool, BoolProperty(), SerializedName('HasGlow')]

@suitebro_dataclass
class ChairPlasticGarden_C(BaseSeatColorable_C):
    un_gunked: Annotated[bool, BoolProperty(), SerializedName('UnGunked')]

@suitebro_dataclass
class CondoLightManager_C(Actor):
    intensity: Annotated[float, FloatProperty(), SerializedName('Intensity')]
    lights_on: Annotated[bool, BoolProperty(), SerializedName('LightsOn')]
    color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('Color')]
    light_function: Annotated[int, ByteProperty(), SerializedName('LightFunction')]
    time_of_day_toggle: Annotated[bool, BoolProperty(), SerializedName('TimeOfDayToggle')]
    time_of_day_state_day: Annotated[bool, BoolProperty(), SerializedName('TimeOfDayStateDay')]
    should_cast_shadows: Annotated[bool, BoolProperty(), SerializedName('ShouldCastShadows')]

@suitebro_dataclass
class CondoSettingsManager_C(CondoSettings):
    trust_info_saved: Annotated[PlayerTrustSaveData, StructProperty(PlayerTrustSaveData), SerializedName('TrustInfoSaved')]

@suitebro_dataclass
class CondoWeather_C(Actor):
    weather_configuration_new: Annotated[WeatherManifestEntry, StructProperty(WeatherManifestEntry), SerializedName('WeatherConfigurationNew')]
    weather_transition_time: Annotated[float, FloatProperty(), SerializedName('WeatherTransitionTime')]
    weather_switch_interval: Annotated[float, FloatProperty(), SerializedName('WeatherSwitchInterval')]
    weather_configuration_checklist: Annotated[list[bool], ArrayProperty('WeatherConfigurationChecklist', BoolProperty()), SerializedName('WeatherConfigurationChecklist')]
    truly_random_weather_selection: Annotated[bool, BoolProperty(), SerializedName('TrulyRandomWeatherSelection')]
    weather_cycler_enabled: Annotated[bool, BoolProperty(), SerializedName('WeatherCyclerEnabled')]

@suitebro_dataclass
class FutonCouch_C(BaseSeatColorable_C):
    down: Annotated[bool, BoolProperty(), SerializedName('Down')]

@suitebro_dataclass
class GW_BallRaceSpawn_C(BaseGWProxy_C):
    bonus: Annotated[bool, BoolProperty(), SerializedName('Bonus')]
    level: Annotated[int, IntProperty(), SerializedName('Level')]

@suitebro_dataclass
class GW_MinigolfHole_C(BaseGWProxy_C):
    hole: Annotated[int, IntProperty(), SerializedName('Hole')]

@suitebro_dataclass
class GW_MinigolfStart_C(BaseGWProxy_C):
    hole: Annotated[int, IntProperty(), SerializedName('Hole')]
    par: Annotated[int, IntProperty(), SerializedName('Par')]
    name: Annotated[str, StrProperty(), SerializedName('Name')]

@suitebro_dataclass
class GW_SDNLFlag_C(BaseGWProxy_C):
    team: Annotated[UEnum, EnumProperty(), SerializedName('Team')]

@suitebro_dataclass
class GuitarChordPaletteSave_C(BaseFileSaveObject):
    palette: Annotated[GuitarChordPalette, StructProperty(GuitarChordPalette), SerializedName('Palette')]

@suitebro_dataclass
class Counter_C(IOModuleBase_C):
    counter: Annotated[float, FloatProperty(), SerializedName('Counter')]
    counter_min: Annotated[float, FloatProperty(), SerializedName('CounterMin')]
    counter_max: Annotated[float, FloatProperty(), SerializedName('CounterMax')]
    persistent_save: Annotated[bool, BoolProperty(), SerializedName('PersistentSave')]
    show_value: Annotated[bool, BoolProperty(), SerializedName('ShowValue')]

@suitebro_dataclass
class BaseCanvas_C(InventoryItem):
    url: Annotated[str, StrProperty(), SerializedName('URL')]
    scale: Annotated[float, FloatProperty(), SerializedName('Scale')]
    type: Annotated[int, ByteProperty(), SerializedName('Type')]
    canvas_shape: Annotated[int, ByteProperty(), SerializedName('CanvasShape')]
    emissive: Annotated[float, FloatProperty(), SerializedName('Emissive')]
    scale_x: Annotated[float, FloatProperty(), SerializedName('ScaleX')]
    scale_y: Annotated[float, FloatProperty(), SerializedName('ScaleY')]
    scale_z: Annotated[float, FloatProperty(), SerializedName('ScaleZ')]
    world_scale: Annotated[Vector, StructProperty(Vector), SerializedName('WorldScale')]
    tiling: Annotated[Vector, StructProperty(Vector), SerializedName('Tiling')]
    cache_to_disk: Annotated[bool, BoolProperty(), SerializedName('CacheToDisk')]
    additional_urls: Annotated[list[str], ArrayProperty('AdditionalURLs', StrProperty()), SerializedName('AdditionalURLs')]
    surface_material: Annotated[Object, ObjectProperty('MaterialInterface'), SerializedName('SurfaceMaterial')]
    surface_colorable: Annotated[Colorable, StructProperty(Colorable), SerializedName('SurfaceColorable')]
    animation_mode: Annotated[bool, BoolProperty(), SerializedName('AnimationMode')]
    animation_columns: Annotated[int, IntProperty(), SerializedName('AnimationColumns')]
    animation_rows: Annotated[int, IntProperty(), SerializedName('AnimationRows')]
    animation_rate: Annotated[float, FloatProperty(), SerializedName('AnimationRate')]
    world_align_canvas: Annotated[bool, BoolProperty(), SerializedName('WorldAlignCanvas')]
    nsfw: Annotated[bool, BoolProperty(), SerializedName('NSFW')]
    rotation: Annotated[float, FloatProperty(), SerializedName('Rotation')]

@suitebro_dataclass
class BalloonCanvas_C(BaseCanvas_C):
    length: Annotated[float, FloatProperty(), SerializedName('Length')]

@suitebro_dataclass
class BaseCanvasMultiMesh_C(BaseCanvas_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class CanvasCartridges_C(BaseCanvasMultiMesh_C):
    frame_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('FrameColor')]

@suitebro_dataclass
class CanvasJewelcase_C(BaseCanvasMultiMesh_C):
    frame_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('FrameColor')]
    format_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('FormatColor')]

@suitebro_dataclass
class CanvasCartridge_C(BaseCanvas_C):
    index: Annotated[Name, NameProperty(), SerializedName('Index')]
    cart_colour: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('CartColour')]

@suitebro_dataclass
class CanvasDecal_C(BaseCanvas_C):
    roughness: Annotated[float, FloatProperty(), SerializedName('Roughness')]

@suitebro_dataclass
class CanvasElbow_C(BaseCanvas_C):
    radius: Annotated[int, IntProperty(), SerializedName('Radius')]
    thickness: Annotated[int, IntProperty(), SerializedName('Thickness')]
    division: Annotated[int, IntProperty(), SerializedName('Division')]
    cut: Annotated[int, IntProperty(), SerializedName('Cut')]

@suitebro_dataclass
class CanvasFloppyDiskette_C(BaseCanvas_C):
    frame_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('FrameColor')]

@suitebro_dataclass
class CanvasTorus_C(BaseCanvas_C):
    radius: Annotated[int, IntProperty(), SerializedName('Radius')]
    thickness: Annotated[int, IntProperty(), SerializedName('Thickness')]
    division: Annotated[int, IntProperty(), SerializedName('Division')]
    cut: Annotated[int, IntProperty(), SerializedName('Cut')]

@suitebro_dataclass
class CanvasVHS_C(BaseCanvas_C):
    frame_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('FrameColor')]

@suitebro_dataclass
class DoorCanvasTall_C(BaseCanvas_C):
    opened: Annotated[bool, BoolProperty(), SerializedName('Opened')]
    auto_close: Annotated[bool, BoolProperty(), SerializedName('AutoClose')]
    locked: Annotated[bool, BoolProperty(), SerializedName('Locked')]
    open_on_spawn: Annotated[bool, BoolProperty(), SerializedName('OpenOnSpawn')]
    auto_close_delay: Annotated[float, FloatProperty(), SerializedName('AutoCloseDelay')]
    is_condo_hub_door: Annotated[bool, BoolProperty(), SerializedName('IsCondoHubDoor')]
    frame_enabled: Annotated[bool, BoolProperty(), SerializedName('FrameEnabled')]
    automatic: Annotated[bool, BoolProperty(), SerializedName('Automatic')]
    hinge_vis: Annotated[bool, BoolProperty(), SerializedName('HingeVis')]
    rotation_angle: Annotated[float, FloatProperty(), SerializedName('RotationAngle')]
    invert_rotation: Annotated[bool, BoolProperty(), SerializedName('InvertRotation')]

@suitebro_dataclass
class BaseColorable_C(InventoryItem):
    colors: Annotated[list[LinearColor], ArrayProperty('Colors', StructProperty(LinearColor)), SerializedName('Colors')]

@suitebro_dataclass
class AdjustableMicrophone_C(BaseColorable_C):
    height: Annotated[float, FloatProperty(), SerializedName('Height')]
    tilt: Annotated[float, FloatProperty(), SerializedName('Tilt')]

@suitebro_dataclass
class Balloon_C(BaseColorable_C):
    length: Annotated[float, FloatProperty(), SerializedName('Length')]

@suitebro_dataclass
class Balloon_FoilShapes_C(Balloon_C):
    active_balloon: Annotated[int, IntProperty(), SerializedName('ActiveBalloon')]

@suitebro_dataclass
class BarrelMetal_C(BaseColorable_C):
    lid: Annotated[bool, BoolProperty(), SerializedName('Lid')]
    clean: Annotated[bool, BoolProperty(), SerializedName('Clean')]

@suitebro_dataclass
class BarrelPlastic_C(BaseColorable_C):
    lid: Annotated[bool, BoolProperty(), SerializedName('Lid')]
    damage: Annotated[bool, BoolProperty(), SerializedName('Damage')]
    clean: Annotated[bool, BoolProperty(), SerializedName('Clean')]

@suitebro_dataclass
class BaseBalloon_C(BaseColorable_C):
    length: Annotated[float, FloatProperty(), SerializedName('Length')]

@suitebro_dataclass
class BaseBed_C(BaseColorable_C):
    can_sleep: Annotated[bool, BoolProperty(), SerializedName('CanSleep')]

@suitebro_dataclass
class DressedMattress_C(BaseBed_C):
    comforter: Annotated[bool, BoolProperty(), SerializedName('Comforter')]

@suitebro_dataclass
class BaseDoor_C(BaseColorable_C):
    opened: Annotated[bool, BoolProperty(), SerializedName('Opened')]
    is_condo_hub_door: Annotated[bool, BoolProperty(), SerializedName('IsCondoHubDoor')]
    auto_close: Annotated[bool, BoolProperty(), SerializedName('AutoClose')]
    auto_close_delay: Annotated[float, FloatProperty(), SerializedName('AutoCloseDelay')]
    locked: Annotated[bool, BoolProperty(), SerializedName('Locked')]
    open_on_spawn: Annotated[bool, BoolProperty(), SerializedName('OpenOnSpawn')]
    rotation_angle: Annotated[float, FloatProperty(), SerializedName('RotationAngle')]
    automatic: Annotated[bool, BoolProperty(), SerializedName('Automatic')]
    frame_enabled: Annotated[bool, BoolProperty(), SerializedName('FrameEnabled')]
    invert_rotation: Annotated[bool, BoolProperty(), SerializedName('InvertRotation')]
    hidden: Annotated[bool, BoolProperty(), SerializedName('Hidden')]
    locked_prompt: Annotated[str, StrProperty(), SerializedName('LockedPrompt')]

@suitebro_dataclass
class BaseDoorMulti_C(BaseDoor_C):
    opened_right: Annotated[bool, BoolProperty(), SerializedName('OpenedRight')]

@suitebro_dataclass
class DumpsterOpening_C(BaseDoorMulti_C):
    label: Annotated[bool, BoolProperty(), SerializedName('Label')]
    clean: Annotated[bool, BoolProperty(), SerializedName('Clean')]
    range: Annotated[float, FloatProperty(), SerializedName('Range')]

@suitebro_dataclass
class FridgeClassic_C(BaseDoorMulti_C):
    shelves: Annotated[bool, BoolProperty(), SerializedName('Shelves')]
    range: Annotated[float, FloatProperty(), SerializedName('Range')]

@suitebro_dataclass
class CurtainBasicDouble_C(BaseDoor_C):
    pattern: Annotated[int, IntProperty(), SerializedName('Pattern')]
    type: Annotated[int, IntProperty(), SerializedName('Type')]

@suitebro_dataclass
class CurtainBasic_C(BaseDoor_C):
    pattern: Annotated[int, IntProperty(), SerializedName('Pattern')]
    width: Annotated[int, IntProperty(), SerializedName('Width')]
    type: Annotated[int, IntProperty(), SerializedName('Type')]

@suitebro_dataclass
class DoorDungeonWood_C(BaseDoor_C):
    rounded: Annotated[bool, BoolProperty(), SerializedName('Rounded')]
    look_hole: Annotated[bool, BoolProperty(), SerializedName('LookHole')]

@suitebro_dataclass
class DoorVentHalf_C(BaseDoor_C):
    orientation: Annotated[bool, BoolProperty(), SerializedName('Orientation')]
    shape: Annotated[bool, BoolProperty(), SerializedName('Shape')]
    range: Annotated[float, FloatProperty(), SerializedName('Range')]

@suitebro_dataclass
class DoorVent_C(BaseDoor_C):
    orientation: Annotated[bool, BoolProperty(), SerializedName('Orientation')]
    shape: Annotated[bool, BoolProperty(), SerializedName('Shape')]
    range: Annotated[float, FloatProperty(), SerializedName('Range')]

@suitebro_dataclass
class FreezerHorizontal_C(BaseDoor_C):
    shelved: Annotated[bool, BoolProperty(), SerializedName('Shelved')]

@suitebro_dataclass
class BaseEmitter_C(BaseColorable_C):
    particle_velocity: Annotated[float, FloatProperty(), SerializedName('ParticleVelocity')]
    spawn_rate: Annotated[int, IntProperty(), SerializedName('SpawnRate')]
    time_off: Annotated[float, FloatProperty(), SerializedName('TimeOff')]
    time_on: Annotated[float, FloatProperty(), SerializedName('TimeOn')]
    active: Annotated[bool, BoolProperty(), SerializedName('Active')]
    is_on: Annotated[bool, BoolProperty(), SerializedName('IsOn')]

@suitebro_dataclass
class BaseFireplace_C(BaseColorable_C):
    chimney_height: Annotated[float, FloatProperty(), SerializedName('Chimney_Height')]
    texture_world_scale: Annotated[float, FloatProperty(), SerializedName('TextureWorldScale')]

@suitebro_dataclass
class FireplaceHuge_C(BaseFireplace_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class BaseLadderItem_C(BaseColorable_C):
    top_mesh_index: Annotated[int, IntProperty(), SerializedName('TopMeshIndex')]
    bot_mesh_index: Annotated[int, IntProperty(), SerializedName('BotMeshIndex')]
    num_sections: Annotated[int, IntProperty(), SerializedName('NumSections')]
    climb_up_target: Annotated[Vector, StructProperty(Vector), SerializedName('ClimbUpTarget')]
    climb_down_target: Annotated[Vector, StructProperty(Vector), SerializedName('ClimbDownTarget')]
    use_ladder_volume: Annotated[bool, BoolProperty(), SerializedName('UseLadderVolume')]
    custom_up_target: Annotated[bool, BoolProperty(), SerializedName('CustomUpTarget')]
    custom_down_target: Annotated[bool, BoolProperty(), SerializedName('CustomDownTarget')]

@suitebro_dataclass
class BaseLamp_C(BaseColorable_C):
    light_on: Annotated[bool, BoolProperty(), SerializedName('LightOn')]
    intensity: Annotated[float, FloatProperty(), SerializedName('Intensity')]
    attenuation_radius: Annotated[float, FloatProperty(), SerializedName('AttenuationRadius')]
    light_function: Annotated[int, ByteProperty(), SerializedName('LightFunction')]
    cone_angle: Annotated[float, FloatProperty(), SerializedName('ConeAngle')]
    should_cast_shadows: Annotated[bool, BoolProperty(), SerializedName('ShouldCastShadows')]
    rainbow: Annotated[bool, BoolProperty(), SerializedName('Rainbow')]
    ies: Annotated[Name, NameProperty(), SerializedName('IES')]
    play_switch_sound_io: Annotated[bool, BoolProperty(), SerializedName('PlaySwitchSoundIO')]

@suitebro_dataclass
class BaseLampDualString_C(BaseLamp_C):
    length: Annotated[float, FloatProperty(), SerializedName('Length')]

@suitebro_dataclass
class BaseLampString_C(BaseLamp_C):
    length: Annotated[float, FloatProperty(), SerializedName('Length')]

@suitebro_dataclass
class GhostLightString_C(BaseLampString_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class HeartLightString_C(BaseLampString_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class BrambleDeer_C(BaseLamp_C):
    antlers: Annotated[bool, BoolProperty(), SerializedName('Antlers')]

@suitebro_dataclass
class DiscoBallModern_C(BaseLamp_C):
    light_materials: Annotated[list[Object], ArrayProperty('LightMaterials', ObjectProperty('MaterialInstanceDynamic')), SerializedName('LightMaterials')]
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class DiscoBallRetro_C(BaseLamp_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class EmergencyLight_C(BaseLamp_C):
    spin_speed: Annotated[int, IntProperty(), SerializedName('SpinSpeed')]

@suitebro_dataclass
class FestiveLawnLight_C(BaseLamp_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class GasLantern_C(BaseLamp_C):
    handle: Annotated[float, FloatProperty(), SerializedName('Handle')]

@suitebro_dataclass
class HeartFloorLamp_C(BaseLamp_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class HeartLamp_C(BaseLamp_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class HeartLight_C(BaseLamp_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]

@suitebro_dataclass
class BaseMedia_C(BaseColorable_C):
    saved_playlist: Annotated[list[str], ArrayProperty('SavedPlaylist', StrProperty()), SerializedName('SavedPlaylist')]

@suitebro_dataclass
class BaseVideoMedia_C(BaseMedia_C):
    screen_desaturation: Annotated[float, FloatProperty(), SerializedName('ScreenDesaturation')]
    screen_scanlines: Annotated[bool, BoolProperty(), SerializedName('ScreenScanlines')]
    screen_glare: Annotated[float, FloatProperty(), SerializedName('ScreenGlare')]
    allow_vote_skip: Annotated[bool, BoolProperty(), SerializedName('AllowVoteSkip')]
    voteskip_ratio: Annotated[float, FloatProperty(), SerializedName('VoteskipRatio')]
    admin_only_mode: Annotated[bool, BoolProperty(), SerializedName('AdminOnlyMode')]

@suitebro_dataclass
class Cellphone_C(BaseVideoMedia_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class BaseMultiMesh_C(BaseColorable_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class CatwalkModular_C(BaseMultiMesh_C):
    handrail: Annotated[bool, BoolProperty(), SerializedName('Handrail')]

@suitebro_dataclass
class CatwalkModularStairs_C(CatwalkModular_C):
    railing_top: Annotated[int, IntProperty(), SerializedName('RailingTop')]
    railing_bottom: Annotated[int, IntProperty(), SerializedName('RailingBottom')]

@suitebro_dataclass
class DoorframeBasic_C(BaseMultiMesh_C):
    frame_material: Annotated[int, IntProperty(), SerializedName('FrameMaterial')]

@suitebro_dataclass
class FXLightbeam_C(BaseMultiMesh_C):
    density: Annotated[float, FloatProperty(), SerializedName('Density')]

@suitebro_dataclass
class GlassBlocks_C(BaseMultiMesh_C):
    mortar: Annotated[bool, BoolProperty(), SerializedName('Mortar')]

@suitebro_dataclass
class BaseMultiType_C(BaseColorable_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class BaseRotating_C(BaseColorable_C):
    enabled: Annotated[bool, BoolProperty(), SerializedName('Enabled')]

@suitebro_dataclass
class BaseSign_C(BaseColorable_C):
    selected_font: Annotated[int, IntProperty(), SerializedName('SelectedFont')]
    title: Annotated[str, StrProperty(), SerializedName('Title')]
    date: Annotated[str, StrProperty(), SerializedName('Date')]
    large_text: Annotated[str, StrProperty(), SerializedName('LargeText')]
    small_box1_font_size: Annotated[float, FloatProperty(), SerializedName('SmallBox1 FontSize')]
    small_box2_font_size: Annotated[float, FloatProperty(), SerializedName('SmallBox2 FontSize')]
    large_box_font_size: Annotated[float, FloatProperty(), SerializedName('LargeBoxFontSize')]
    glow: Annotated[float, FloatProperty(), SerializedName('Glow')]
    vert_spacing: Annotated[float, FloatProperty(), SerializedName('VertSpacing')]

@suitebro_dataclass
class GravestoneSign_C(BaseSign_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class BaseSink_C(BaseColorable_C):
    fill: Annotated[bool, BoolProperty(), SerializedName('Fill')]
    constant_flow: Annotated[bool, BoolProperty(), SerializedName('ConstantFlow')]

@suitebro_dataclass
class BloodiedAxe_C(BaseColorable_C):
    bloody: Annotated[bool, BoolProperty(), SerializedName('Bloody')]

@suitebro_dataclass
class BloodiedMachete_C(BaseColorable_C):
    bloody: Annotated[bool, BoolProperty(), SerializedName('Bloody')]

@suitebro_dataclass
class CabinWood_C(BaseColorable_C):
    stripped: Annotated[bool, BoolProperty(), SerializedName('Stripped')]
    style: Annotated[int, IntProperty(), SerializedName('Style')]
    length: Annotated[int, IntProperty(), SerializedName('Length')]

@suitebro_dataclass
class Cabin_PanelDouble_C(BaseColorable_C):
    stripped: Annotated[bool, BoolProperty(), SerializedName('Stripped')]
    length: Annotated[int, IntProperty(), SerializedName('Length')]
    style: Annotated[int, IntProperty(), SerializedName('Style')]

@suitebro_dataclass
class Cabin_Panel_C(BaseColorable_C):
    stripped: Annotated[bool, BoolProperty(), SerializedName('Stripped')]
    length: Annotated[int, IntProperty(), SerializedName('Length')]
    style: Annotated[int, IntProperty(), SerializedName('Style')]

@suitebro_dataclass
class Cabin_Wall1_C(BaseColorable_C):
    stripped: Annotated[bool, BoolProperty(), SerializedName('Stripped')]
    length: Annotated[int, IntProperty(), SerializedName('Length')]
    style: Annotated[int, IntProperty(), SerializedName('Style')]

@suitebro_dataclass
class Cabin_Wall2_C(BaseColorable_C):
    stripped: Annotated[bool, BoolProperty(), SerializedName('Stripped')]
    length: Annotated[int, IntProperty(), SerializedName('Length')]
    style: Annotated[int, IntProperty(), SerializedName('Style')]

@suitebro_dataclass
class CatsackAnimated_C(BaseColorable_C):
    animation: Annotated[int, IntProperty(), SerializedName('Animation')]
    material: Annotated[bool, BoolProperty(), SerializedName('Material')]

@suitebro_dataclass
class DumpsterStatic_C(BaseColorable_C):
    lid: Annotated[bool, BoolProperty(), SerializedName('Lid')]
    label: Annotated[bool, BoolProperty(), SerializedName('Label')]
    clean: Annotated[bool, BoolProperty(), SerializedName('Clean')]

@suitebro_dataclass
class FestiveCushion_C(BaseColorable_C):
    pattern: Annotated[int, IntProperty(), SerializedName('Pattern')]

@suitebro_dataclass
class GearHollow_C(BaseColorable_C):
    speed: Annotated[int, IntProperty(), SerializedName('Speed')]
    teeth: Annotated[int, IntProperty(), SerializedName('Teeth')]
    active: Annotated[bool, BoolProperty(), SerializedName('Active')]

@suitebro_dataclass
class GreenhouseWall_C(BaseColorable_C):
    rotation_angle: Annotated[float, FloatProperty(), SerializedName('RotationAngle')]

@suitebro_dataclass
class BasePhysicsItem_C(InventoryItem):
    can_be_picked_up: Annotated[bool, BoolProperty(), SerializedName('CanBePickedUp')]
    respawn_location: Annotated[Transform, StructProperty(Transform), SerializedName('RespawnLocation')]
    respawn_on_thrown: Annotated[bool, BoolProperty(), SerializedName('RespawnOnThrown')]
    respawn_delay: Annotated[float, FloatProperty(), SerializedName('RespawnDelay')]
    mass_multiplier: Annotated[float, FloatProperty(), SerializedName('MassMultiplier')]
    simulate_on_respawn: Annotated[bool, BoolProperty(), SerializedName('SimulateOnRespawn')]
    colors: Annotated[list[LinearColor], ArrayProperty('Colors', StructProperty(LinearColor)), SerializedName('Colors')]
    shelfed: Annotated[bool, BoolProperty(), SerializedName('Shelfed')]

@suitebro_dataclass
class BalloonPhysics_C(BasePhysicsItem_C):
    helium: Annotated[bool, BoolProperty(), SerializedName('Helium')]

@suitebro_dataclass
class BarrelMetalPhysics_C(BasePhysicsItem_C):
    clean: Annotated[bool, BoolProperty(), SerializedName('Clean')]

@suitebro_dataclass
class BarrelPlasticPhysics_C(BasePhysicsItem_C):
    clean: Annotated[bool, BoolProperty(), SerializedName('Clean')]
    damaged: Annotated[bool, BoolProperty(), SerializedName('Damaged')]

@suitebro_dataclass
class BasePhysicalMedia_C(BasePhysicsItem_C):
    emissive: Annotated[float, FloatProperty(), SerializedName('Emissive')]
    url: Annotated[str, StrProperty(), SerializedName('URL')]
    media_url: Annotated[str, StrProperty(), SerializedName('MediaURL')]
    label: Annotated[str, StrProperty(), SerializedName('Label')]
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class BaseLibretroCartridge_C(BasePhysicalMedia_C):
    system: Annotated[int, ByteProperty(), SerializedName('System')]
    media_fetched_from_igdb: Annotated[str, StrProperty(), SerializedName('MediaFetchedFromIGDB')]

@suitebro_dataclass
class ChristmasSnowball_C(BasePhysicsItem_C):
    saved_scale: Annotated[float, FloatProperty(), SerializedName('SavedScale')]

@suitebro_dataclass
class CinderblockPhysics_C(BasePhysicsItem_C):
    mesh: Annotated[int, IntProperty(), SerializedName('Mesh')]

@suitebro_dataclass
class BasePlaceableFX_C(InventoryItem):
    color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('Color')]

@suitebro_dataclass
class BasePlaceableParticleFX_C(BasePlaceableFX_C):
    particle_id: Annotated[int, IntProperty(), SerializedName('ParticleID')]
    auto_start: Annotated[bool, BoolProperty(), SerializedName('AutoStart')]

@suitebro_dataclass
class BaseSoundEmitterItem_C(InventoryItem):
    selected_sound: Annotated[int, IntProperty(), SerializedName('SelectedSound')]
    play_interval_min: Annotated[float, FloatProperty(), SerializedName('PlayIntervalMin')]
    play_interval_max: Annotated[float, FloatProperty(), SerializedName('PlayIntervalMax')]
    pitch_min: Annotated[float, FloatProperty(), SerializedName('PitchMin')]
    pitch_max: Annotated[float, FloatProperty(), SerializedName('PitchMax')]
    range: Annotated[float, FloatProperty(), SerializedName('Range')]
    range_falloff: Annotated[float, FloatProperty(), SerializedName('RangeFalloff')]
    occlusion: Annotated[bool, BoolProperty(), SerializedName('Occlusion')]
    volume_min: Annotated[float, FloatProperty(), SerializedName('VolumeMin')]
    volume_max: Annotated[float, FloatProperty(), SerializedName('VolumeMax')]
    starts_active: Annotated[bool, BoolProperty(), SerializedName('StartsActive')]
    play_once: Annotated[bool, BoolProperty(), SerializedName('PlayOnce')]

@suitebro_dataclass
class BaseTargetable_C(InventoryItem):
    targets: Annotated[list[Vector], ArrayProperty('Targets', StructProperty(Vector)), SerializedName('Targets')]
    target_rotation: Annotated[Rotator, StructProperty(Rotator), SerializedName('TargetRotation')]

@suitebro_dataclass
class BaseRope_C(BaseTargetable_C):
    light_radius: Annotated[float, FloatProperty(), SerializedName('LightRadius')]
    light_visible: Annotated[bool, BoolProperty(), SerializedName('LightVisible')]
    light_intensity: Annotated[float, FloatProperty(), SerializedName('LightIntensity')]
    curve: Annotated[float, FloatProperty(), SerializedName('Curve')]
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]
    colors: Annotated[list[LinearColor], ArrayProperty('Colors', StructProperty(LinearColor)), SerializedName('Colors')]
    manual_colors: Annotated[bool, BoolProperty(), SerializedName('ManualColors')]

@suitebro_dataclass
class BaseWorkshopItem_C(InventoryItem):
    world_scale: Annotated[Vector, StructProperty(Vector), SerializedName('WorldScale')]
    item_metadata_scale: Annotated[float, FloatProperty(), SerializedName('ItemMetadataScale')]
    colors: Annotated[list[LinearColor], ArrayProperty('Colors', StructProperty(LinearColor)), SerializedName('Colors')]

@suitebro_dataclass
class BaseLibretro_C(BaseWorkshopItem_C):
    game_name: Annotated[str, StrProperty(), SerializedName('GameName')]
    system: Annotated[int, ByteProperty(), SerializedName('System')]
    screen_desaturation: Annotated[float, FloatProperty(), SerializedName('ScreenDesaturation')]
    screen_scanlines: Annotated[bool, BoolProperty(), SerializedName('ScreenScanlines')]
    screen_glare: Annotated[float, FloatProperty(), SerializedName('ScreenGlare')]

@suitebro_dataclass
class BaseWorkshopPhysicsItem_C(BaseWorkshopItem_C):
    can_be_picked_up: Annotated[bool, BoolProperty(), SerializedName('CanBePickedUp')]
    mass_multiplier: Annotated[float, FloatProperty(), SerializedName('MassMultiplier')]
    respawn_on_thrown: Annotated[bool, BoolProperty(), SerializedName('RespawnOnThrown')]
    respawn_location: Annotated[Transform, StructProperty(Transform), SerializedName('RespawnLocation')]
    respawn_delay: Annotated[float, FloatProperty(), SerializedName('RespawnDelay')]
    simulate_on_respawn: Annotated[bool, BoolProperty(), SerializedName('SimulateOnRespawn')]

@suitebro_dataclass
class BottleMessage_C(InventoryItem):
    message_id: Annotated[int, IntProperty(), SerializedName('MessageID')]

@suitebro_dataclass
class CustomSpawnPoint_C(InventoryItem):
    tag: Annotated[Name, NameProperty(), SerializedName('Tag')]
    blocked: Annotated[bool, BoolProperty(), SerializedName('Blocked')]
    is_checkpoint: Annotated[bool, BoolProperty(), SerializedName('IsCheckpoint')]
    team: Annotated[UEnum, EnumProperty(), SerializedName('Team')]

@suitebro_dataclass
class FloatingChat_C(InventoryItem):
    range: Annotated[int, IntProperty(), SerializedName('Range')]
    text_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('TextColor')]
    background_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('BackgroundColor')]
    text: Annotated[str, StrProperty(), SerializedName('Text')]

@suitebro_dataclass
class BaseVolume_C(InventoryItemIO):
    filter_players: Annotated[bool, BoolProperty(), SerializedName('FilterPlayers')]
    filter_physics: Annotated[bool, BoolProperty(), SerializedName('FilterPhysics')]
    filter_npcs: Annotated[bool, BoolProperty(), SerializedName('FilterNPCS')]
    filter_weapons: Annotated[bool, BoolProperty(), SerializedName('FilterWeapons')]
    filter_camera: Annotated[bool, BoolProperty(), SerializedName('FilterCamera')]
    filter_team_a: Annotated[bool, BoolProperty(), SerializedName('FilterTeamA')]
    filter_team_b: Annotated[bool, BoolProperty(), SerializedName('FilterTeamB')]
    filter_team_c: Annotated[bool, BoolProperty(), SerializedName('FilterTeamC')]
    filter_movers: Annotated[bool, BoolProperty(), SerializedName('FilterMovers')]

@suitebro_dataclass
class ButtonVolume_C(BaseVolume_C):
    prompt: Annotated[str, StrProperty(), SerializedName('Prompt')]

@suitebro_dataclass
class CommentVolume_C(BaseVolume_C):
    prompt: Annotated[str, StrProperty(), SerializedName('Prompt')]

@suitebro_dataclass
class DamageHealVolume_C(BaseVolume_C):
    deals_damage: Annotated[bool, BoolProperty(), SerializedName('DealsDamage')]
    deal_damage_amount: Annotated[int, IntProperty(), SerializedName('DealDamageAmount')]
    add_health_amount: Annotated[int, IntProperty(), SerializedName('AddHealthAmount')]
    rate: Annotated[float, FloatProperty(), SerializedName('Rate')]
    damage_type_id: Annotated[int, IntProperty(), SerializedName('DamageTypeID')]

@suitebro_dataclass
class DialogueVolume_C(BaseVolume_C):
    font: Annotated[int, ByteProperty(), SerializedName('Font')]
    camera_offset: Annotated[Vector, StructProperty(Vector), SerializedName('CameraOffset')]
    name: Annotated[str, StrProperty(), SerializedName('Name')]
    avatar_url: Annotated[str, StrProperty(), SerializedName('AvatarURL')]
    on_enter: Annotated[list[str], ArrayProperty('OnEnter', TextProperty()), SerializedName('OnEnter')]
    on_leave: Annotated[list[str], ArrayProperty('OnLeave', TextProperty()), SerializedName('OnLeave')]
    on_talk: Annotated[list[str], ArrayProperty('OnTalk', TextProperty()), SerializedName('OnTalk')]
    prompt: Annotated[str, StrProperty(), SerializedName('Prompt')]

@suitebro_dataclass
class GravityVolume_C(BaseVolume_C):
    gravity: Annotated[float, FloatProperty(), SerializedName('Gravity')]

@suitebro_dataclass
class HitTargetVolume_C(BaseVolume_C):
    health: Annotated[float, FloatProperty(), SerializedName('Health')]
    default_health: Annotated[float, FloatProperty(), SerializedName('DefaultHealth')]
    blood_type: Annotated[int, ByteProperty(), SerializedName('BloodType')]
    show_value: Annotated[bool, BoolProperty(), SerializedName('ShowValue')]
    text_offset: Annotated[Vector, StructProperty(Vector), SerializedName('TextOffset')]
    hit_fx: Annotated[bool, BoolProperty(), SerializedName('HitFX')]

@suitebro_dataclass
class KeyPad_C(InventoryItem):
    attached_lock: Annotated[Guid, StructProperty(Guid), SerializedName('AttachedLock')]
    passcode: Annotated[str, StrProperty(), SerializedName('Passcode')]
    incognito: Annotated[bool, BoolProperty(), SerializedName('Incognito')]

@suitebro_dataclass
class KeycardsPhysics_C(BasePhysicsItem_C):
    mesh_choice: Annotated[int, IntProperty(), SerializedName('MeshChoice')]

@suitebro_dataclass
class LadderRung_C(BaseLadderItem_C):
    material: Annotated[bool, BoolProperty(), SerializedName('Material')]

@suitebro_dataclass
class LaserBeam_C(BaseTargetable_C):
    color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('Color')]
    width: Annotated[float, FloatProperty(), SerializedName('Width')]
    deal_damage: Annotated[bool, BoolProperty(), SerializedName('DealDamage')]
    damage_amount: Annotated[float, FloatProperty(), SerializedName('DamageAmount')]
    filter_players: Annotated[bool, BoolProperty(), SerializedName('FilterPlayers')]
    filter_physics: Annotated[bool, BoolProperty(), SerializedName('FilterPhysics')]
    stop_laser_on_hit_location: Annotated[bool, BoolProperty(), SerializedName('StopLaserOnHitLocation')]

@suitebro_dataclass
class LaserProjector_C(InventoryItem):
    base_angle: Annotated[float, FloatProperty(), SerializedName('BaseAngle')]
    laser_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('LaserColor')]
    time_offset: Annotated[float, FloatProperty(), SerializedName('TimeOffset')]
    fov: Annotated[float, FloatProperty(), SerializedName('FOV')]
    pattern_sequence: Annotated[list[bool], ArrayProperty('PatternSequence', BoolProperty()), SerializedName('PatternSequence')]
    pattern_interval: Annotated[float, FloatProperty(), SerializedName('PatternInterval')]
    enable_sequence: Annotated[bool, BoolProperty(), SerializedName('EnableSequence')]
    rotation: Annotated[float, FloatProperty(), SerializedName('Rotation')]
    rotation_should_animate: Annotated[bool, BoolProperty(), SerializedName('RotationShouldAnimate')]
    size_x: Annotated[float, FloatProperty(), SerializedName('SizeX')]
    size_x_should_animate: Annotated[bool, BoolProperty(), SerializedName('SizeXShouldAnimate')]
    size_y: Annotated[float, FloatProperty(), SerializedName('SizeY')]
    size_y_should_animate: Annotated[bool, BoolProperty(), SerializedName('SizeYShouldAnimate')]
    is_on: Annotated[bool, BoolProperty(), SerializedName('IsOn')]
    beam_opacity: Annotated[float, FloatProperty(), SerializedName('BeamOpacity')]
    laser_expressions: Annotated[list[LaserExpressionPreset], ArrayProperty('LaserExpressions', StructProperty(LaserExpressionPreset)), SerializedName('LaserExpressions')]
    sequence: Annotated[list[LaserProjectionIndex], ArrayProperty('Sequence', StructProperty(LaserProjectionIndex)), SerializedName('Sequence')]
    active_laser_projection: Annotated[LaserProjectionIndex, StructProperty(LaserProjectionIndex), SerializedName('ActiveLaserProjection')]
    laser_pattern: Annotated[UEnum, EnumProperty(), SerializedName('LaserPattern')]
    render_distance: Annotated[float, FloatProperty(), SerializedName('RenderDistance')]
    projection_radius: Annotated[float, FloatProperty(), SerializedName('ProjectionRadius')]
    base_visible: Annotated[bool, BoolProperty(), SerializedName('BaseVisible')]

@suitebro_dataclass
class LibretroArcade_C(BaseLibretro_C):
    url: Annotated[str, StrProperty(), SerializedName('URL')]
    additional_urls: Annotated[list[str], ArrayProperty('AdditionalURLs', StrProperty()), SerializedName('AdditionalURLs')]
    animation_mode: Annotated[bool, BoolProperty(), SerializedName('AnimationMode')]
    animation_columns: Annotated[int, IntProperty(), SerializedName('AnimationColumns')]
    animation_rows: Annotated[int, IntProperty(), SerializedName('AnimationRows')]
    animation_rate: Annotated[float, FloatProperty(), SerializedName('AnimationRate')]
    game_name_artwork_searched: Annotated[str, StrProperty(), SerializedName('GameNameArtworkSearched')]
    control_style: Annotated[str, StrProperty(), SerializedName('ControlStyle')]

@suitebro_dataclass
class LibretroArcadeGun_C(LibretroArcade_C):
    lightgun_style: Annotated[int, IntProperty(), SerializedName('LightgunStyle')]

@suitebro_dataclass
class LibretroArcadeRetroCap1_C(LibretroArcade_C):
    type: Annotated[int, IntProperty(), SerializedName('Type')]

@suitebro_dataclass
class LibretroArcadeRetroCap4_C(LibretroArcade_C):
    type: Annotated[int, IntProperty(), SerializedName('Type')]

@suitebro_dataclass
class LibretroArcadeRetroGlass_C(LibretroArcade_C):
    square_mode: Annotated[bool, BoolProperty(), SerializedName('SquareMode')]

@suitebro_dataclass
class LibretroArcadeTableTop_C(LibretroArcade_C):
    square_ratio: Annotated[bool, BoolProperty(), SerializedName('SquareRatio')]

@suitebro_dataclass
class LibretroComputer_C(BaseLibretro_C):
    keyboard_override: Annotated[bool, BoolProperty(), SerializedName('KeyboardOverride')]

@suitebro_dataclass
class LibretroComputerAquaModern_C(LibretroComputer_C):
    tower: Annotated[bool, BoolProperty(), SerializedName('Tower')]

@suitebro_dataclass
class LibretroConsole_C(BaseLibretro_C):
    controller_override: Annotated[bool, BoolProperty(), SerializedName('ControllerOverride')]

@suitebro_dataclass
class LibretroConsoleWaveScape_C(LibretroConsole_C):
    lid_closed: Annotated[bool, BoolProperty(), SerializedName('LidClosed')]

@suitebro_dataclass
class LightPanelStand_C(BaseLamp_C):
    height: Annotated[float, FloatProperty(), SerializedName('Height')]
    pan: Annotated[float, FloatProperty(), SerializedName('Pan')]
    tilt: Annotated[float, FloatProperty(), SerializedName('Tilt')]

@suitebro_dataclass
class LightPanel_C(BaseLamp_C):
    tilt: Annotated[float, FloatProperty(), SerializedName('Tilt')]

@suitebro_dataclass
class LocationVolumeIO_C(BaseVolume_C):
    location_info: Annotated[LocationInfo, StructProperty(LocationInfo), SerializedName('LocationInfo')]
    location_rules: Annotated[LocationRules, StructProperty(LocationRules), SerializedName('LocationRules')]
    priority: Annotated[int, IntProperty(), SerializedName('Priority')]

@suitebro_dataclass
class MicrophoneStand_C(BaseColorable_C):
    height: Annotated[float, FloatProperty(), SerializedName('Height')]
    tilt: Annotated[float, FloatProperty(), SerializedName('Tilt')]

@suitebro_dataclass
class MiniatureFerrisWheel_C(InventoryItem):
    active_season: Annotated[UEnum, EnumProperty(), SerializedName('ActiveSeason')]

@suitebro_dataclass
class ModernTelescope_C(BaseColorable_C):
    swivel: Annotated[float, FloatProperty(), SerializedName('Swivel')]
    tilt: Annotated[float, FloatProperty(), SerializedName('Tilt')]

@suitebro_dataclass
class Mover_C(IOModuleBase_C):
    original_transform: Annotated[Transform, StructProperty(Transform), SerializedName('OriginalTransform')]
    ease_movement: Annotated[bool, BoolProperty(), SerializedName('EaseMovement')]
    time_before_reverse: Annotated[float, FloatProperty(), SerializedName('TimeBeforeReverse')]
    looping_type: Annotated[int, ByteProperty(), SerializedName('LoopingType')]
    duration: Annotated[float, FloatProperty(), SerializedName('Duration')]
    auto_start: Annotated[bool, BoolProperty(), SerializedName('AutoStart')]
    move_to: Annotated[Vector, StructProperty(Vector), SerializedName('MoveTo')]
    rotation_type: Annotated[int, ByteProperty(), SerializedName('RotationType')]
    rotate_to: Annotated[Rotator, StructProperty(Rotator), SerializedName('RotateTo')]
    rotation_rate: Annotated[float, FloatProperty(), SerializedName('RotationRate')]
    closed_loop: Annotated[bool, BoolProperty(), SerializedName('ClosedLoop')]
    offset_location: Annotated[Vector, StructProperty(Vector), SerializedName('OffsetLocation')]
    offset_rotation: Annotated[Rotator, StructProperty(Rotator), SerializedName('OffsetRotation')]
    item_to_look_at: Annotated[str, StrProperty(), SerializedName('ItemToLookAt')]
    spin_reversed: Annotated[bool, BoolProperty(), SerializedName('SpinReversed')]
    spin_axis: Annotated[Vector, StructProperty(Vector), SerializedName('SpinAxis')]
    actor_guid: Annotated[Guid, StructProperty(Guid), SerializedName('ActorGuid')]
    overlaps: Annotated[bool, BoolProperty(), SerializedName('Overlaps')]
    rotate_from: Annotated[Rotator, StructProperty(Rotator), SerializedName('RotateFrom')]
    reverse_rate: Annotated[float, FloatProperty(), SerializedName('ReverseRate')]
    start_delay: Annotated[float, FloatProperty(), SerializedName('StartDelay')]
    start_spin_on_start: Annotated[bool, BoolProperty(), SerializedName('StartSpinOnStart')]

@suitebro_dataclass
class MoverAdvanced_C(Mover_C):
    spline_data: Annotated[list[SplineSaveData], ArrayProperty('SplineData', StructProperty(SplineSaveData)), SerializedName('SplineData')]

@suitebro_dataclass
class MoverPlayerSlide_C(Mover_C):
    spline_data: Annotated[list[SplineSaveData], ArrayProperty('SplineData', StructProperty(SplineSaveData)), SerializedName('SplineData')]
    use_pool_tube: Annotated[bool, BoolProperty(), SerializedName('UsePoolTube')]
    show_slide: Annotated[bool, BoolProperty(), SerializedName('ShowSlide')]
    show_splashes: Annotated[bool, BoolProperty(), SerializedName('ShowSplashes')]

@suitebro_dataclass
class MoverTrain_C(Mover_C):
    spline_data: Annotated[list[SplineSaveData], ArrayProperty('SplineData', StructProperty(SplineSaveData)), SerializedName('SplineData')]
    cart_type: Annotated[int, ByteProperty(), SerializedName('CartType')]
    cart_num: Annotated[int, IntProperty(), SerializedName('CartNum')]
    cart_spacing: Annotated[float, FloatProperty(), SerializedName('CartSpacing')]
    cart_length: Annotated[float, FloatProperty(), SerializedName('CartLength')]
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    station_wait_time: Annotated[float, FloatProperty(), SerializedName('StationWaitTime')]
    track_type: Annotated[int, ByteProperty(), SerializedName('TrackType')]

@suitebro_dataclass
class NPCAI_C(IOModuleBase_C):
    current_model: Annotated[int, ByteProperty(), SerializedName('CurrentModel')]
    character_name: Annotated[str, StrProperty(), SerializedName('CharacterName')]
    alliance: Annotated[int, ByteProperty(), SerializedName('Alliance')]
    workshop_model: Annotated[WorkshopFile, StructProperty(WorkshopFile), SerializedName('WorkshopModel')]
    health: Annotated[float, FloatProperty(), SerializedName('Health')]
    attack_damage: Annotated[float, FloatProperty(), SerializedName('AttackDamage')]
    default_state: Annotated[int, ByteProperty(), SerializedName('DefaultState')]
    max_search_distance: Annotated[float, FloatProperty(), SerializedName('MaxSearchDistance')]
    type: Annotated[int, ByteProperty(), SerializedName('Type')]
    walk_speed: Annotated[float, FloatProperty(), SerializedName('WalkSpeed')]

@suitebro_dataclass
class NPCSpawner_C(IOModuleBase_C):
    actor_limit: Annotated[int, IntProperty(), SerializedName('ActorLimit')]
    radius: Annotated[float, FloatProperty(), SerializedName('Radius')]
    template: Annotated[str, StrProperty(), SerializedName('Template')]

@suitebro_dataclass
class NPC_C(InventoryItem):
    font: Annotated[int, ByteProperty(), SerializedName('Font')]
    show_name_tag: Annotated[bool, BoolProperty(), SerializedName('ShowNameTag')]
    show_model: Annotated[bool, BoolProperty(), SerializedName('ShowModel')]
    current_model: Annotated[int, ByteProperty(), SerializedName('CurrentModel')]
    current_idle: Annotated[int, ByteProperty(), SerializedName('CurrentIdle')]
    current_wearables: Annotated[NPCWearables, StructProperty(NPCWearables), SerializedName('CurrentWearables')]
    camera_offset: Annotated[Vector, StructProperty(Vector), SerializedName('CameraOffset')]
    name: Annotated[str, StrProperty(), SerializedName('Name')]
    avatar_url: Annotated[str, StrProperty(), SerializedName('AvatarURL')]
    on_enter: Annotated[list[str], ArrayProperty('OnEnter', TextProperty()), SerializedName('OnEnter')]
    on_leave: Annotated[list[str], ArrayProperty('OnLeave', TextProperty()), SerializedName('OnLeave')]
    on_talk: Annotated[list[str], ArrayProperty('OnTalk', TextProperty()), SerializedName('OnTalk')]
    name_offset: Annotated[Vector, StructProperty(Vector), SerializedName('NameOffset')]
    prompt: Annotated[str, StrProperty(), SerializedName('Prompt')]
    look_at: Annotated[bool, BoolProperty(), SerializedName('LookAt')]
    workshop_model: Annotated[WorkshopFile, StructProperty(WorkshopFile), SerializedName('WorkshopModel')]

@suitebro_dataclass
class NewtonsCradle_C(InventoryItem):
    is_on: Annotated[bool, BoolProperty(), SerializedName('IsOn')]

@suitebro_dataclass
class NightclubMediaPlayerItem_C(NightclubMediaPlayer_C):
    bpm: Annotated[int, IntProperty(), SerializedName('BPM')]

@suitebro_dataclass
class NightclubSpotlight_C(BaseLamp_C):
    movement_mode: Annotated[Name, NameProperty(), SerializedName('MovementMode')]
    desired_rotation: Annotated[float, FloatProperty(), SerializedName('DesiredRotation')]
    desired_pitch: Annotated[float, FloatProperty(), SerializedName('DesiredPitch')]
    random_delay: Annotated[float, FloatProperty(), SerializedName('RandomDelay')]

@suitebro_dataclass
class NumberSignGlow_C(BaseColorable_C):
    number_input: Annotated[int, IntProperty(), SerializedName('NumberInput')]

@suitebro_dataclass
class NumberSign_C(BaseColorable_C):
    number_input: Annotated[int, IntProperty(), SerializedName('NumberInput')]

@suitebro_dataclass
class OfficeSwivelChair_C(BaseSeatColorable_C):
    height: Annotated[float, FloatProperty(), SerializedName('Height')]
    angle: Annotated[float, FloatProperty(), SerializedName('Angle')]

@suitebro_dataclass
class PaverGardenLiner_C(BaseColorable_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class PaverGardenTile_C(BaseColorable_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class PaverSteppingStoneCluster_C(BaseColorable_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class PaverSteppingStoneSingle_C(BaseColorable_C):
    active_index: Annotated[int, IntProperty(), SerializedName('ActiveIndex')]

@suitebro_dataclass
class PhysicalMediaShelf_C(InventoryItem):
    spacer_multiplier: Annotated[float, FloatProperty(), SerializedName('SpacerMultiplier')]
    rotation: Annotated[float, FloatProperty(), SerializedName('Rotation')]
    shelf_data: Annotated[list[PhysicalMediaShelfData], ArrayProperty('ShelfData', StructProperty(PhysicalMediaShelfData)), SerializedName('ShelfData')]

@suitebro_dataclass
class PhysicsSlot_C(BaseColorable_C):
    auto_eject: Annotated[bool, BoolProperty(), SerializedName('AutoEject')]
    name_match: Annotated[str, StrProperty(), SerializedName('NameMatch')]
    base_visibility: Annotated[bool, BoolProperty(), SerializedName('BaseVisibility')]

@suitebro_dataclass
class BatterySlot_C(PhysicsSlot_C):
    mute_sfx: Annotated[bool, BoolProperty(), SerializedName('MuteSFX')]

@suitebro_dataclass
class KeycardSlot_C(PhysicsSlot_C):
    mesh_choice: Annotated[int, IntProperty(), SerializedName('MeshChoice')]
    mute_sfx: Annotated[bool, BoolProperty(), SerializedName('MuteSFX')]

@suitebro_dataclass
class PileOfUnits_C(BaseItemCurrency_C):
    has_glow: Annotated[bool, BoolProperty(), SerializedName('HasGlow')]

@suitebro_dataclass
class PlaceableLight_C(BaseLamp_C):
    fill_light: Annotated[bool, BoolProperty(), SerializedName('FillLight')]

@suitebro_dataclass
class PlayerCannon_C(BaseTargetable_C):
    launch_speed: Annotated[float, FloatProperty(), SerializedName('Launch Speed')]
    show_trajectory: Annotated[bool, BoolProperty(), SerializedName('ShowTrajectory')]
    lock_player_on_launch: Annotated[bool, BoolProperty(), SerializedName('LockPlayerOnLaunch')]

@suitebro_dataclass
class PlayerInputVolume_C(BaseVolume_C):
    prompt: Annotated[str, StrProperty(), SerializedName('Prompt')]
    camera_offset: Annotated[Vector, StructProperty(Vector), SerializedName('CameraOffset')]
    camera_rotation: Annotated[Rotator, StructProperty(Rotator), SerializedName('CameraRotation')]
    camera_enabled: Annotated[bool, BoolProperty(), SerializedName('CameraEnabled')]

@suitebro_dataclass
class PlayerMovementVolume_C(BaseVolume_C):
    walk_speed: Annotated[float, FloatProperty(), SerializedName('WalkSpeed')]
    sprint_multiplier: Annotated[float, FloatProperty(), SerializedName('SprintMultiplier')]
    walk_multiplier: Annotated[float, FloatProperty(), SerializedName('WalkMultiplier')]
    jump_amount: Annotated[float, FloatProperty(), SerializedName('JumpAmount')]
    allow_jump: Annotated[bool, BoolProperty(), SerializedName('AllowJump')]
    allow_crouch: Annotated[bool, BoolProperty(), SerializedName('AllowCrouch')]
    allow_sprint: Annotated[bool, BoolProperty(), SerializedName('AllowSprint')]
    preset: Annotated[Name, NameProperty(), SerializedName('Preset')]
    allow_suicide: Annotated[bool, BoolProperty(), SerializedName('AllowSuicide')]

@suitebro_dataclass
class PlazaMusicEmitter_C(InventoryItem):
    selected_sound: Annotated[int, IntProperty(), SerializedName('SelectedSound')]
    play_interval_min: Annotated[float, FloatProperty(), SerializedName('PlayIntervalMin')]
    play_interval_max: Annotated[float, FloatProperty(), SerializedName('PlayIntervalMax')]
    pitch_min: Annotated[float, FloatProperty(), SerializedName('PitchMin')]
    pitch_max: Annotated[float, FloatProperty(), SerializedName('PitchMax')]
    range: Annotated[float, FloatProperty(), SerializedName('Range')]
    volume_min: Annotated[float, FloatProperty(), SerializedName('VolumeMin')]
    volume_max: Annotated[float, FloatProperty(), SerializedName('VolumeMax')]

@suitebro_dataclass
class PostProcessVolume_C(BaseVolume_C):
    priority: Annotated[float, FloatProperty(), SerializedName('Priority')]
    unbound: Annotated[bool, BoolProperty(), SerializedName('Unbound')]
    blend_radius: Annotated[float, FloatProperty(), SerializedName('BlendRadius')]
    blend_weight: Annotated[float, FloatProperty(), SerializedName('BlendWeight')]
    post_process_settings: Annotated[PostProcessVolumeSettings, StructProperty(PostProcessVolumeSettings), SerializedName('PostProcessSettings')]

@suitebro_dataclass
class PotionBottles_C(BaseMultiMesh_C):
    amount: Annotated[float, FloatProperty(), SerializedName('Amount')]
    enable: Annotated[bool, BoolProperty(), SerializedName('Enable')]

@suitebro_dataclass
class PropCrate_C(BaseColorable_C):
    tarp: Annotated[bool, BoolProperty(), SerializedName('Tarp')]

@suitebro_dataclass
class PushVolume_C(BaseVolume_C):
    direction: Annotated[Rotator, StructProperty(Rotator), SerializedName('Direction')]
    force: Annotated[float, FloatProperty(), SerializedName('Force')]

@suitebro_dataclass
class Random_C(IOModuleBase_C):
    max_int: Annotated[int, IntProperty(), SerializedName('MaxInt')]
    no_repeat: Annotated[bool, BoolProperty(), SerializedName('NoRepeat')]

@suitebro_dataclass
class Relay_C(IOModuleBase_C):
    fired: Annotated[bool, BoolProperty(), SerializedName('Fired')]
    fire_once: Annotated[bool, BoolProperty(), SerializedName('FireOnce')]

@suitebro_dataclass
class RemainsDecoration_C(BaseColorable_C):
    remains: Annotated[int, IntProperty(), SerializedName('Remains')]
    particles: Annotated[bool, BoolProperty(), SerializedName('Particles')]

@suitebro_dataclass
class RideSeat_C(BaseSeatColorable_C):
    has_safety_bars: Annotated[bool, BoolProperty(), SerializedName('HasSafetyBars')]
    has_base: Annotated[bool, BoolProperty(), SerializedName('HasBase')]

@suitebro_dataclass
class SacrificialStone_C(BaseBed_C):
    disable_interact: Annotated[bool, BoolProperty(), SerializedName('DisableInteract')]

@suitebro_dataclass
class SeatVolume_C(BaseSeat_C):
    pose: Annotated[Name, NameProperty(), SerializedName('Pose')]

@suitebro_dataclass
class SecurityCamera_C(BaseDrivable_C):
    automatic_movement: Annotated[bool, BoolProperty(), SerializedName('AutomaticMovement')]
    angle: Annotated[float, FloatProperty(), SerializedName('Angle')]

@suitebro_dataclass
class SignChalkboardStand_C(BaseSign_C):
    position: Annotated[float, FloatProperty(), SerializedName('Position')]

@suitebro_dataclass
class SizeVolume_C(BaseVolume_C):
    size: Annotated[float, FloatProperty(), SerializedName('Size')]

@suitebro_dataclass
class SkeletonPosed_Leaning_C(BaseMultiMesh_C):
    messy_skele: Annotated[int, IntProperty(), SerializedName('MessySkele')]

@suitebro_dataclass
class SkeletonPosed_Lying_C(BaseMultiMesh_C):
    messy_skele: Annotated[int, IntProperty(), SerializedName('MessySkele')]

@suitebro_dataclass
class SkeletonPosed_Sexy_C(BaseMultiMesh_C):
    messy_skele: Annotated[int, IntProperty(), SerializedName('MessySkele')]

@suitebro_dataclass
class SkeletonPosed_Shackled_C(BaseMultiMesh_C):
    messy_skele: Annotated[int, IntProperty(), SerializedName('MessySkele')]

@suitebro_dataclass
class Skeleton_BonePile_C(BaseMultiMesh_C):
    messy_skele: Annotated[int, IntProperty(), SerializedName('MessySkele')]

@suitebro_dataclass
class Skeleton_Bone_C(BaseMultiMesh_C):
    messy_skele: Annotated[int, IntProperty(), SerializedName('MessySkele')]

@suitebro_dataclass
class SkyProcessVolume_C(BaseVolume_C):
    unbound: Annotated[bool, BoolProperty(), SerializedName('Unbound')]
    fog_enabled: Annotated[bool, BoolProperty(), SerializedName('FogEnabled')]
    fog_volume_settings: Annotated[FogVolumeSettings, StructProperty(FogVolumeSettings), SerializedName('FogVolumeSettings')]
    sky_volume_settings: Annotated[SkyVolumeSettings, StructProperty(SkyVolumeSettings), SerializedName('SkyVolumeSettings')]
    priority: Annotated[int, IntProperty(), SerializedName('Priority')]

@suitebro_dataclass
class SnowGlobe_C(BaseColorable_C):
    decorations_visibility: Annotated[bool, BoolProperty(), SerializedName('Decorations_Visibility')]

@suitebro_dataclass
class SpawnPointTagVolume_C(BaseVolume_C):
    tag: Annotated[Name, NameProperty(), SerializedName('Tag')]

@suitebro_dataclass
class SpikeBoard_C(BaseColorable_C):
    base: Annotated[bool, BoolProperty(), SerializedName('Base')]
    style: Annotated[bool, BoolProperty(), SerializedName('Style')]
    damage_amount: Annotated[float, FloatProperty(), SerializedName('DamageAmount')]

@suitebro_dataclass
class SpiritBored_C(BaseColorable_C):
    question_prompt: Annotated[str, StrProperty(), SerializedName('QuestionPrompt')]
    answer: Annotated[str, StrProperty(), SerializedName('Answer')]

@suitebro_dataclass
class SpiralStairs1_C(Stairs_C):
    invert: Annotated[bool, BoolProperty(), SerializedName('Invert')]

@suitebro_dataclass
class CondoEditableStaticMesh_C(StaticMeshActor):
    visible: Annotated[bool, BoolProperty(), SerializedName('Visible')]

@suitebro_dataclass
class CondoEditableSurface_C(StaticMeshActor):
    surface_colorable: Annotated[Colorable, StructProperty(Colorable), SerializedName('SurfaceColorable')]
    surface_material: Annotated[Object, ObjectProperty('MaterialInterface'), SerializedName('SurfaceMaterial')]
    canvas_url: Annotated[str, StrProperty(), SerializedName('CanvasURL')]
    tiling: Annotated[Vector, StructProperty(Vector), SerializedName('Tiling')]
    world_align_canvas: Annotated[bool, BoolProperty(), SerializedName('WorldAlignCanvas')]

@suitebro_dataclass
class CondoEditableSurfaceTogglable_C(CondoEditableSurface_C):
    visible: Annotated[bool, BoolProperty(), SerializedName('Visible')]

@suitebro_dataclass
class PoolCover_C(CondoEditableSurface_C):
    opened: Annotated[bool, BoolProperty(), SerializedName('Opened')]

@suitebro_dataclass
class SlidingCondoRoof_C(CondoEditableSurface_C):
    opened: Annotated[bool, BoolProperty(), SerializedName('Opened')]

@suitebro_dataclass
class HighRise_ToggleHide_C(StaticMeshActor):
    is_hidden: Annotated[bool, BoolProperty(), SerializedName('IsHidden')]

@suitebro_dataclass
class StoneFountainBar_C(BaseColorable_C):
    active: Annotated[bool, BoolProperty(), SerializedName('Active')]

@suitebro_dataclass
class TableClothRound_C(BaseCanvasMultiMesh_C):
    frame_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('FrameColor')]
    ghost_cloth: Annotated[bool, BoolProperty(), SerializedName('GhostCloth')]

@suitebro_dataclass
class TablePlasticGarden_C(BaseColorable_C):
    un_gunked: Annotated[bool, BoolProperty(), SerializedName('UnGunked')]

@suitebro_dataclass
class Teleporter_C(BaseTargetable_C):
    colour: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('Colour')]
    ask_permission: Annotated[bool, BoolProperty(), SerializedName('AskPermission')]
    keep_velocity: Annotated[bool, BoolProperty(), SerializedName('KeepVelocity')]
    prompt: Annotated[str, StrProperty(), SerializedName('Prompt')]
    absolute_rotation: Annotated[bool, BoolProperty(), SerializedName('AbsoluteRotation')]
    visible: Annotated[bool, BoolProperty(), SerializedName('Visible')]
    relative_teleport: Annotated[bool, BoolProperty(), SerializedName('RelativeTeleport')]

@suitebro_dataclass
class CanvasTeleporter_C(Teleporter_C):
    url: Annotated[str, StrProperty(), SerializedName('URL')]
    emissive: Annotated[float, FloatProperty(), SerializedName('Emissive')]
    canvas_shape: Annotated[int, ByteProperty(), SerializedName('CanvasShape')]
    type: Annotated[int, ByteProperty(), SerializedName('Type')]
    animation_rate: Annotated[float, FloatProperty(), SerializedName('AnimationRate')]
    animation_rows: Annotated[int, IntProperty(), SerializedName('AnimationRows')]
    animation_columns: Annotated[int, IntProperty(), SerializedName('AnimationColumns')]
    animation_mode: Annotated[bool, BoolProperty(), SerializedName('AnimationMode')]

@suitebro_dataclass
class TeleportVolume_C(Teleporter_C):
    filter_players: Annotated[bool, BoolProperty(), SerializedName('FilterPlayers')]
    filter_physics: Annotated[bool, BoolProperty(), SerializedName('FilterPhysics')]

@suitebro_dataclass
class Text3D_C(FloatingTextSign_C):
    material_override: Annotated[int, IntProperty(), SerializedName('MaterialOverride')]

@suitebro_dataclass
class Timer_C(IOModuleBase_C):
    min_duration: Annotated[float, FloatProperty(), SerializedName('MinDuration')]
    max_duration: Annotated[float, FloatProperty(), SerializedName('MaxDuration')]
    looping: Annotated[bool, BoolProperty(), SerializedName('Looping')]
    randomize_duration: Annotated[bool, BoolProperty(), SerializedName('RandomizeDuration')]
    show_value: Annotated[bool, BoolProperty(), SerializedName('ShowValue')]
    start_on_spawn: Annotated[bool, BoolProperty(), SerializedName('StartOnSpawn')]

@suitebro_dataclass
class ToiletPaperHolder_C(BaseColorable_C):
    inwards: Annotated[bool, BoolProperty(), SerializedName('Inwards')]
    tp: Annotated[bool, BoolProperty(), SerializedName('TP')]

@suitebro_dataclass
class ToolPaintRoller_C(BaseColorable_C):
    dirty: Annotated[bool, BoolProperty(), SerializedName('Dirty')]

@suitebro_dataclass
class ToolPaintTray_C(BaseColorable_C):
    dirty: Annotated[bool, BoolProperty(), SerializedName('Dirty')]

@suitebro_dataclass
class Trampoline_C(BaseColorable_C):
    power_multiplier: Annotated[float, FloatProperty(), SerializedName('PowerMultiplier')]
    scale_power: Annotated[bool, BoolProperty(), SerializedName('ScalePower')]

@suitebro_dataclass
class TransdimensialPainting_C(Teleporter_C):
    has_frame: Annotated[bool, BoolProperty(), SerializedName('HasFrame')]

@suitebro_dataclass
class TreasureChestOUnits_C(BaseItemCurrency_C):
    has_glow: Annotated[bool, BoolProperty(), SerializedName('HasGlow')]

@suitebro_dataclass
class TriggerVolume_C(BaseVolume_C):
    trigger_once: Annotated[bool, BoolProperty(), SerializedName('TriggerOnce')]
    players_required: Annotated[int, IntProperty(), SerializedName('PlayersRequired')]

@suitebro_dataclass
class Ultra_Dynamic_Sky_BP_C(BaseTimeCycler):
    moon_inclination: Annotated[float, FloatProperty(), SerializedName('Moon Inclination')]
    moonlight_intensity: Annotated[float, FloatProperty(), SerializedName('Moonlight Intensity')]
    sun_inclination: Annotated[float, FloatProperty(), SerializedName('Sun Inclination')]
    should_animate_day_night: Annotated[bool, BoolProperty(), SerializedName('ShouldAnimateDayNight')]
    time_of_day_setpoint: Annotated[float, FloatProperty(), SerializedName('TimeOfDaySetpoint')]

@suitebro_dataclass
class WaterCooler_C(BaseColorable_C):
    bottle_bool: Annotated[bool, BoolProperty(), SerializedName('BottleBool')]

@suitebro_dataclass
class WaterVolume_C(BaseVolume_C):
    water_type: Annotated[int, IntProperty(), SerializedName('WaterType')]
    water_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('WaterColor')]
    water_color_shallow: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('WaterColorShallow')]
    friction: Annotated[float, FloatProperty(), SerializedName('Friction')]
    underwater_color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('UnderwaterColor')]
    top_only: Annotated[bool, BoolProperty(), SerializedName('TopOnly')]

@suitebro_dataclass
class WeaponPickup_C(InventoryItem):
    type: Annotated[int, ByteProperty(), SerializedName('Type')]

@suitebro_dataclass
class WeaponPickupIO_C(WeaponPickup_C):
    item_id: Annotated[int, IntProperty(), SerializedName('ItemID')]
    has_stand: Annotated[bool, BoolProperty(), SerializedName('HasStand')]
    has_glow: Annotated[bool, BoolProperty(), SerializedName('HasGlow')]
    do_pickup_effects: Annotated[bool, BoolProperty(), SerializedName('DoPickupEffects')]

@suitebro_dataclass
class Windtower_C(BaseColorable_C):
    active: Annotated[bool, BoolProperty(), SerializedName('Active')]
    speed: Annotated[int, IntProperty(), SerializedName('Speed')]
    angle: Annotated[float, FloatProperty(), SerializedName('Angle')]

@suitebro_dataclass
class WinterMarketStall_C(BaseColorable_C):
    snow_job: Annotated[bool, BoolProperty(), SerializedName('SnowJob')]

@suitebro_dataclass
class WorkshopCharacterLoaderComponent_C(ActorComponent):
    active_workshop_model: Annotated[WorkshopFile, StructProperty(WorkshopFile), SerializedName('ActiveWorkshopModel')]

@suitebro_dataclass
class WorkshopStaticMeshLoaderComponent_C(ActorComponent):
    workshop_file: Annotated[WorkshopFile, StructProperty(WorkshopFile), SerializedName('WorkshopFile')]

@suitebro_dataclass
class XmasLights_ArchCandy_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_ArchCircle_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_ArchReindeer_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]
    animated: Annotated[bool, BoolProperty(), SerializedName('Animated')]
    animation_on: Annotated[float, FloatProperty(), SerializedName('AnimationOn')]

@suitebro_dataclass
class XmasLights_ArchTunnel_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_Candle_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_CandyCanes_C(BaseMultiMesh_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_JackFrost_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]
    animated: Annotated[bool, BoolProperty(), SerializedName('Animated')]
    animation_on: Annotated[float, FloatProperty(), SerializedName('AnimationOn')]

@suitebro_dataclass
class XmasLights_Lollipops_C(BaseMultiMesh_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_Moose_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]

@suitebro_dataclass
class XmasLights_Reindeer_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]
    animated: Annotated[bool, BoolProperty(), SerializedName('Animated')]

@suitebro_dataclass
class XmasLights_Santa_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]
    animated: Annotated[bool, BoolProperty(), SerializedName('Animated')]
    animation_on: Annotated[float, FloatProperty(), SerializedName('AnimationOn')]

@suitebro_dataclass
class XmasLights_Snowman_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]
    animated: Annotated[bool, BoolProperty(), SerializedName('Animated')]
    animation_on: Annotated[float, FloatProperty(), SerializedName('AnimationOn')]

@suitebro_dataclass
class XmasLights_Tree_C(BaseColorable_C):
    speed: Annotated[float, FloatProperty(), SerializedName('Speed')]
    power: Annotated[float, FloatProperty(), SerializedName('Power')]
