# About

動画に映る人物の関節点を推定し，アノテーションされた動画，アノテーションマトリックスのどちらかまたは両方を出力する

# Help

### Usage
```
mpdriver run <src> [-l | --landmarks <outdir> [<ext>] [optkey=optvalue ...]]
                   [-a | --annotated <outdir> [<ext>] [optkey=optvalue ...]]
```

#### landmarks option
- `overwrite`: 上書きする
- `normalize`: 正規化する
- `clip`:  値を -1 ~ 1 の範囲に切り抜く

### annotated option
- `show`: 表示する
- `overwrite`: 上書きする
- `fps=<fps_value>`: 出力のフレームレートを設定する


