## MPDriver3 配置文件说明

本说明详细解释了 MPDriver3 配置文件中的每个项目。

### 1. holistic

配置 MediaPipe Holistic 模型设置。

- **static_image_mode**：启用/禁用静态图像模式（布尔值）。默认为 `false`。
- **model_complexity**：模型复杂度（0、1、2）。默认为 `1`。
- **smooth_landmarks**：关键点平滑（布尔值）。默认为 `true`。
- **enable_segmentation**：启用/禁用分割（布尔值）。默认为 `false`。
- **smooth_segmentation**：分割平滑（布尔值）。默认为 `true`。
- **refine_face_landmarks**：细化面部关键点（布尔值）。默认为 `false`。
- **min_detection_confidence**：最小检测置信度（浮点数）。默认为 `0.5`。
- **min_tracking_confidence**：最小跟踪置信度（浮点数）。默认为 `0.5`。

### 2. landmark_indices

设置要使用的关节点。

- **face**：面部关键点。空数组 `[]` 表示不使用。
- **left_hand**：左手关键点。`null` 表示使用所有关节点。
- **right_hand**：右手关键点。`null` 表示使用所有关节点。
- **pose**：身体关键点。通过名称指定特定关节点（例如：`"LEFT_SHOULDER"`）。

### 3. annotate_targets

设置要使用的键的顺序。不包含在此数组中的键将不会被使用。

示例：`["left_hand", "right_hand", "pose"]`

### 注意事项

- 通过适当调整每个配置项，您可以自定义 MPDriver3 的行为以适应特定项目或应用程序的需求。
- 更改设置后，可能需要重新启动应用程序。
- 有关详细信息和最新更新，请参阅 [MPDriver3 GitHub 仓库](https://github.com/plumiume/MPDriver3)。