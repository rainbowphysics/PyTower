import json
import sys
import uuid

import open3d as o3d
import numpy as np

from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize, OptimizeResult

from .object import TowerObject

WEDGE_ITEM_DATA = json.loads('''
    {
      "name": "CanvasWedge",
      "guid": "",
      "format_version": 1,
      "unreal_version": 517,
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


def load_mesh(path):
    mesh = o3d.io.read_triangle_mesh(path)
    vertices = np.asarray(mesh.vertices)
    tris = np.asarray(mesh.triangles)

    faces = []
    for tri in tris:
        faces.append(vertices[tri])

    return faces


def convert_triangle(face: np.ndarray):
    wedge1 = TowerObject(item=WEDGE_ITEM_DATA, properties=WEDGE_PROPERTY_DATA)
    wedge1.item['guid'] = str(uuid.uuid4()).lower()
    wedge2 = wedge1.copy()

    # Create our standard triangle
    wedge1.position[0] = 25
    wedge1.position[1] = -50 / 3
    wedge1.scale[1] = 0.01
    wedge2.position[0] = -25
    wedge2.position[1] = -50 / 3
    wedge2.scale[1] = 0.01
    wedge2.rotation = R.from_euler('xyz', np.array([0, 0, 180]), degrees=True).as_quat()

    # Translate given triangle face back to origin
    centroid = np.sum(face, axis=0)
    face -= centroid

    # Rotate so that it faces the y-axis and is upright w.r.t. z-axis
    def optimize_func(input_vec):
        quat = input_vec[0:3]
        translate = input_vec[3:]
        rot = R.from_quat(quat)
        rotated = rot.apply(face)
        rotated += translate
        xy = rotated[1] - rotated[0]
        xz = rotated[2] - rotated[0]
        cross = np.cross(xy, xz)
        return (np.abs(cross[0]) + np.abs(cross[2]) + np.abs(rotated[1][0]) + np.abs(rotated[1][2])
                + max(-rotated[1][1], 0) + np.abs(rotated[0][1]) + np.abs(rotated[0][2]) + np.abs(rotated[2][1])
                + np.abs(rotated[2][2]))

    res: OptimizeResult = minimize(optimize_func, np.array([0, 0, 0, 0, 0, 0]))

    if not res.success:
        print(f'Panic: {res.message}')
        sys.exit(1)

    ans_quat = res.x[0:3]
    ans_translate = res.x[3:]
    rot = R.from_quat(ans_quat)
    face = rot.apply(face)
    face += ans_translate

    # Now simply scale the triangle
    scale_y = 50 / face[1][1]
    wedge1_scale_x_inv = 50 / face[0][0]
    wedge2_scale_x_inv = -50 / face[2][0]
    wedge1_translate_x_inv = 25 / wedge1_scale_x_inv - 25
    wedge2_translate_x_inv = 25 / wedge2_scale_x_inv - 25

    # TODO now apply TRTS model matrix to wedges


def convert(mesh):
    for face in mesh:
        convert_triangle(face)
