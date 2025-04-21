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

from typing import *
import json

import numpy as np
import cv2
from mediapipe.python.solutions import holistic
from mediapipe.python.solutions import face_mesh_connections
from mediapipe.python.solutions import drawing_utils, drawing_styles

from ..core.config import load_config
from ..core.index import Index

#####################################################
### Note ############################################
#####################################################
# This module will delete at version 0.3
# please use mpdriver.engine.mediapipe instead of it
#


_T = TypeVar("_T")
NDArray = np.ndarray[Any, np.dtype[_T]]

X = 0
Y = 1
Z = 2

### Landmark Definition

class Pose(Index):
  "MediaPipe Pose Index"
  NOSE            : Literal[ 0]
  LEFT_EYE_INNER  : Literal[ 1]
  LEFT_EYE        : Literal[ 2]
  LEFT_EYE_OUTER  : Literal[ 3]
  RIGHT_EYE_INNER : Literal[ 4]
  RIGHT_EYE       : Literal[ 5]
  RIGHT_EYE_OUTER : Literal[ 6]
  LEFT_EAR        : Literal[ 7]
  RIGHT_EAR       : Literal[ 8]
  MOUTH_LEFT      : Literal[ 9]
  MOUTH_RIGHT     : Literal[10]
  LEFT_SHOULDER   : Literal[11]
  RIGHT_SHOULDER  : Literal[12]
  LEFT_ELBOW      : Literal[13]
  RIGHT_ELBOW     : Literal[14]
  LEFT_WRIST      : Literal[15]
  RIGHT_WRIST     : Literal[16]
  LEFT_PINKY      : Literal[17]
  RIGHT_PINKY     : Literal[18]
  LEFT_INDEX      : Literal[19]
  RIGHT_INDEX     : Literal[20]
  LEFT_THUMB      : Literal[21]
  RIGHT_THUMB     : Literal[22]
  LEFT_HIP        : Literal[23]
  RIGHT_HIP       : Literal[24]
  LEFT_KNEE       : Literal[25]
  RIGHT_KNEE      : Literal[26]
  LEFT_ANKLE      : Literal[27]
  RIGHT_ANKLE     : Literal[28]
  LEFT_HEEL       : Literal[29]
  RIGHT_HEEL      : Literal[30]
  LEFT_FOOT_INDEX : Literal[31]
  RIGHT_FOOT_INDEX: Literal[32]

class Hand(Index):
  """
  MediaPipe Hand Index
  """
  WRIST            : Literal[ 0]
  THUMB_CMC        : Literal[ 1]
  THUMB_MDP        : Literal[ 2]
  THUMB_IP         : Literal[ 3]
  THUMB_TIP        : Literal[ 4]
  INDEX_FINGER_MCP : Literal[ 5]
  INDEX_FINGER_PIP : Literal[ 6]
  INDEX_FINGER_DIP : Literal[ 7]
  INDEX_FINGER_TIP : Literal[ 8]
  MIDDLE_FINGER_MCP: Literal[ 9]
  MIDDLE_FINGER_PIP: Literal[10]
  MIDDLE_FINGER_DIP: Literal[11]
  MIDDLE_FINGER_TIP: Literal[12]
  RING_FINGER_MCP  : Literal[13]
  RING_FINGER_PIP  : Literal[14]
  RING_FINGER_DIP  : Literal[15]
  RING_FINGER_TIP  : Literal[16]
  PINKY_FINGER_MCP : Literal[17]
  PINKY_FINGER_PIP : Literal[18]
  PINKY_FINGER_DIP : Literal[19]
  PINKY_FINGER_TIP : Literal[20]

Face = tuple(range(468))

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

MediaPipeDict = dict[Literal["face", "left_hand", "right_hand", "pose"], _T]

class TargetSpec(TypedDict):
    indices: Sequence[int] | slice
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

class MediaPipeIndicesOptions(TypedDict):
    face: list[int] | None
    left_hand: list[str] | None
    right_hand: list[str] | None
    pose: list[str] | None

class MediaPipeOptions(TypedDict):
    holistic: MediaPipeHolisticOptions
    indices: MediaPipeIndicesOptions
    order: list[Literal["face", "left_hand", "right_hand", "pose"]]

mediapipe_config: MediaPipeOptions = load_config('mediapipe')
mediapipe_holistic_config = mediapipe_config['holistic']
mediapipe_indices_config = mediapipe_config["indices"]
mediapipe_order_config = mediapipe_config["order"]

### configration

