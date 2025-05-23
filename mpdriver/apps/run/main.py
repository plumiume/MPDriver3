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

import os
import shutil
from pathlib import Path
from itertools import *
from typing import *
import json
import tempfile
import mimetypes
import unicodedata
from multiprocessing.synchronize import RLock

import numpy as np
import cv2

from ...utils import FOURCC, VideoCapture, VideoWriter, VideoWriter_fourcc
from ...utils import is_image, is_video, cap_to_frame_iter, video_or_imgdir_pathes
from ...core.config import decompose_keys
from ...core.main_base import AppBase, AppWorkerThread, AppExecutor, PROGRESS_DESC_PREFIX
from ...core.progress import TqdmKwargs

from ...engine.mediapipe import MP, mediapipe_config

from .args import RunArgs

os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

class RunApp(AppBase):

    def __init__(
        self,
        config: list[tuple[str, str]] = []
        ):

        # Apply additional configuration
        for ck, cv in config:
            cfile, *keys = ck.split('.')
            if cfile != 'mediapipe':
                continue
            obj_prev, obj_temp, k = decompose_keys(mediapipe_config, keys)
            obj_prev[k] = json.loads(cv)

        self.mp = MP()

    def __del__(self):
        try:
            shutil.rmtree(self.tmpdir)
        except:
            pass

    def run(
        self,
        src: Path,
        annotated: Path | None = None,
        landmarks: Path | None = None,
        show_annotated: bool = False,
        fps: float = 30,
        f_draw_lm: bool = True, 
        f_draw_conn: bool = True, 
        f_mask_face: bool = False, 
        fourcc: str | None = None,
        f_normalize: bool = True, 
        f_clip: bool = True, 
        f_flat: bool = True,
        f_header: bool = False, 
        tqdm_kwds: TqdmKwargs = {},
        rlock: RLock | None = None,
        src_str_len: int | None = None
        ):
        """
        This method processes the input source (video or image sequence) to perform pose estimation
        using MediaPipe. It can annotate the frames, save the results, and output landmarks in CSV
        or NPY format. The method supports progress tracking and handles various configurations
        for annotation and landmark extraction.

        Args:
                src (Path): The input source, either a video file or a directory containing images.
                annotated (Path | None): The path to save the annotated output. If None, no annotation is saved.
                landmarks (Path | None): The path to save the landmarks. If None, no landmarks are saved.
                show_annotated (bool): Whether to display the annotated frames.
                fps (float): Frames per second for the output video.
                f_draw_lm (bool): Whether to draw landmarks on the frames.
                f_draw_conn (bool): Whether to draw connections between landmarks.
                f_mask_face (bool): Whether to mask the face in the annotation.
                fourcc (str | None): FourCC code for video encoding. If None, default is used.
                f_normalize (bool): Whether to normalize the landmarks.
                f_clip (bool): Whether to clip the landmarks.
                f_flat (bool): Whether to flatten the landmark matrix.
                f_header (bool): Whether to include header in CSV output.
                tqdm_kwds (TqdmKwargs): Additional arguments for tqdm progress bar.
                rlock (RLock | None): A lock for thread safety when writing files.
                src_str_len (int | None): Length of the source string for progress bar formatting.
        """

        str_src = src.as_posix()
        imshow_winname = str(id(self))
        stem_ext = None if annotated is None else annotated.name

        current_thread = AppWorkerThread.get_thread()
        tqdm_handler = current_thread.tqdm_handler

        # if is_video(src):
        if src.is_file():

            cap = VideoCapture(str_src)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fourcc = VideoWriter_fourcc(*'h264')
            if annotated is not None:
                if annotated.suffix in FOURCC:
                    fourcc = VideoWriter_fourcc(*FOURCC[annotated.suffix])
                else:
                    print('WARNNING:', f'annotated .ext \'{annotated.suffix}\' is invalid. use \'.mp4\'')
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            frame_iter = cap_to_frame_iter(cap, end=total)

        # elif is_frame_sequence(src):
        else:

            img_pathes = list(p for p in src.iterdir() if is_image(p))
            total = len(img_pathes)
            fourcc = VideoWriter_fourcc(*'h264')
            if annotated is not None:
                if annotated.suffix in FOURCC:
                    fourcc = VideoWriter_fourcc(*FOURCC[annotated.suffix])
                else:
                    print('WARNNING:', f'annotated .ext \'{annotated.suffix}\' is invalid. use \'.mp4\'')
            # fps = fps
            img_iter = (cv2.imread(f.as_posix(), cv2.IMREAD_COLOR) for f in img_pathes)
            if (f0 := next(img_iter, None)) is None:
                # raise ValueError
                return
            size = (f0.shape[1], f0.shape[0])
            frame_iter = chain((f0,), img_iter)

        total_str_len = max(4, len(str(total)))
        on_completed_tasks = list[Callable[[], None]]()

        # np.Mat -> np.Mat, MPD (=MediaPipeDict)
        tasks = ((f, self.mp.detect(f)) for f in frame_iter) # 姿勢推定

        if annotated is not None or show_annotated: # 描画する場合
            # np.Mat, MPD -> MPD, np.Mat
            tasks = ((mpd, self.mp.annotate(f, mpd, f_draw_conn, f_draw_lm, f_mask_face)) for f, mpd in tasks) # 関節点の描画

            if show_annotated:
                # MPD, np.Mat -> MPD, np.Mat
                # （変化しない）
                tasks = (((mpd, ann), cv2.imshow(imshow_winname, ann), cv2.waitKey(1))[0] for mpd, ann in tasks) # 描画したものを表示

            if annotated is None: # 描画を保存しない
                # Nothing to do
                # MPD, np.Mat -> MPD
                tasks = (mpd for mpd, ann in tasks)

            elif stem_ext and is_video(stem_ext): # 描画を動画で保存する場合
                tmp_video = (self.tmpdir / f'{hash(annotated)}.{annotated.suffix}').as_posix()
                video_writer = VideoWriter(tmp_video, fourcc, fps, size) # 描画したものを保存（to動画）
                # MPD, np.Mat -> MPD
                tasks = ((mpd, video_writer.write(ann))[0] for mpd, ann in tasks)
                def release_video():
                    video_writer.release()
                    shutil.copy(tmp_video, annotated.as_posix())
                    os.remove(tmp_video)
                on_completed_tasks.append(release_video)

            elif stem_ext and is_image(stem_ext): # 描画を連続画像で保存する場合
                # MPD, np.Mat -> MPD
                tasks = (
                    (mpd, cv2.imwrite(
                        (annotated.parent / annotated.stem / f"{{:0{total_str_len}}}{{}}".format(idx, annotated.suffix)),
                        ann
                    ))[0]
                    for idx, (mpd, ann) in enumerate(tasks)
                ) # 描画したものを保存（to連続画像）

            else:
                raise AssertionError(f"may be unreach (type of stem_ext '({stem_ext}: {stem_ext.__class__})')")

        else:
            # np.Mat, MPD -> MPD
            tasks = (mpd for f, mpd in tasks) # イテレータの整形


        # normalize and clip
        if f_normalize:
            # MPD -> MPD
            tasks = (self.mp.normalize(mpd, clip=f_clip) for mpd in tasks)

        # flatten
        if f_flat:
            # MPD -> np.float
            tasks = (self.mp.flatten(mpd) for mpd in tasks)
        else:
            # MPD -> np.float
            tasks = (self.mp.flatten(mpd, as_3d=True) for mpd in tasks)

        # 表示する文字幅を設定
        src_str_len = 70 if src_str_len is None else src_str_len

        tasks = tqdm_handler.tqdm(tasks, **({
            "total": total, "desc": str_src,
            "bar_format": (
                f"{{desc:{70 if src_str_len is None else src_str_len}}} "
                f"{{percentage:6.2f}}%|"
                f"{{bar}}|"
                f"{{n:{total_str_len}d}}/{{total:{total_str_len}d}}|"
                f"{{rate_fmt}}{{postfix}}"
            ),
            "priority": 0,
            "unit": "f"
        } | tqdm_kwds)) # プログレスバー

        if landmarks is None: # 関節点の出力なし
            for _ in tasks: pass # 実行
            tasks.update(total - tasks.last_print_n)
            del tasks
            return

        # Check that result is empty 
        if not bool(matrix := list(tasks)):
            tqdm_handler.write(f'skip at {src} because it isn\'t detected from src')
            return
        tasks.update(total - tasks.last_print_n)
        del tasks

        # Execute all on_completed_tasks
        for task in on_completed_tasks:
            task()

        matrix = np.stack(matrix)

        if landmarks.suffix == ".csv": # CSVで出力

            header = self.mp.get_header() if f_header else ""

            if matrix.ndim != 2:
                raise ValueError(f"matrix.ndim != 2 ({matrix.ndim})")

            if rlock is not None: rlock.acquire()
            os.makedirs(landmarks.parent, exist_ok=True)
            np.savetxt(landmarks, matrix, delimiter=",", header=header)
            if rlock is not None: rlock.release()

        elif landmarks.suffix == ".npy": # NumPy.npy形式で出力

            if rlock is not None: rlock.acquire()
            os.makedirs(landmarks.parent, exist_ok=True)
            np.save(landmarks, matrix)
            if rlock is not None: rlock.release()

        return

