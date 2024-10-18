import json
import sys
import uuid
from typing import Optional

import open3d as o3d
import numpy as np

from scipy.spatial.transform import Rotation as R

from .logging import *
from .object import TowerObject
from .selection import Selection
from .suitebro import Suitebro
from .tool_lib import ParameterDict
from .tools import rotate
from .util import xyz, XYZ, XYZW

WEDGE_ITEM_DATA = json.loads('''
    {
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
    ''')

WEDGE_PROPERTY_DATA = json.loads('''
    {
      "name": "CanvasWedge_C_2",
      "properties": {
        "SlopeOverride": {
          "Bool": {
            "value": false
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
            "value": true
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
            "value": false
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
            "value": false
          }
        },
        "NSFW": {
          "Bool": {
            "value": false
          }
        },
        "Rotation": {
          "Float": {
            "value": 0.0
          }
        },
        "Activated": {
          "Bool": {
            "value": true
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
                    "value": false
                  }
                },
                "PhysicsCanPickup": {
                  "Bool": {
                    "value": true
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
                    "value": false
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
            "value": false
          }
        },
        "ItemNoCollide": {
          "Bool": {
            "value": false
          }
        },
        "SpawnDefaults": {
          "Struct": {
            "value": {
              "Struct": {
                "Hidden": {
                  "Bool": {
                    "value": false
                  }
                },
                "Active": {
                  "Bool": {
                    "value": true
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
            "value": true
          }
        }
      }
    }
    ''')


class OctreeNode:
    """Axis-aligned octree node implementation"""

    def __init__(self, centroid: XYZ, size: float, point: XYZ):
        self.centroid = centroid
        self.size = size
        self.point = point
        self.children = [None] * 8

    def contains(self, point: XYZ) -> bool:
        return point.clamp(self.centroid - self.size / 2, self.centroid + self.size / 2).distance(point) < XYZ.EPSILON

    def traverse(self, point: XYZ) -> Optional['OctreeNode']:
        if not self.contains(point):
            return None

        pos_dirs = point >= self.centroid
        dirs = [1 if x else 0 for x in pos_dirs]
        bitstring = dirs[2] << 2 | dirs[1] << 1 | dirs[0]
        return self.children[bitstring]


class OctreeBVH:
    def __init__(self, centroid: XYZ, size: float):
        self.root = None
        self.centroid = centroid
        self.size = size

    def add_point(self, p: XYZ):
        if self.root is None:
            self.root = OctreeNode(self.centroid, self.size, p)

        # TODO


def load_mesh(path):
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
        # First fix the coordinate system handedness
        for vert in tri:
            vert[0], vert[1] = vert[1], vert[0]

        # Wedge object for triangle
        wedge = TowerObject(item=WEDGE_ITEM_DATA, properties=WEDGE_PROPERTY_DATA)

        # Scale from side lengths
        scale = wedge.scale
        scale[0] = xyz(tri[1]).distance(tri[0]) / 50
        scale[1] = 0.01
        scale[2] = xyz(tri[0]).distance(tri[2]) / 50
        wedge.scale = scale

        # Apply rotation
        ab_dir = xyz(tri[1] - tri[0]).normalize()
        ac_dir = xyz(tri[2] - tri[0]).normalize()
        perp = xyz(np.cross(ab_dir, ac_dir)).normalize()
        rot_matrix = np.matrix.transpose(np.array([ab_dir, -perp, ac_dir]))
        rot = R.from_matrix(rot_matrix)
        wedge.rotation = XYZW(rot.as_quat())

        # Translate to centroid
        wedge_pos = np.array([[-25 * scale[0], 0, 0], [25 * scale[0], 0, 0], [-25 * scale[0], 0, 50 * scale[2]]],
                             dtype=np.float64)
        wedge_pos = rot.apply(wedge_pos)
        wedge_centroid = np.sum(wedge_pos, axis=0) / 3
        wedge.position -= wedge_centroid

        tri_centroid = np.sum(tri, axis=0) / 3
        wedge.position += tri_centroid

        wedges.append(wedge)

    return wedges


def convert_mesh(save: Suitebro, mesh: list[np.ndarray], offset=xyz(0, 0, 0)) -> Selection:
    wedges = []
    for face in mesh:
        wedges += convert_triangle(face * 100)

    # Fix mesh rotation
    rotate.main(save, Selection(wedges), ParameterDict({'rotation': xyz(0, -90, 0), 'local': False}))

    for wedge in wedges:
        wedge.position += offset

    save.add_objects(wedges)

    return Selection(wedges)