DEFAULT_DETECT_TARGETS = MediaPipeDict[TargetSpec](
    face = {
        "indices": slice(None) if (i := mediapipe_indices_config["face"]) is None else i,
        "connections": holistic.FACEMESH_CONTOURS,
        "landmark_drawing_spec": {idx: drawing_utils.DrawingSpec() for idx in range(len(Face))},
        "connection_drawing_spce": drawing_styles.get_default_face_mesh_contours_style()
    },
    left_hand = {
        "indices": slice(None) if (i := mediapipe_indices_config["left_hand"]) is None else [getattr(Hand, j) for j in i if hasattr(Hand, j)],
        "connections": holistic.HAND_CONNECTIONS,
        "landmark_drawing_spec": drawing_styles.get_default_hand_landmarks_style(),
        "connection_drawing_spce": drawing_styles.get_default_hand_connections_style()
    },
    right_hand = {
        "indices": slice(None) if (i := mediapipe_indices_config["right_hand"]) is None else [getattr(Hand, j) for j in i if hasattr(Hand, j)],
        "connections": holistic.HAND_CONNECTIONS,
        "landmark_drawing_spec": drawing_styles.get_default_hand_landmarks_style(),
        "connection_drawing_spce": drawing_styles.get_default_hand_connections_style()
    },
    pose = {
        "indices": slice(None) if (i := mediapipe_indices_config["pose"]) is None else [getattr(Hand, j) for j in i if hasattr(Hand, j)],
        "connections": holistic.POSE_CONNECTIONS,
        "landmark_drawing_spec": drawing_styles.get_default_pose_landmarks_style(),
        "connection_drawing_spce": {conn: drawing_utils.DrawingSpec() for conn in holistic.POSE_CONNECTIONS}
    }
)

### body

class MP:

    def __init__(
        self,
        detect_targets: Iterable[Literal["face", "left_hand", "right_hand", "pose"]] | None = None,
        holistic_options: MediaPipeHolisticOptions | None = None
        ):

        self.holistic = holistic.Holistic(**(holistic_options or mediapipe_holistic_config))
        self.detect_targets = frozenset(DEFAULT_DETECT_TARGETS.keys() if detect_targets is None else detect_targets)
    
    def detect_landmarks2ndarray(self, landmark_list: LandmarkList | None, landmark_index: Sized) -> NDArray[np.float32]:

        if landmark_list is None:
            return np.full([len(landmark_index), 3], np.nan, dtype=np.float32)
        else:
            return np.array([(float(lm.x), float(lm.y), float(lm.z)) for lm in landmark_list.landmark], dtype=np.float32)

    def detect(self, img: cv2.Mat) -> MediaPipeDict[NDArray[np.float32]]:

        solution_outputs: SolutionOutputs = self.holistic.process(img)

        detect_output = {
            "face": self.detect_landmarks2ndarray(solution_outputs.face_landmarks, Face) if "face" in self.detect_targets else None,
            "left_hand": self.detect_landmarks2ndarray(solution_outputs.left_hand_landmarks, Hand) if "left_hand" in self.detect_targets else None,
            "right_hand": self.detect_landmarks2ndarray(solution_outputs.right_hand_landmarks, Hand) if "right_hand" in self.detect_targets else None,
            "pose": self.detect_landmarks2ndarray(solution_outputs.pose_landmarks, Pose) if "pose" in self.detect_targets else None
        }

        return MediaPipeDict((o, detect_output[o]) for o in mediapipe_order_config)

    def annotate_pixel_coordinates(self, landmark_array: NDArray[np.float32], width: int, height: int) -> NDArray[np.float32]:

        return np.clip(
            a = landmark_array[:, :2] * (width - 1, height - 1),
            a_min = (0, 0),
            a_max = (width, height)
        ).astype(np.int_)

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

        mask = cv2.fillConvexPoly(
            np.zeros_like(src_img),
            [face_pixel_coord[p] for p, _ in face_mesh_connections.FACEMESH_FACE_OVAL],
            (255, 255, 255) # bgr
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

        for target, coord in pixel_coordinates.items():

            if np.isnan(coord).any(): continue

            if draw_connection:
                out_img = self.annotate_draw_connections(
                    out_img, coord,
                    DEFAULT_DETECT_TARGETS[target]["connections"],
                    DEFAULT_DETECT_TARGETS[target]["connection_drawing_spce"]
                )

            if draw_landmark:
                out_img = self.annotate_draw_landmarks(
                    out_img, coord,
                    DEFAULT_DETECT_TARGETS[target]["landmark_drawing_spec"],
                )

        if mask_face_oval and "face" in pixel_coordinates:
            out_img = self.annotate_face_masking(
                out_img, pixel_coordinates["face"],
                cv2.blur(out_img, max(out_img.shape[0], out_img.shape[1]) // 100)
            )

        return out_img
    
    def normalize(
        self,
        mp_dict: MediaPipeDict[NDArray[np.float32]],
        clip: bool = True
        ):

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
                    a_min = np.array([clip_domain["left"], clip_domain["top"], -np.inf]),
                    a_max = np.array([clip_domain["right"], clip_domain["bottom"], np.inf])
                )
                if clip else
                landmark_array
            ) / np.array([clip_domain["right"] - clip_domain["left"], clip_domain["bottom"] - clip_domain["top"], 1])
            for target, landmark_array in mp_dict.items() if landmark_array is not None
        })

    def flatten(
        self,
        mp_dict: MediaPipeDict[NDArray[np.float32]],
        ):

        return np.concatenate([
            landmark_array[DEFAULT_DETECT_TARGETS[target]["indices"]]
            for target, landmark_array in mp_dict.items()
        ], axis=-2).reshape(-1)
