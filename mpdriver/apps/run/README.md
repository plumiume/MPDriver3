# About

動画に映る人物の関節点を推定し，アノテーションされた動画，アノテーションマトリックスのどちらかまたは両方を出力する

# Help

### Usage
```
mpdriver run <src> [-l | --landmarks <outdir> [<ext>] [optkey=optvalue ...]]
                   [-a | --annotated <outdir> [<ext>] [optkey=optvalue ...]]
                   [-p | --cpu <n_cpu>]
                   [--add-ext <v_ext>]
```

### `--landmark`
関節点の２次元配列についての設定

- `outdir`: 出力先のディレクトリ．もし存在しないなら作成される
- `ext`: 出力形式．".csv", ".npy"がサポート

#### option
- `overwrite=false`: 上書きする
- `normalize=true`: 正規化する
- `clip=true`:  値を -1 ~ 1 の範囲に切り抜く

### `--annotated`
アノテーションされた動画についての設定

- `outdir`: 出力先のディレクトリ．もし存在しないなら作成される
- `ext`: 出力形式．OpenCVが対応する出力なら利用可能

#### option
- `show=false`: 表示する
- `overwrite=false`: 上書きする
- `fps=25`: 出力のフレームレートを設定する

### `--cpu`
マルチプロセスを使用

- `n_cpu`: 使用するプロセス数

### `--add-ext`
追加のビデオ拡張子 mimetypeライブラリでvideo/*とならない拡張子は登録してください

- `v_ext`: 拡張子 `.flv` のように記述
