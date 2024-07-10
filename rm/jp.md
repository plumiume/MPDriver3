## 必要条件

このシステムには以下が必要です：

[FFmpeg](https://ffmpeg.org/download.html)

## インストール

現在、MPDriverは以下の方法でインストールできます：
1. Python環境へのインストール
2. Dockerを使用したインストール

### 1. Pythonへのインストール

```bash
python -m pip install git+ssh://git@github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
## https経由でのインストール
# python -m pip install git+https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
```

または、開発モードでインストールすることもできます。

```bash
git clone git@github.com:Kimura-Lab-NIT-Toyota/MPDriver3.git MPDriver3
## https経由でのクローン
# git clone https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
cd MPDriver3
python -m pip install -e .
```

### 2. Dockerによるインストール

以下のコマンドを実行する前に、システムに [Docker](https://www.docker.com/ja-jp/) がインストールされている必要があります。

```shell
git clone git@github.com:Kimura-Lab-NIT-Toyota/MPDriver3.git MPDriver3
cd MPDriver3
docker build . -t kimura-lab-nit-toyota/mpdriver3
docker create -it --name mpdriver3-container kimura-lab-nit-toyota/mpdriver3 bash
```

### インストール確認

```bash
mpdriver -h
# 動作しない場合：
python -m MPDriver3 -h
```

## 使用方法

```bash
# 単一の動画ファイルをCSVファイルに変換します。
mpdriver run path/to/video.file -l path/to/outdir

# ディレクトリ内のすべての動画を .npy ファイルに変換し、注釈付き動画も出力します。
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

またはDocker内で

```shell
docker start mpdriver3-container
docker attach mpdriver3-container
```
```shell
mpdriver run path/to/video.file --landmark path/to/outdir
```

[MPDriver.run](mpdriver/apps/run/README.md) で、`run` の引数についての詳細情報をご覧ください。