class RunExecutor(AppExecutor[RunApp]): # 子プロセス上の実行クラス
    app_type = RunApp # AppExecutor で使用するので，必ず app_type を設定

def app_main(ns: RunArgs): # アプリケーションのコマンドラインツール用エントリーポイント

    config = tuple(ns.config)

    if ns.template is not None:
        config

    executor = RunExecutor(ns.cpu, (ns.config,))

    for ext in ns.add_ext:
        if ext.startswith('.'):
            ext = ext[1:]
        mimetypes.add_type(f'video/{ext}', f'.{ext}')

    def args_kwargs_iter() -> Iterator[tuple[tuple[Path, Path | None, Path | None, bool, float, bool], dict]]:

        if is_video(ns.src): # src が単一ファイル

            if ns.annotated[0][0] is None: # 描画なし
                annotated = None
            else:                          # 描画あり
                annotated = (ns.annotated[0][0] / ns.src.name).with_suffix(ns.annotated[0][1])
                if not ns.annotated[1]["overwrite"] and annotated.exists():
                    annotated = None

            if ns.landmarks[0][0] is None: # 関節点の出力なし
                landmarks = None
            else:                          # 関節点の出力あり
                landmarks = (ns.landmarks[0][0] / ns.src.name).with_suffix(ns.landmarks[0][1])
                if not ns.landmarks[1]["overwrite"] and landmarks.exists():
                    landmarks = None

            if annotated is None and landmarks is None and not ns.annotated[1]["show"]:
                # mediapipeの姿勢推定が必要ない状態
                return

            yield (
                (
                    ns.src # src: Path,
                ),
                {
                    'annotated': annotated,  # annotated: Path | None = None,
                    'landmarks': landmarks,  # landmarks: Path | None = None,
                    'show_annotated': ns.annotated[1]["show"],  # show_annotated: bool = False,
                    'fps': ns.annotated[1]["fps"],  # fps: float = 30,
                    'f_draw_lm': ns.annotated[1]["draw_lm"],  # f_draw_lm: bool = True,
                    'f_draw_conn': ns.annotated[1]["draw_conn"],  # f_draw_conn: bool = True,
                    'f_mask_face': ns.annotated[1]["mask_face"],  # f_mask_face: bool = False,
                    'fourcc': ns.annotated[1]["fourcc"],  # fourcc: str | None = None,
                    'f_normalize': ns.landmarks[1]["normalize"],  # f_normalize: bool = True,
                    'f_clip': ns.landmarks[1]["clip"],  # f_clip: bool = True,
                    'f_flat': ns.landmarks[1]["flat"],  # f_flat: bool = True,
                    'f_header': ns.landmarks[1]["header"],  # f_header: bool = False,
                    # tqdm_kwds: TqdmKwargs = {},
                    # rlock: RLock | None = None,
                    # src_str_len: int | None = None
                }
            
            )
            return

        for src in video_or_imgdir_pathes(ns.src): # src がディレクトリ

            src_related = src.relative_to(ns.src)

            if ns.annotated[0][0] is None: # 描画なし
                annotated = None
            else:                          # 描画あり
                annotated = (ns.annotated[0][0] / src_related).with_suffix(ns.annotated[0][1])
                if not ns.annotated[1]["overwrite"] and annotated.exists():
                    annotated = None

            if ns.landmarks[0][0] is None: # 関節点の出力なし
                landmarks = None
            else:                          # 関節点の出力あり
                landmarks = (ns.landmarks[0][0] / src_related).with_suffix(ns.landmarks[0][1])
                if not ns.landmarks[1]["overwrite"] and landmarks.exists():
                    landmarks = None

            if annotated is None and landmarks is None and not ns.annotated[1]["show"]:
                # mediapipeの姿勢推定が必要ない状態
                continue

            yield (
                (
                    ns.src / src_related,  # src: Path,
                ),
                {
                    'annotated': annotated,  # annotated: Path | None = None,
                    'landmarks': landmarks,  # landmarks: Path | None = None,
                    'show_annotated': ns.annotated[1]["show"],  # show_annotated: bool = False,
                    'fps': ns.annotated[1]["fps"],  # fps: float = 30,
                    'f_draw_lm': ns.annotated[1]["draw_lm"],  # f_draw_lm: bool = True,
                    'f_draw_conn': ns.annotated[1]["draw_conn"],  # f_draw_conn: bool = True,
                    'f_mask_face': ns.annotated[1]["mask_face"],  # f_mask_face: bool = False,
                    'fourcc': ns.annotated[1]["fourcc"],  # fourcc: str | None = None,
                    'f_normalize': ns.landmarks[1]["normalize"],  # f_normalize: bool = True,
                    'f_clip': ns.landmarks[1]["clip"],  # f_clip: bool = True,
                    'f_flat': ns.landmarks[1]["flat"],  # f_flat: bool = True,
                    'f_header': ns.landmarks[1]["header"],  # f_header: bool = False,
                    # tqdm_kwds: TqdmKwargs = {},
                    # rlock: RLock | None = None,
                    # src_str_len: int | None = None
                }
            )

    args_kwargs_list = list(executor._tqdm_func(
        args_kwargs_iter(),
        desc = f'\033[46m{PROGRESS_DESC_PREFIX.format("Searching...")}\033[0m',
        priority=1
    )) # ファイルを探索

    # プログレスバーに表示する入力ファイルのパスの最大文字長を取得 -> 0埋め用
    src_str_len = max(
        (
            sum(
                2 if unicodedata.east_asian_width(c) in "FWA" else 1
                for c in item[0][0].as_posix()
            )
            for item in args_kwargs_list
        ),
        default=None
    )

    for item in args_kwargs_list:
        item[1]['src_str_len'] = src_str_len

    # アプリケーションを実行
    executor.execute(args_kwargs_list)
