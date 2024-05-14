## インストール

```bash
python -m pip install git+ssh://git@github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
##  httpsでのインストール
# python -m pip install git+https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
```

または、開発モードでインストールすることもできます

```bash
git clone git@github.com:Kimura-Lab-NIT-Toyota/MPDriver3.git MPDriver3
## httpsでのインストール
# git clone https://github.com/Kimura-Lab-NIT-Toyota/MPDriver3.git
cd MPDriver3
python -m pip install -e 。
```

### インストールを確認する

```bash
mpdriver -h
# 動作しない場合:
Python -m MPDriver -h
```

## 使用法

```bash
# 単一のビデオ ファイルを CSV ファイルに変換します。
mpdriver run path/to/video.file -l path/to/outdir

# ディレクトリ内のすべてのビデオを .npy ファイルに保存し、注釈付きビデオも出力します。
mpdriver run path/to/video_dir -a path/to/annotated_dir -l path/to/outdir .npy
```

run の引数の詳細については、[MPDriver.run](mpdriver/apps/run/README.md) を参照してください。