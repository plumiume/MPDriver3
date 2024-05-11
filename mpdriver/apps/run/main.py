import os
from pathlib import Path
from itertools import *
from typing import *
import mimetypes
# from threading import RLock
from multiprocessing.synchronize import RLock

import numpy as np
import cv2

from mpdriver.core.mp import MediaPipeHolisticOptions

from ...utils import is_video, is_image, VideoCapture, VideoWriter, cap_to_frame_iter, video_or_imgdir_pathes
from ...core.mp import MP, MediaPipeHolisticOptions
from ...core.main_base import AppBase, AppWorkerThread, AppExecutor, PROGRESS_DESC_PREFIX
from ...core.progress import TqdmKwargs
from ...core.config import load_config

from .args import RunArgs

class RunApp(AppBase):

    def __init__(self):
        holistic_options: MediaPipeHolisticOptions = load_config('mediapipe')

        self.mp = MP(
            detect_targets = ["left_hand", "right_hand", "pose"],
            holistic_options = holistic_options
        )

    def run(
        self,
        src: Path,
        annotated: Path | None = None,
        landmarks: Path | None = None,
        show_annotated: bool = False,
        fps: float = 30,
        normalize_clip: bool = True,
        tqdm_kwds: TqdmKwargs = {},
        rlock: RLock | None = None,
        src_str_len: int | None = None
        ):

        str_src = src.as_posix()
        imshow_winname = str(id(self))
        stem_ext = None if annotated is None else annotated.name

        tqdm_handler = AppWorkerThread.get_thread().tqdm_handler

        # if is_video(src):
        if src.is_file():

            cap = VideoCapture(str_src)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # TODO add AV1 support
            # fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            fourcc = VideoWriter.fourcc(*"mp4v")
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            frame_iter = cap_to_frame_iter(cap, end=total)

        else:

            img_pathes = list(p for p in src.iterdir() if is_image(p))
            total = len(img_pathes)
            fourcc = VideoWriter.fourcc(*"mp4v")
            # fps = fps
            img_iter = (cv2.imread(f.as_posix(), cv2.IMREAD_COLOR) for f in img_pathes)
            if (f0 := next(img_iter, None)) is None:
                # raise ValueError
                return
            size = (f0.shape[1], f0.shape[0])
            frame_iter = chain((f0,), img_iter)

        total_str_len = max(4, len(str(total)))

        # np.Mat -> np.Mat, MPD (=MediaPipeDict)
        job = ((f, self.mp.detect(f)) for f in frame_iter) # 姿勢推定

        if annotated is not None or show_annotated:
            # np.Mat, MPD -> MPD, np.Mat
            job = ((mpd, self.mp.annotate(f, mpd)) for f, mpd in job) # 関節点の描画

            if show_annotated:
                # MPD, np.Mat -> MPD, np.Mat
                # （変化しない）
                job = (((mpd, ann), cv2.imshow(imshow_winname, ann), cv2.waitKey(1))[0] for mpd, ann in job) # 描画したものを表示

            if stem_ext and is_video(stem_ext):
                video_writer = VideoWriter(annotated.as_posix(), fourcc, fps, size) # 描画したものを保存（to動画）
                # MPD, np.Mat -> MPD
                job = ((mpd, video_writer.write(ann))[0] for mpd, ann in job)

            elif stem_ext and is_image(stem_ext):
                # MPD, np.Mat -> MPD
                job = (
                    (mpd, cv2.imwrite(
                        (annotated.parent / annotated.stem / f"{{:0{total_str_len}}}{{}}".format(idx, annotated.suffix)),
                        ann
                    ))[0]
                    for idx, (mpd, ann) in enumerate(job)
                ) # 描画したものを保存（to連続画像）
            
            else:
                raise AssertionError("may be unreach")
        
        else:
            # np.Mat, MPD -> MPD
            job = (mpd for f, mpd in job) # イテレータの整形

        # MPD -> np.float
        job = (self.mp.flatten(self.mp.normalize(mpd, clip=normalize_clip)) for mpd in job) # 3次元のフレームを１列に並べる

        src_str_len = 70 if src_str_len is None else src_str_len

        progress = tqdm_handler.tqdm(job, **({
            "total": total, "desc": str_src,
            "bar_format": f"{{desc:{70 if src_str_len is None else src_str_len}}} {{percentage:6.2f}}%|{{bar}}|{{n:{total_str_len}d}}/{{total:{total_str_len}d}}{{postfix}}",
            "priority": 0,
        } | tqdm_kwds)) # プログレスバー

        if landmarks is None:
            for _ in progress: pass # 実行
            del progress
            return

        # check that result is empty 
        if not bool(list_job := list(progress)):
            tqdm_handler.write(f'skip at {src} because it isn\'t detected from src')
            return

        matrix = np.stack(list_job)

        if landmarks.suffix == ".csv": # CSVで出力

            if rlock is not None: rlock.acquire()
            os.makedirs(landmarks.parent, exist_ok=True)
            np.savetxt(landmarks, matrix, delimiter=",")
            if rlock is not None: rlock.release()

        elif landmarks.suffix == ".npy": # NumPy.npy形式で出力

            if rlock is not None: rlock.acquire()
            os.makedirs(landmarks.parent, exist_ok=True)
            np.save(landmarks, matrix)
            if rlock is not None: rlock.release()

        del job
        return

class RunExecutor(AppExecutor[RunApp]): # 子プロセス上の実行クラス
    app_type = RunApp # AppExecutor で使用するので，必ず app_type を設定

def app_main(ns: RunArgs): # アプリケーションのコマンドラインツール用エントリーポイント

    executor = RunExecutor(ns.cpu)

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
            else:                          # 関節店の出力あり
                landmarks = (ns.landmarks[0][0] / ns.src.name).with_suffix(ns.landmarks[0][1])
                if not ns.landmarks[1]["overwrite"] and landmarks.exists():
                    landmarks = None

            if annotated is None and landmarks is None and not ns.annotated[1]["show"]:
                # mediapipeの姿勢推定が必要ない状態
                return

            yield ((
                ns.src,
                annotated,
                landmarks,
                ns.annotated[1]["show"],
                ns.annotated[1]["fps"],
                ns.landmarks[1]["clip"]
            ), {})
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

            yield ((
                ns.src / src_related,
                annotated,
                landmarks,
                ns.annotated[1]["show"],
                ns.annotated[1]["fps"],
                ns.landmarks[1]["clip"]
            ), {})

    args_kwargs_list = list(executor._tqdm_func(
        args_kwargs_iter(),
        desc = f'\033[46m{PROGRESS_DESC_PREFIX.format("Searching...")}\033[0m',
        priority=1
    )) # ファイルを探索

    # プログレスバーに表示する入力ファイルのパスの最大文字長を取得 -> 0埋め用
    src_str_len = max((len(item[0][0].as_posix()) for item in args_kwargs_list), default=None)
    for item in args_kwargs_list:
        item[1]['src_str_len'] = src_str_len

    # アプリケーションを実行
    executor.execute(args_kwargs_list)
