### Lang
- [JP](/rm/jp.md)
- [CH](/rm/ch.md)

## Requirments

This system requires the following:

[FFmpeg](https://ffmpeg.org/download.html)

## Instllation

Currently, MPDriver can be installed in the following ways:
1. Installation in a Python environment
2. Installation using Docker

### 1. install to python

```bash
python -m pip install git+ssh://git@github.com/plumiume/MPDriver3.git
## Install via https
# python -m pip install git+https://github.com/plumiume/MPDriver3.git
```

Or you can install in development mode

```bash
git clone git@github.com:plumiume/MPDriver3.git MPDriver3
## Install via https
# git clone https://github.com/plumiume/MPDriver3.git
cd MPDriver3
python -m pip install -e .
```

### 2. docker install

Before running the following commands,
you must have [Docker](https://www.docker.com/) installed on your system.

```shell
git clone git@github.com:plumiume/MPDriver3.git MPDriver3
cd MPDriver3
docker build . -t plumiume/mpdriver3:latest
# please visit https://hub.docker.com/repository/docker/plumiiume/mpdriver3
# and pull image plumiume/mpdriver3
```

### Check Installation

```bash
mpdriver -h
# if not work:
python -m MPDriver3 -h
```

## Usage

```bash
# Single video file to CSV file.
mpdriver run path/to/video.file -l path/to/outdir

# All videos in the directory to .npy files and also output annotated videos.
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

or in Docker

```shell
docker run --rm -it plumiume/mpdriver3:latest mpdriver run path/to/video.file --landmark path/to/outdir
```

See [MPDriver.run](mpdriver/apps/run/README.md) for more information about run's arguments
