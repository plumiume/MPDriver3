### Lang
[JA](/rm/engine/mediapipe/ja.md)
[CH](/rm/engine/mediapipe/ch.md)

## MPDriver3 Configuration File README

This README provides a detailed explanation of each item in the MPDriver3 configuration file.

### 1. holistic

Configure the MediaPipe Holistic model settings.

- **static_image_mode**: Enable/disable static image mode (boolean). Default is `false`.
- **model_complexity**: Model complexity (0, 1, 2). Default is `1`.
- **smooth_landmarks**: Landmark smoothing (boolean). Default is `true`.
- **enable_segmentation**: Enable/disable segmentation (boolean). Default is `false`.
- **smooth_segmentation**: Segmentation smoothing (boolean). Default is `true`.
- **refine_face_landmarks**: Refine face landmarks (boolean). Default is `false`.
- **min_detection_confidence**: Minimum detection confidence (float). Default is `0.5`.
- **min_tracking_confidence**: Minimum tracking confidence (float). Default is `0.5`.

### 2. landmark_indices

Set the joint points to be used.

- **face**: Face landmarks. An empty array `[]` means not to use.
- **left_hand**: Left hand landmarks. `null` means to use all joint points.
- **right_hand**: Right hand landmarks. `null` means to use all joint points.
- **pose**: Body landmarks. Specify particular joint points by name (e.g., `"LEFT_SHOULDER"`).

### 3. annotate_targets

Set the order of keys to be used. Keys not included in this array will not be used.

Example: `["left_hand", "right_hand", "pose"]`

### Notes

- By appropriately adjusting each configuration item, you can customize MPDriver3's behavior to suit the needs of specific projects or applications.
- After changing settings, it may be necessary to restart the application.
- For detailed information and the latest updates, please refer to the [MPDriver3 GitHub repository](https://github.com/plumiume/MPDriver3).