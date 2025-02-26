import json
import math
from typing import Optional

import open3d as o3d
import numpy as np
from open3d.cpu.pybind.geometry import TriangleMesh

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
        "SurfaceMaterial": {
          "Object": {
            "value": "/Game/Materials/Lobby/Condo/SimpleColor_Inst.SimpleColor_Inst"
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
                }
              }
            },
            "struct_type": {
              "Struct": "Colorable"
            },
            "struct_id": "00000000-0000-0000-0000-000000000000"
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
        "SurfaceMaterial": {
          "Object": {
            "value": "/Game/Materials/Lobby/Condo/SimpleColor_Inst.SimpleColor_Inst"
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
                }
              }
            },
            "struct_type": {
              "Struct": "Colorable"
            },
            "struct_id": "00000000-0000-0000-0000-000000000000"
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
        }
      }
    }
    ''')

COLOR_PATH = 'properties.SurfaceColorable.Struct.value.Struct.Color.Struct.value.LinearColor'

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

class TowerMesh:
    def __init__(self, mesh: TriangleMesh):
        self.vertices = np.asarray(mesh.vertices)  # shape (#V, 3)
        self.tri_ids = np.asarray(mesh.triangles)  # shape (#F, 3)

        self.vertex_colors = np.asarray(mesh.vertex_colors)  # shape (#V, 3)
        if self.vertex_colors.shape[0] == 0:
            self.vertex_colors = np.array([[255, 255, 255]] * self.vertices.shape[0])

        self.triangle_uvs = np.asarray(mesh.triangle_uvs)  # shape (3 * #F, 2)

        # Needed to filter out 0x0 Image objects, which crash NumPy
        textures_filtered = []
        for texture in mesh.textures:
            if np.all(texture.get_min_bound() == texture.get_max_bound()):
                textures_filtered.append(None)
            else:
                textures_filtered.append(texture)

        # shape [(#H_m, #W_m, 3)] * #M
        self.textures = [np.asarray(tex) if tex is not None else None for tex in textures_filtered]

        self.triangle_material_ids = np.asarray(mesh.triangle_material_ids)  # shape (#F,)

        self.triangles = self.vertices[self.tri_ids] # shape (#F, 3)

    def get_color(self, uv: np.ndarray, material_id: int) -> np.ndarray | None:
        texture = self.textures[material_id]
        if texture is None:
            return None

        height, width, _ = texture.shape
        u, v = uv[0], uv[1]

        # Bilinear interpolate
        w_value = u * width
        h_value = v * height

        # Assume GL_REPEAT mode with the modulus
        w_pixel_low = math.floor(w_value)
        w_pixel_high = math.ceil(w_value)
        h_pixel_low = math.floor(h_value)
        h_pixel_high = math.ceil(h_value)

        w_r = w_value - w_pixel_low
        h_r = h_value - h_pixel_low

        high_u_interp = (w_r * texture[h_pixel_high % height, w_pixel_high % width, :]
                         + (1 - w_r) * texture[h_pixel_high % height, w_pixel_low % width, :])
        low_u_interp = (w_r * texture[h_pixel_low % height, w_pixel_high % width, :]
                        + (1 - w_r) * texture[h_pixel_low % height, w_pixel_low % width, :])
        return h_r * high_u_interp + (1 - h_r) * low_u_interp

    def get_triangle_color(self, tri_id: int):
        uvs = self.triangle_uvs[3*tri_id:3*(tri_id+1)] # shape (3, 2)
        avg_color = np.zeros((3,))
        for uv_pair in uvs:
            color = self.get_color(uv_pair, int(self.triangle_material_ids[tri_id]))
            # if color is not None and (np.any(color > 255) or np.any(color < 0)):
            #     print(color)

            if color is not None:
                avg_color += color[:3] / 3

        return avg_color / 255

    def get_triangles(self) -> np.ndarray:
        # Results in 3x3 matrices
        return self.triangles

def load_mesh(path) -> TowerMesh:
    return TowerMesh(o3d.io.read_triangle_mesh(path))

def divide_triangle(face: np.ndarray) -> np.ndarray | None:
    """
    Given a triangular face as input, divide it into two right triangles using the altitude

    Args:
        face: List of triangle face's vertices

    Returns:
        Triangle subdivided into two right triangles (i.e., canvas wedges)
    """
    for idx in range(3):
        v0 = face[idx]
        v1 = face[(idx + 1) % 3]
        v2 = face[(idx + 2) % 3]

        opp_line = v2 - v1
        perp = xyz(np.cross(opp_line, np.cross(v1 - v0, v2 - v0))).normalize()

        lin_op = np.transpose(np.array([opp_line, perp]))
        b = v0 - v1

        try:
            soln = np.dot(np.linalg.pinv(lin_op), np.array([[b[0]], [b[1]], [b[2]]]))
        except np.linalg.LinAlgError:
            continue

        foot_coeff = soln[0][0]
        if foot_coeff < 0 or foot_coeff > 1:
            continue

        v3 = foot_coeff * opp_line + v1
        return np.array([[v3, v1, v0], [v3, v2, v0]])

    return None


def convert_triangle(face: np.ndarray, rgb: np.ndarray | None) -> list[TowerObject]:
    """
    Given a triangular face, convert the face into one or two canvas wedges

    Args:
        face: List of triangle face's vertices

    Returns:
        List of TowerObject corresponding to the new canvas wedges
    """
    tris = divide_triangle(face)
    if tris is None:
        return []

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

        # Double-check rotation is non-zero or NAN
        bad_rotation = False
        if wedge.rotation.norm() < XYZ.EPSILON or np.isnan(wedge.rotation.norm()):
            bad_rotation = True

        if bad_rotation:
            wedge.rotation = XYZW(0.0, 0.0, 0.0, 1.0)

        # Translate to centroid
        wedge_pos = np.array([[-25 * scale[0], 0, 0], [25 * scale[0], 0, 0], [-25 * scale[0], 0, 50 * scale[2]]],
                             dtype=np.float64)

        if not bad_rotation:
            wedge_pos = rot.apply(wedge_pos)
        wedge_centroid = np.sum(wedge_pos, axis=0) / 3
        wedge.position -= wedge_centroid

        tri_centroid = np.sum(tri, axis=0) / 3
        wedge.position += tri_centroid

        wedges.append(wedge)

    if rgb is not None:
        for wedge in wedges:
            wedge.set_property(COLOR_PATH, {'r': rgb[0], 'g': rgb[1], 'b': rgb[2], 'a': 1.0})

    return wedges


def convert_mesh(save: Suitebro, mesh: TowerMesh, offset=xyz(0, 0, 0)) -> Selection:
    """
    Given a mesh as a list of faces, convert the mesh to TowerObjects (i.e., canvas wedges)

    Args:
        save: Save to add the new TowerObjects to
        mesh: Mesh as a list of faces
        offset: (Optional) Positional offset to apply

    Returns:
        Selection of the converted mesh
    """
    wedges = []
    for tri_id, face in enumerate(mesh.get_triangles()):
        wedges += convert_triangle(face * 60, mesh.get_triangle_color(tri_id))

    # Fix mesh rotation
    rotate.main(save, Selection(wedges), ParameterDict({'rotation': xyz(0, -90, 0), 'local': False}))

    for wedge in wedges:
        wedge.position += offset

    save.add_objects(wedges)

    return Selection(wedges)
