## 必要条件

このシステムには以下が必要です：

[FFmpeg](https://ffmpeg.org/download.html)

## インストール

現在、MPDriverは以下の方法でインストールできます：
1. Python環境にインストール
2. Dockerを使用してインストール

### 1. Pythonにインストール

```bash
python -m pip install git+ssh://git@github.com/plumiume/MPDriver3.git
## https経由でインストール
# python -m pip install git+https://github.com/plumiume/MPDriver3.git
```

または、開発モードでインストールすることもできます

```bash
git clone git@github.com:plumiume/MPDriver3.git MPDriver3
## https経由でインストール
# git clone https://github.com/plumiume/MPDriver3.git
cd MPDriver3
python -m pip install -e .
```

### 2. Dockerにインストール

以下のコマンドを実行する前に、
システムに[Docker](https://www.docker.com/)がインストールされている必要があります。

```shell
git clone git@github.com:plumiume/MPDriver3.git MPDriver3
cd MPDriver3
docker build . -t plumiume/mpdriver3
docker create -it --name mpdriver3-container plumiume/mpdriver3 bash
```

### インストール確認

```bash
mpdriver -h
# 動作しない場合：
python -m MPDriver3 -h
```

## 使用方法

```bash
# 単一のビデオファイルをCSVファイルに変換
mpdriver run path/to/video.file -l path/to/outdir

# ディレクトリ内のすべてのビデオを.npyファイルに変換し、注釈付きビデオも出力
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

またはDockerで

```shell
docker start mpdriver3-container
docker attach mpdriver3-container
```

```shell
mpdriver run path/to/video.file --landmark path/to/outdir
```

runの引数についての詳細は[MPDriver.run](mpdriver/apps/run/README.md)を参照してください