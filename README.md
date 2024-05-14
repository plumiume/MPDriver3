### Lang
- [JP](/rm/jp.md)

## Instllation

```bash
python -m pip install git+ssh://git@github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
## Install via https
# python -m pip install git+https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
```

Or you can install in development mode

```bash
git clone git@github.com:Kimura-Lab-NIT-Toyota/MPDriver3.git MPDriver3
## Install via https
# git clone https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
cd MPDriver3
python -m pip install -e .
```

### Check Installation

```bash
mpdriver -h
# if not work:
python -m MPDriver -h
```

## Usage

```bash
# Single video file to CSV file.
mpdriver run path/to/video.file -l path/to/outdir

# All videos in the directory to .npy files and also output annotated videos.
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

See [MPDriver.run](mpdriver/apps/run/README.md) for more information about run's arguments
