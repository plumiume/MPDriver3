# Copyright 2024 The MPDriver3 Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

HELP = {
    'apps.run.args:src': '入力として利用する動画ファイルまたは連続画像ディレクトリ',
    'apps.run.args:annotated_options_title': 'アノテーション出力',
    'apps.run.args:annotated_options_dst': 'アノテーション出力ディレクトリ',
    'apps.run.args:annotated_options_ext': 'アノテーション出力の拡張子',
    'apps.run.args:annotated_options_show': '表示する ({default})',
    'apps.run.args:annotated_options_overwirte': '上書きする ({default})',
    'apps.run.args:annotated_options_fps': '出力のフレームレート ({default})',
    'apps.run.args:annotated_options_draw_lm': 'ランドマークの描画 ({default})',
    'apps.run.args:annotated_options_draw_conn': 'ボーンの表示 ({default})',
    'apps.run.args.annotated_options_fourcc': 'FOURCC文字列 ({default})',
    'apps.run.args:annotated_options_mask_face': '顔のマスキング ({default})',
    'apps.run.args:landmarks_options_title': 'ランドマーク出力',
    'apps.run.args:landmarks_options_dst': 'アノテーション出力ディレクトリ',
    'apps.run.args:landmarks_options_ext': 'ランドマーク出力の拡張子',
    'apps.run.args:landmarks_options_overwrite': '上書きする ({default})',
    'apps.run.args:landmarks_options_normalize': '正規化する ({default})',
    'apps.run.args:landmarks_options_clip': '値を -1 ~ 1 の範囲にする ({default})',
    'apps.run.args:landmarks_options_header_0': '.csvのヘッダをつける ({default})',
    'apps.run.args:landmarks_options_header_1': 'ヘッダー行を表す # が先頭に付加されます',
    'apps.run.args:cpu': 'マルチプロセスの数を設定する．指定しない場合はシングルプロセスで動作します',
    'apps.run.args:add_ext': '入力動画ファイルの追加の拡張子．',
    'apps.run.args:config': '追加の設定．[confkey]=[confvalue]で設定ファイルの内容を上書きできます',
}
