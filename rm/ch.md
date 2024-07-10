## 要求

此系统需要以下内容：

[FFmpeg](https://ffmpeg.org/download.html)

## 安装

目前，MPDriver可以通过以下方式安装：
1. 在Python环境中安装
2. 使用Docker安装

### 1. 安装到Python

```bash
python -m pip install git+ssh://git@github.com/plumiume/MPDriver3.git
## 通过https安装
# python -m pip install git+https://github.com/plumiume/MPDriver3.git
```

或者你可以以开发模式安装

```bash
git clone git@github.com:plumiume/MPDriver3.git MPDriver3
## 通过https安装
# git clone https://github.com/plumiume/MPDriver3.git
cd MPDriver3
python -m pip install -e .
```

### 2. Docker安装

在运行以下命令之前，
你必须在系统中安装[Docker](https://www.docker.com/)。

```shell
git clone git@github.com:plumiume/MPDriver3.git MPDriver3
cd MPDriver3
docker build . -t plumiume/mpdriver3
docker create -it --name mpdriver3-container plumiume/mpdriver3 bash
```

### 检查安装

```bash
mpdriver -h
# 如果不工作：
python -m MPDriver3 -h
```

## 使用方法

```bash
# 将单个视频文件转换为CSV文件
mpdriver run path/to/video.file -l path/to/outdir

# 将目录中的所有视频转换为.npy文件，并输出带注释的视频
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

或在Docker中

```shell
docker start mpdriver3-container
docker attach mpdriver3-container
```

```shell
mpdriver run path/to/video.file --landmark path/to/outdir
```

有关run参数的更多信息，请参见[MPDriver.run](mpdriver/apps/run/README.md)
