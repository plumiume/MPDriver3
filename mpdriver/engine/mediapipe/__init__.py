# Copyright 2024 The MPDriver3 Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from itertools import chain
from pathlib import Path
from typing import *
from enum import IntEnum

import numpy as np
import cv2
from mediapipe.python.solutions import holistic
from mediapipe.python.solutions import face_mesh, face_mesh_connections
from mediapipe.python.solutions import drawing_utils, drawing_styles

from ...core.utils import raise_exception
from ...core.config import load_config
from ...core import index

_T = TypeVar("_T")
NDArray = np.ndarray[Any, np.dtype[_T]]

X = 0
Y = 1
Z = 2

TARGET_DIMS = Literal["x", "y", "z", "visibility"]
TARGET_NAMES = Literal["face", "left_hand", "right_hand", "pose"]

class MediaPipeDict(dict[TARGET_NAMES, _T]): ...


### Landmark Definition

class Pose(IntEnum):
    """
    MediaPipe Pose Index
    """
    NOSE             =  0
    LEFT_EYE_INNER   =  1
    LEFT_EYE         =  2
    LEFT_EYE_OUTER   =  3
    RIGHT_EYE_INNER  =  4
    RIGHT_EYE        =  5
    RIGHT_EYE_OUTER  =  6
    LEFT_EAR         =  7
    RIGHT_EAR        =  8
    MOUTH_LEFT       =  9
    MOUTH_RIGHT      = 10
    LEFT_SHOULDER    = 11
    RIGHT_SHOULDER   = 12
    LEFT_ELBOW       = 13
    RIGHT_ELBOW      = 14
    LEFT_WRIST       = 15
    RIGHT_WRIST      = 16
    LEFT_PINKY       = 17
    RIGHT_PINKY      = 18
    LEFT_INDEX       = 19
    RIGHT_INDEX      = 20
    LEFT_THUMB       = 21
    RIGHT_THUMB      = 22
    LEFT_HIP         = 23
    RIGHT_HIP        = 24
    LEFT_KNEE        = 25
    RIGHT_KNEE       = 26
    LEFT_ANKLE       = 27
    RIGHT_ANKLE      = 28
    LEFT_HEEL        = 29
    RIGHT_HEEL       = 30
    LEFT_FOOT_INDEX  = 31
    RIGHT_FOOT_INDEX = 32

class Hand(IntEnum):
    """
    MediaPipe Hand Index
    """
    WRIST             =  0
    THUMB_CMC         =  1
    THUMB_MCP         =  2
    THUMB_IP          =  3
    THUMB_TIP         =  4
    INDEX_FINGER_MCP  =  5
    INDEX_FINGER_PIP  =  6
    INDEX_FINGER_DIP  =  7
    INDEX_FINGER_TIP  =  8
    MIDDLE_FINGER_MCP =  9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP   = 13
    RING_FINGER_PIP   = 14
    RING_FINGER_DIP   = 15
    RING_FINGER_TIP   = 16
    PINKY_MCP  = 17
    PINKY_PIP  = 18
    PINKY_DIP  = 19
    PINKY_TIP  = 20

Face = tuple(range(face_mesh.FACEMESH_NUM_LANDMARKS))

INDEXINGS = MediaPipeDict[type[IntEnum] | Sequence[int]](
    face = Face,
    left_hand = Hand,
    right_hand = Hand,
    pose = Pose
)


### Mediapipe result

class Landmark:
    x: float
    y: float
    z: float
    visibility: float

class LandmarkList:
    landmark: list[Landmark]

class SolutionOutputs:
    face_landmarks: LandmarkList
    left_hand_landmarks: LandmarkList
    right_hand_landmarks: LandmarkList
    pose_landmarks: LandmarkList


### config/mediapipe.json

class TargetSpec(TypedDict):
    landmark_indices: slice | list[int]
    connections: frozenset[tuple[int, int]]
    landmark_drawing_spec: Mapping[int, drawing_utils.DrawingSpec]
    connection_drawing_spce: Mapping[tuple[int, int], drawing_utils.DrawingSpec]

