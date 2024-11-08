## MPDriver3 設定ファイル README

このREADMEでは、MPDriver3の設定ファイルの各項目について詳細に解説します。

### 1. holistic

MediaPipe Holisticモデルの設定を行います。

- **static_image_mode**: 静止画像モードの有効/無効（boolean）。デフォルトは`false`。
- **model_complexity**: モデルの複雑さ（0, 1, 2）。デフォルトは`1`。
- **smooth_landmarks**: ランドマークの平滑化（boolean）。デフォルトは`true`。
- **enable_segmentation**: セグメンテーションの有効/無効（boolean）。デフォルトは`false`。
- **smooth_segmentation**: セグメンテーションの平滑化（boolean）。デフォルトは`true`。
- **refine_face_landmarks**: 顔のランドマークの精緻化（boolean）。デフォルトは`false`。
- **min_detection_confidence**: 検出の最小信頼度（float）。デフォルトは`0.5`。
- **min_tracking_confidence**: トラッキングの最小信頼度（float）。デフォルトは`0.5`。

### 2. landmark_indices

使用する関節点を設定します。

- **face**: 顔のランドマーク。空の配列`[]`は使用しないことを意味します。
- **left_hand**: 左手のランドマーク。`null`はすべての関節点を使用することを意味します。
- **right_hand**: 右手のランドマーク。`null`はすべての関節点を使用することを意味します。
- **pose**: 体のランドマーク。特定の関節点を名前で指定します（例：`"LEFT_SHOULDER"`）。

### 3. annotate_targets

使用するキーの順序を設定します。この配列に含まれないキーは使用されません。

例：`["left_hand", "right_hand", "pose"]`

### 注意事項

- 各設定項目を適切に調整することで、特定のプロジェクトやアプリケーションのニーズに合わせてMPDriver3の動作をカスタマイズできます。
- 設定の変更後は、アプリケーションの再起動が必要な場合があります。
- 詳細な情報や最新の更新については、[MPDriver3のGitHubリポジトリ](https://github.com/plumiume/MPDriver3)を参照してください。