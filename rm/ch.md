## 必要条件

该系统需要以下组件：

[FFmpeg](https://ffmpeg.org/download.html)

## 安装

目前，MPDriver 可以通过以下方式安装：
1. 在 Python 环境中安装
2. 使用 Docker 安装

### 1. Python 环境中的安装

```bash
python -m pip install git+ssh://git@github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
## 通过 https 安装
# python -m pip install git+https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
```

或者，你也可以以开发模式进行安装。

```bash
git clone git@github.com:Kimura-Lab-NIT-Toyota/MPDriver3.git MPDriver3
## 通过 https 克隆
# git clone https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
cd MPDriver3
python -m pip install -e .
```

### 2. 使用 Docker 安装

在执行以下命令之前，你需要在系统中安装 [Docker](https://www.docker.com/ja-jp/)。

```shell
git clone git@github.com:Kimura-Lab-NIT-Toyota/MPDriver3.git MPDriver3
cd MPDriver3
docker build . -t kimura-lab-nit-toyota/mpdriver3
docker create -it --name mpdriver3-container kimura-lab-nit-toyota/mpdriver3 bash
```

### 检查安装

```bash
mpdriver -h
# 如果不工作：
python -m MPDriver3 -h
```

## 使用方法

```bash
# 将单个视频文件转换为 CSV 文件。
mpdriver run path/to/video.file -l path/to/outdir

# 将目录中的所有视频转换为 .npy 文件，并输出带注释的视频。
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

或者在 Docker 中

```shell
docker start mpdriver3-container
docker attach mpdriver3-container
```
```shell
mpdriver run path/to/video.file --landmark path/to/outdir
```

有关 `run` 参数的更多信息，请参见 `[MPDriver.run](mpdriver/apps/run/README.md)`。