class MediaPipeHolisticOptions(TypedDict):
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#cross-platform-configuration-options"
    static_image_mode: bool # False
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#static_image_mode"
    model_complexity: int # 1
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#model_complexity"
    smooth_landmarks: bool # True
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#smooth_landmarks"
    enable_segmentation: bool # False
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#enable_segmentation"
    smooth_segmentation: bool # True
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#smooth_segmentation"
    refine_face_landmarks: bool # False
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#refine_face_landmarks"
    min_detection_confidence: float # 0.5
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#min_detection_confidence"
    min_tracking_confidence: float # 0.5
    "https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md#min_tracking_confidence"

class MediaPipeLandmarkIndicesOptions(TypedDict):
    "None is a configuration that use all landmarks"
    face: list[int] | None
    left_hand: list[str] | None
    right_hand: list[str] | None
    pose: list[str] | None

MediaPipeAnnotateTargetsOptions = list[TARGET_NAMES]
MediaPipeDimensionTargetsOptions = list[TARGET_DIMS]

class MediaPipeOptions(TypedDict):
    holistic: MediaPipeHolisticOptions
    landmark_indices: MediaPipeLandmarkIndicesOptions
    annotate_targets: MediaPipeAnnotateTargetsOptions
    dimension_targets: MediaPipeDimensionTargetsOptions

mediapipe_config = load_config('mediapipe', default_path=Path('engine/mediapipe'), ctype=MediaPipeOptions)


### configration

dffo = dict(face_mesh.FACEMESH_FACE_OVAL)
tmp = next(iter(dffo))
FACEMESH_FACE_OVAL_ORDERED = [tmp]
while (tmp := dffo.pop(tmp, None)) is not None:
    FACEMESH_FACE_OVAL_ORDERED.append(tmp)

# DEFAULT_HOLISTIC_KWARGS = mediapipe_config['holistic']
# DEFAULT_LANDMARK_INDICES = mediapipe_config['landmark_indices']
# DEFAULT_ANNOTATE_TARGETS = mediapipe_config['annotate_targets']
# DEFAULT_DIMENSION_TARGETS = mediapipe_config['dimension_targets']
DEFAULT_CONNECTIONS = MediaPipeDict(
    face=holistic.FACEMESH_CONTOURS,
    left_hand=holistic.HAND_CONNECTIONS,
    right_hand=holistic.HAND_CONNECTIONS,
    pose=holistic.POSE_CONNECTIONS
)
DEFAULT_LANDMARK_DRAWING_SPEC = MediaPipeDict(
    face={lm: drawing_utils.DrawingSpec(circle_radius=0) for lm in Face},
    left_hand=drawing_styles.get_default_hand_landmarks_style(),
    right_hand=drawing_styles.get_default_hand_landmarks_style(),
    pose=drawing_styles.get_default_pose_landmarks_style()
)
DEFAULT_CONNECTION_DRAWING_SPEC = MediaPipeDict(
    face=drawing_styles.get_default_face_mesh_contours_style(),
    left_hand=drawing_styles.get_default_hand_connections_style(),
    right_hand=drawing_styles.get_default_hand_connections_style(),
    pose={conn: drawing_utils.DrawingSpec() for conn in holistic.POSE_CONNECTIONS}
)


### body

