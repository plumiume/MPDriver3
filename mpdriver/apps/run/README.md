### Lang
[JA](/rm/apps/run/ja.md)  
[CH](/rm/apps/run/ch.md)  

# About

Estimate the joint points of the person in the video, and output either the annotated video, the annotation matrix, or both.

# Help

### Usage
```
mpdriver run <src> [-l | --landmarks <outdir> [<ext>] [optkey=optvalue ...]]
                   [-a | --annotated <outdir> [<ext>] [optkey=optvalue ...]]
                   [-p | --cpu <n_cpu>]
                   [--add-ext <v_ext>]
                   [--config confkey=confvalue]
```

### `--landmark`
Settings for the 2D array of joint points

- `outdir`: Output directory. If it does not exist, it will be created
- `ext`: Output format. ".csv", ".npy" are supported

#### option
- `overwrite=false`: Overwrite
- `normalize=true`: Normalize
- `clip=true`: Clip the values to the range of -1 to 1

### `--annotated`
Settings for annotated videos

- `outdir`: Output directory. If it does not exist, it will be created
- `ext`: Output format. Available if supported by OpenCV

#### option
- `show=false`: Display
- `overwrite=false`: Overwrite
- `fps=25`: Set the output frame rate

### `--cpu`
Use multiprocessing

- `n_cpu`: Number of processes to use

### `--add-ext`
Additional video extension. Register extensions that do not become `video/*` with the mimetype library

- `v_ext`: Describe the extension like `.flv`

### `--config`
Additional configuration. Values ​​set here take precedence over any configuration files.
You can use multiple key-value pairs at the same time.

- `confkey`: The key of the item to set. Same as JSON object reference
- `convvalue`: The value of the setting. Only values ​​that can be parsed into JSON are valid.
