# 新しいアプリの追加

新しいアプリを追加するには，
[mpdriver/apps](.)ディレクトリ以下に任意の名前でディレクトリを作成します．
また，作成したディレクトリに `args.py`, `main.py` ファイルを作成します．

ディレクトリ構造は以下のようになります．
```
mpdriver/apps/
├─ new_app/
│  ├─ args.py
│  ├─ main.py
:  :

```

#### Note:

`args.py`, `main.py` はディレクトリで代用できます

## `args.py`

ここにはコマンドライン解析用のコードを設置します

[`argparse`](https://docs.python.org/ja/3/library/argparse.html)を使用して，既存のコマンドラインに追加でアプリのコマンドを追加できます．以下はその例です．

```python
from ...core.args_base import argparse, subparsers, help_action, HelpFormatter

## command name
command = "newapp"
## or use dirname
#command = Path(__file__).parent.name

## add command to existing command line system
parser = subparser.add_parser(command, add_help=False, formatter_class=HelpFormatter)

## add default for import newapp
parser.set_defaults(command=command)

## set MPDriver's help
parser._add_help(help_action)

## for example
parser.add_argument("-v", "--verbose", action=argparse._StoreTrueAction)

...

```

#### Warning:

`args.py` に，ロードに時間のかかるモジュールをインポートしないでください．
ヘルプの表示 `mpdriver -h` (または `mpdriver <command> -h`) に毎回時間がかかるようになります．

## `main.py`

ここにはアプリの実体コードを配置します．

アプリのエントリポイントとして，`argparse.Namespace`を引数に持つ`main`関数を作成します．

```python
def main(namespace: MyAppArgs):
    ## something to do
    pass
    # return None
```