class MP:

    def __init__(
        self,
        holistic_options: MediaPipeHolisticOptions | None = None,
        landmarks_indices: MediaPipeLandmarkIndicesOptions | None = None,
        annotate_targets: MediaPipeAnnotateTargetsOptions | None = None,
        dimension_targets: MediaPipeDimensionTargetsOptions | None = None,
        connections: MediaPipeDict[set[tuple[int, int]]] | None = None,
        landmark_drawing_spec: MediaPipeDict[Mapping[int, drawing_utils.DrawingSpec]] | None = None,
        connection_drawing_spec: MediaPipeDict[Mapping[tuple[int, int], drawing_utils.DrawingSpec]] | None = None
        ):

        self.header_cache = ''
        self.dims_cache: list[int] | None = None

        self.holistic = holistic.Holistic(**(holistic_options or mediapipe_config['holistic']))
        self.landmark_indices = MediaPipeDict({
            target: index.to_landmark_indices(INDEXINGS[target], indices)
            for target, indices in (landmarks_indices or mediapipe_config['landmark_indices']).items()
        })
        self.annotate_targets = annotate_targets or mediapipe_config['annotate_targets']
        self.dimension_targets = {
            dim_name: (
                0 if dim_name == 'x' else
                1 if dim_name == 'y' else
                2 if dim_name == 'z' else
                3 if dim_name == 'visibility' else
                raise_exception(NameError, f'invalid dimension name ({dim_name})')
            )
            for dim_name in (dimension_targets or mediapipe_config['dimension_targets'])
        }
        self.connections = connections or DEFAULT_CONNECTIONS
        self.landmark_drawing_spec = landmark_drawing_spec or DEFAULT_LANDMARK_DRAWING_SPEC
        self.connection_drawing_spec = connection_drawing_spec or DEFAULT_CONNECTION_DRAWING_SPEC

    def detect_landmarks2ndarray(self, landmark_list: LandmarkList | None, landmark_index: Sized) -> NDArray[np.float32]:

        if landmark_list is None:
            return np.full([len(landmark_index), 4], np.nan, dtype=np.float32)
        else:
            return np.array([(float(lm.x), float(lm.y), float(lm.z), float(lm.visibility)) for lm in landmark_list.landmark], dtype=np.float32)

    def detect(self, img: cv2.Mat) -> MediaPipeDict[NDArray[np.float32]]:

        solution_outputs: SolutionOutputs = self.holistic.process(img)

        return MediaPipeDict(
            face=self.detect_landmarks2ndarray(solution_outputs.face_landmarks, Face),
            left_hand=self.detect_landmarks2ndarray(solution_outputs.left_hand_landmarks, Hand),
            right_hand=self.detect_landmarks2ndarray(solution_outputs.right_hand_landmarks, Hand),
            pose=self.detect_landmarks2ndarray(solution_outputs.pose_landmarks, Pose)
        )

    def annotate_pixel_coordinates(self, landmark_array: NDArray[np.float32], width: int, height: int) -> NDArray[np.float32]:

        return np.clip(
            a = landmark_array[:, :2] * (width - 1, height - 1),
            a_min = (0, 0),
            a_max = (width, height)
        ).astype(np.int32)

    def annotate_draw_connections(
        self, img: cv2.Mat, pixel_coord: NDArray[np.float32],
        connections: frozenset[tuple[int, int]],
        connection_draw_spec: Mapping[tuple[int, int], drawing_utils.DrawingSpec]
        ) -> cv2.Mat:

        for conn in connections:
            start_point, end_point = conn
            drawing_spec = connection_draw_spec[conn]
            img = cv2.line(
                img,
                pixel_coord[start_point], pixel_coord[end_point],
                drawing_spec.color, drawing_spec.thickness
            )

        return img

    def annotate_draw_landmarks(
        self, img: cv2.Mat, pixel_coord: NDArray[np.float32],
        landmark_draw_spec: Mapping[int, drawing_utils.DrawingSpec],
        ) -> cv2.Mat:

        for idx, p in enumerate(pixel_coord):
            drawing_spec = landmark_draw_spec[idx]
            circle_boarder_radius =  max(drawing_spec.circle_radius + 1, int(drawing_spec.circle_radius * 1.2))
            img = cv2.circle(img, p, circle_boarder_radius, (255, 255, 255), drawing_spec.thickness)
            img = cv2.circle(img, p, drawing_spec.circle_radius, drawing_spec.color, drawing_spec.thickness)
    
        return img

    def annotate_face_masking(self, src_img: cv2.Mat, face_pixel_coord: NDArray[np.float32], mask_img: cv2.Mat) -> cv2.Mat:

        mask = cv2.fillPoly(
        # mask = cv2.polylines(
            np.zeros_like(src_img),
            [face_pixel_coord[FACEMESH_FACE_OVAL_ORDERED]],
            color=(255, 255, 255), # bgr=white
            # isClosed=True,
        )

        return np.where(mask, mask_img, src_img)

    def annotate(
        self,
        img: cv2.Mat,
        mp_dict: MediaPipeDict[NDArray[np.float32] | None],
        draw_connection: bool = True,
        draw_landmark: bool = True,
        mask_face_oval: bool = False
        ) -> cv2.Mat:

        out_img = img.copy()

        pixel_coordinates = MediaPipeDict[NDArray[np.float32]]({
            target: self.annotate_pixel_coordinates(landmark_array, img.shape[1], img.shape[0])
            for target, landmark_array in mp_dict.items()
            if landmark_array is not None and not np.isnan(landmark_array).any()
        })

        # draw and mask

        if mask_face_oval and "face" in pixel_coordinates:
            ksize = (tmp := np.array(img.shape[:2]) // 50) + (1 - tmp % 2)
            out_img = self.annotate_face_masking(
                out_img, pixel_coordinates["face"],
                cv2.blur(out_img, ksize)
            )

        for target in self.annotate_targets:

            if not target in pixel_coordinates: continue

            if np.isnan(pixel_coordinates[target]).any(): continue

            if draw_connection:
                out_img = self.annotate_draw_connections(
                    out_img, pixel_coordinates[target],
                    self.connections[target],
                    self.connection_drawing_spec[target]
                )

            if draw_landmark:
                out_img = self.annotate_draw_landmarks(
                    out_img, pixel_coordinates[target],
                    DEFAULT_LANDMARK_DRAWING_SPEC[target]
                )

        return out_img

    def normalize(
        self,
        mp_dict: MediaPipeDict[NDArray[np.float32]],
        clip: bool = True
        ):
        """
        Normalize the coordinates of the landmarks to a range of 0 to 1.

        Args:
            mp_dict (MediaPipeDict[NDArray[np.float32]]): The dictionary of landmarks.
            clip (bool): Whether to clip the coordinates to the range of 0 to 1.
        """

        center = (mp_dict['pose'][Pose.LEFT_SHOULDER] + mp_dict['pose'][Pose.RIGHT_SHOULDER]) / 2
        width = abs(mp_dict['pose'][Pose.LEFT_SHOULDER][X] - mp_dict['pose'][Pose.RIGHT_SHOULDER][X])

        clip_domain = {
            "left": center[X] - width, "right": center[X] + width,
            "top": center[Y] - width, "bottom": center[Y] + width
        }

        return MediaPipeDict[NDArray[np.float32]]({
            target: (
                np.clip(
                    landmark_array,
                    a_min = np.array([clip_domain["left"], clip_domain["top"], -np.inf, -np.inf]),
                    a_max = np.array([clip_domain["right"], clip_domain["bottom"], np.inf, np.inf])
                )
                if clip else
                landmark_array
            ) / np.array([clip_domain["right"] - clip_domain["left"], clip_domain["bottom"] - clip_domain["top"], 1, 1])
            for target, landmark_array in mp_dict.items() if landmark_array is not None
        })

    def flatten(
        self,
        mp_dict: MediaPipeDict[NDArray[np.float32]],
        as_3d: bool = False
        ):

        self.dims_cache = self.dims_cache or list(self.dimension_targets.values())

        if as_3d:
            return np.concatenate([
                mp_dict[target][indices][..., self.dims_cache]
                for target, indices in self.landmark_indices.items()
            ], axis=-2)

        else:
            return np.concatenate([
                mp_dict[target][indices][..., self.dims_cache]
                for target, indices in self.landmark_indices.items()
            ], axis=-2).reshape(-1)

    def get_header(self, delimiter = ','):

        self.header_cache = self.header_cache or delimiter.join(chain.from_iterable(
            index.get_header(
                enum=INDEXINGS[target],
                indices=indices,
                name_prefix=target,
                dim_names=[d.capitalize() for d in self.dimension_targets]
            )
            for target, indices in self.landmark_indices.items()
        ))
        return self.header_cache
