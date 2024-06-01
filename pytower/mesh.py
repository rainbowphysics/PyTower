import json
import sys
from typing import Any
import uuid

import open3d as o3d
import numpy as np

from scipy.spatial.transform import Rotation as R

from .object import TowerObject
from .suitebro import Suitebro
from .util import xyz, XYZ

WEDGE_ITEM_DATA: dict[str, Any] = {
    "name": "CanvasWedge",
    "guid": "",
    "format_version": 1,
    "unreal_version": 517,
    "steam_item_id": 0,
    "properties": {
        "OwningSteamID": {
            "Struct": {
                "value": {
                    "Struct": {}
                },
                "struct_type": {
                    "Struct": "SteamID"
                },
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        }
    },
    "actors": [],
    "rotation": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "w": 1.0
    },
    "position": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    },
    "scale": {
        "x": 1.0,
        "y": 1.0,
        "z": 1.0
    }
}

WEDGE_PROPERTY_DATA: dict[str, Any] = {
    "name": "CanvasWedge_C_2",
    "properties": {
        "SlopeOverride": {
            "Bool": {
                "value": False
            }
        },
        "URL": {
            "Str": {
                "value": ""
            }
        },
        "Scale": {
            "Float": {
                "value": 0.0
            }
        },
        "Type": {
            "Byte": {
                "value": {
                    "Label": "CanvasTypes::NewEnumerator0"
                },
                "enum_type": "CanvasTypes"
            }
        },
        "CanvasShape": {
            "Byte": {
                "value": {
                    "Label": "CanvasShapes::NewEnumerator0"
                },
                "enum_type": "CanvasShapes"
            }
        },
        "Emissive": {
            "Float": {
                "value": 0.0
            }
        },
        "ScaleX": {
            "Float": {
                "value": 1.0
            }
        },
        "ScaleY": {
            "Float": {
                "value": 1.0
            }
        },
        "ScaleZ": {
            "Float": {
                "value": 1.0
            }
        },
        "WorldScale": {
            "Struct": {
                "value": {
                    "Vector": {
                        "x": 1.0,
                        "y": 1.0,
                        "z": 1.0
                    }
                },
                "struct_type": "Vector",
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "Tiling": {
            "Struct": {
                "value": {
                    "Vector": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 1.0
                    }
                },
                "struct_type": "Vector",
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "CacheToDisk": {
            "Bool": {
                "value": True
            }
        },
        "AdditionalURLs": {
            "Array": {
                "array_type": "StrProperty",
                "value": {
                    "Base": {
                        "Str": []
                    }
                }
            }
        },
        "SurfaceMaterial": {
            "Object": {
                "value": "None"
            }
        },
        "SurfaceColorable": {
            "Struct": {
                "value": {
                    "Struct": {
                        "Color": {
                            "Struct": {
                                "value": {
                                    "LinearColor": {
                                        "r": 1.0,
                                        "g": 1.0,
                                        "b": 1.0,
                                        "a": 1.0
                                    }
                                },
                                "struct_type": "LinearColor",
                                "struct_id": "00000000-0000-0000-0000-000000000000"
                            }
                        },
                        "DynamicMaterialIndex": {
                            "Int": {
                                "value": 0
                            }
                        }
                    }
                },
                "struct_type": {
                    "Struct": "Colorable"
                },
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "AnimationMode": {
            "Bool": {
                "value": False
            }
        },
        "AnimationColumns": {
            "Int": {
                "value": 5
            }
        },
        "AnimationRows": {
            "Int": {
                "value": 5
            }
        },
        "AnimationRate": {
            "Float": {
                "value": 1.0
            }
        },
        "WorldAlignCanvas": {
            "Bool": {
                "value": False
            }
        },
        "NSFW": {
            "Bool": {
                "value": False
            }
        },
        "Rotation": {
            "Float": {
                "value": 0.0
            }
        },
        "Activated": {
            "Bool": {
                "value": True
            }
        },
        "ItemCustomName": {
            "Name": {
                "value": "None"
            }
        },
        "ItemCustomFolder": {
            "Name": {
                "value": "None"
            }
        },
        "PhysicsSettings": {
            "Struct": {
                "value": {
                    "Struct": {
                        "PhysicsEnabled": {
                            "Bool": {
                                "value": False
                            }
                        },
                        "PhysicsCanPickup": {
                            "Bool": {
                                "value": True
                            }
                        },
                        "MassMultiplier": {
                            "Float": {
                                "value": 1.0
                            }
                        },
                        "PhysicsSurfaceType": {
                            "Enum": {
                                "value": "EItemSurfaceType::NORMAL",
                                "enum_type": "EItemSurfaceType"
                            }
                        },
                        "PhysicsRespawnAfterPickup": {
                            "Bool": {
                                "value": False
                            }
                        },
                        "PhysicsRespawnLocation": {
                            "Struct": {
                                "value": {
                                    "Struct": {
                                        "Rotation": {
                                            "Struct": {
                                                "value": {
                                                    "Quat": {
                                                        "x": 0.0,
                                                        "y": 0.0,
                                                        "z": 0.0,
                                                        "w": 1.0
                                                    }
                                                },
                                                "struct_type": "Quat",
                                                "struct_id": "00000000-0000-0000-0000-000000000000"
                                            }
                                        },
                                        "Translation": {
                                            "Struct": {
                                                "value": {
                                                    "Vector": {
                                                        "x": 0.0,
                                                        "y": 0.0,
                                                        "z": 0.0
                                                    }
                                                },
                                                "struct_type": "Vector",
                                                "struct_id": "00000000-0000-0000-0000-000000000000"
                                            }
                                        },
                                        "Scale3D": {
                                            "Struct": {
                                                "value": {
                                                    "Vector": {
                                                        "x": 1.0,
                                                        "y": 1.0,
                                                        "z": 1.0
                                                    }
                                                },
                                                "struct_type": "Vector",
                                                "struct_id": "00000000-0000-0000-0000-000000000000"
                                            }
                                        }
                                    }
                                },
                                "struct_type": {
                                    "Struct": "Transform"
                                },
                                "struct_id": "00000000-0000-0000-0000-000000000000"
                            }
                        },
                        "PhysicsRespawnDelay": {
                            "Float": {
                                "value": 5.0
                            }
                        }
                    }
                },
                "struct_type": {
                    "Struct": "ItemPhysics"
                },
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "ItemGroupID": {
            "Struct": {
                "value": {
                    "Guid": "00000000-0000-0000-0000-000000000000"
                },
                "struct_type": "Guid",
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "GroupID": {
            "Int": {
                "value": -1
            }
        },
        "ItemLocked": {
            "Bool": {
                "value": False
            }
        },
        "ItemNoCollide": {
            "Bool": {
                "value": False
            }
        },
        "SpawnDefaults": {
            "Struct": {
                "value": {
                    "Struct": {
                        "Hidden": {
                            "Bool": {
                                "value": False
                            }
                        },
                        "Active": {
                            "Bool": {
                                "value": True
                            }
                        }
                    }
                },
                "struct_type": {
                    "Struct": "ItemSpawnDefaults"
                },
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "InteractiveState": {
            "Enum": {
                "value": "FItemInteractiveState::EVERYONE",
                "enum_type": "FItemInteractiveState"
            }
        },
        "ItemConnections": {
            "Array": {
                "array_type": "StructProperty",
                "value": {
                    "Struct": {
                        "_type": "ItemConnections",
                        "name": "StructProperty",
                        "struct_type": {
                            "Struct": "ItemConnectionData"
                        },
                        "id": "00000000-0000-0000-0000-000000000000",
                        "value": []
                    }
                }
            }
        },
        "OwningSteamID": {
            "Struct": {
                "value": {
                    "Struct": {}
                },
                "struct_type": {
                    "Struct": "SteamID"
                },
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "ActiveDragSlot": {
            "Byte": {
                "value": {
                    "Byte": 0
                },
                "enum_type": "None"
            }
        },
        "bCanBeDamaged": {
            "Bool": {
                "value": True
            }
        }
    }
}


def load_mesh(path: str):
    mesh = o3d.io.read_triangle_mesh(path)
    vertices = np.asarray(mesh.vertices)
    tris = np.asarray(mesh.triangles)

    faces = []
    for tri in tris:
        faces.append(vertices[tri])

    return faces


# Given a triangular face as input, it will divide it into two right triangles using the altitude
def divide_triangle(face: np.ndarray):
    for idx in range(3):
        v0 = face[idx]
        v1 = face[(idx + 1) % 3]
        v2 = face[(idx + 2) % 3]

        opp_line = v2 - v1
        perp = xyz(np.cross(opp_line, np.cross(v1 - v0, v2 - v0))).normalize()

        lin_op = np.transpose(np.array([opp_line, perp]))
        b = v0 - v1
        soln = np.dot(np.linalg.pinv(lin_op), np.array([[b[0]], [b[1]], [b[2]]]))

        foot_coeff = soln[0][0]
        if foot_coeff < 0 or foot_coeff > 1:
            continue

        v3 = foot_coeff * opp_line + v1
        return np.array([[v3, v1, v0], [v3, v2, v0]])

    print('OOF')
    return [face]


def convert_triangle(face: np.ndarray):
    tris = divide_triangle(face)
    wedges = []
    for tri in tris:
        #print('Face')
        #print(tri)
        wedge = TowerObject(item=WEDGE_ITEM_DATA, properties=WEDGE_PROPERTY_DATA)
        wedge.item['guid'] = str(uuid.uuid4()).lower()

        # Scale from side lengths
        scale = wedge.scale
        scale[0] = xyz(tri[1]).distance(tri[0]) / 50
        scale[1] = 0.01
        scale[2] = xyz(tri[0]).distance(tri[2]) / 50
        wedge.scale = scale

        #if scale[0] < 0.01 or scale[1] < 0.01 or scale[2] < 0.01:
        #    print(f'FUUCK: {scale}')

        # Apply rotation
        ab_dir = xyz(tri[1] - tri[0]).normalize()
        ac_dir = xyz(tri[2] - tri[0]).normalize()
        perp = xyz(np.cross(ab_dir, ac_dir)).normalize()
        rot_matrix = np.matrix.transpose(np.array([ab_dir, -perp, ac_dir]))
        #print('Rotation matrix:')
        #print(rot_matrix)
        #print(np.linalg.det(rot_matrix))
        #eggs = np.linalg.eigvals(rot_matrix)
        #print(eggs)
        rot = R.from_matrix(rot_matrix)
        #print(rot.as_matrix())
        wedge.rotation = rot.as_quat()

        # Translate to centroid
        wedge_pos = np.array([[-25 * scale[0], 0, 0], [25 * scale[0], 0, 0], [-25 * scale[0], 0, 50 * scale[2]]],
                             dtype=np.float64)
        wedge_pos = rot.apply(wedge_pos)
        wedge_centroid = np.sum(wedge_pos, axis=0) / 3
        wedge.position -= wedge_centroid

        tri_centroid = np.sum(tri, axis=0) / 3
        wedge.position += tri_centroid

        #print('Position:')
        #print(wedge.position)

        wedges.append(wedge)

    return wedges


def convert_mesh(save: Suitebro, mesh: list[np.ndarray], offset=xyz(0, 0, 0)):
    wedges = []
    for face in mesh:
        wedges += convert_triangle(face * 100)

    for wedge in wedges:
        wedge.position += offset

    save.add_objects(wedges)
