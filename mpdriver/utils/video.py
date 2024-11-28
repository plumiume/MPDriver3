from pathlib import Path
from itertools import count, chain
from typing import overload, TypeAlias, Iterable, Iterator, TypedDict, Literal, Callable
from typing_extensions import Self
import mimetypes
import cv2

PathLike = str | Path

FOURCC = {
    '.avi': 'xvid',
    '.mov': 'mp4v',
    '.mp4': 'h264',
}

class VideoCapture:
  @overload
  def __init__(self, filename: str, api_preference: int = ...): ...
  @overload
  def __init__(self, index: int, api_preference: int = ...): ...
  def get(self, prod_id: int) -> any: ...
  def getBackendName(self) -> str: ...
  def getExceptionMode(self) -> bool: ...
  def grab(self) -> bool: ...
  def isOpened(self) -> bool: ...
  @overload
  def open(self, filename: str, api_preference: int = ...) -> bool: ...
  @overload
  def open(self, filename: str, api_preference: int, params: tuple) -> bool: ...
  @overload
  def open(self, index: int, api_preference: int = ...) -> bool: ...
  @overload
  def open(self, index: int, api_preference: int, params: tuple) -> bool: ...
  def read(self, image: cv2.Mat = ...) -> tuple[bool, cv2.Mat]: ...
  def retrieve(self, image: cv2.Mat = ..., flag: int = ...) -> tuple[bool, cv2.Mat]: ...
  def release(self): ...
  def set(self, prod_id: int, value: any) -> bool: ...
  def setExceptionMode(enable: bool): ...
  @classmethod
  def waitAny(cls, streams: any, timeout_ns: int) -> bool: ...
VideoCapture = cv2.VideoCapture
  
FourCC: TypeAlias = int
class VideoWriter:
  @overload
  def __init__(self): ...
  @overload
  def __init__(self, filename: str, fourcc: FourCC, fps: float, frameSize: tuple[int, int], isColor: bool = True): ...
  @overload
  def __init__(self, filename: str, apiPreference: int, fourcc: FourCC, fps: float, frameSize: tuple[int, int], isColor: bool = True): ...
  def get(self, propId: int) -> any: ...
  def set(self, prodId: int, value: any) -> int: ...
  def release(): ...
  def isOpened() -> bool: ...
  def getBackendName() -> str: ...
  @overload
  def open(
    self, filename: str, fourcc: FourCC,
    fps: float, frameSize: tuple[int, int],
    isColor: bool = True
    ): ...
  @overload
  def open(
    self,
    filename: str, apiPreference: int, fourcc: FourCC,
    fps: float, frameSize: tuple[int, int],
    isColor: bool = True
    ): ...
  def write(self, image: cv2.Mat): ...
  @staticmethod
  def fourcc(c1: str, c2: str, c3: str, c4: str) -> FourCC: ...
VideoWriter = cv2.VideoWriter

def VideoWriter_fourcc(a: str, b: str, c: str, d: str) -> int:
    return int(cv2.VideoWriter_fourcc(a, b, c, d))

FFmpegProbeStreamDisposition = dict[
  Literal[
    "default", "dub", "original", "comment", "lyrics", "karaoke",
    "forced", "hearing_impaired", "visual_impaired", "clean_effects",
    "attached_pic", "timed_thumbnails"
  ], int
]
FFmpegProbeStreamTags = dict[Literal["language", "handler_name", "vendor_id"]]

class FFmpegProbeStream(TypedDict):
  index: int
  codec_name: str
  codec_long_name: str
  profile: str
  codec_type: str
  codec_tag_string: str
  codec_tag: str # HEX str
  width: int
  height: int
  coded_width: int
  coded_height: int
  closed_captions: int
  has_b_frames: int
  sample_aspect_ratio: str # w:h
  display_aspect_ratio: str # w:h
  pix_fmt: str
  level: int
  chroma_location: str
  refs: int
  r_frame_rate: str # m/n
  avg_frame_rate: str # m/n
  time_base: str # m/n
  start_pts: int
  start_time: str # float
  duration_ts: int
  bit_rate: str # int
  nb_frames: int
  disposition: FFmpegProbeStreamDisposition
  tags: FFmpegProbeStreamTags

FFmpegProbeFormatTags = dict[
  Literal[
    "major_brand", "minor_version", "compatible_brands", "encoder"
  ]
]

class FFmpegProbeFormat(TypedDict):
  filename: str
  nb_streams: int
  nb_programs: int
  format_name: str # sep=","
  format_long_name: str
  start_time: str # float
  duration: str # float
  size: str # int
  bit_rate: str # int
  probe_score: int
  tags: FFmpegProbeFormatTags

class FFmpegProbe(TypedDict):
  stream: list[FFmpegProbeStream]
  format: FFmpegProbeFormat

class FFmpegStream:
  def asplit(self): ...
  def overwrite_output(self) -> Self: ...
  def colorchannelmixer(self, *streams_and_filename, **kwargs) -> Self: ...
  def crop(self, x: int, y: int, width: int, height: int, **kwargs) -> Self: ...
  def drawbox(
    self,
    x: int = 0, y: int = 0, width: int = 0, height: int = 0,
    color: str = "black", thickness: int = 3,
    **kwargs
    ) -> Self: ...
  def drawtext(
    self,
    text: str = None, x: int = 0, y: int = 0, escape_text: bool = True,
    box: Literal[0, 1] = 0, boxborderw: int = 0, boxcolor: str = "white",
    line_spacing: int = 0, borderw: int = 0, bordercolor: str = "black",
    expansion: Literal["none", "strftime", "normal"] = "normal",
    basetime: int | None = None, fix_bounds: bool = False,
    fontcolor: str = "black", fontcolor_expr: str | None = None,
    font: str = "Sans", fontfile: str | None = None,
    alpha: float = 1., fontsize: int = 16,
    text_shaping: int = 1, ft_load_flags: int = ...,
    shadowcolor: str = "black", shadowx: int = 0, shadowy: int = 0,
    start_number: int = 0, tabsize: int = 4,
    timecode: str = "hh:mm:ss[:;.]ff",
    rate = ..., timecode_rate = ..., r = ...,
    tc24hmax: Literal[0, 1] = 0,
    reload: Literal[0, 1] = 0,
    **kwargs
    ) -> Self: ...
  def hflip(self) -> Self: ...
  def hue(
    self,
    h: float = 0., s: float = 1., H: float = 0., b: float = 0.,
    **kwargs
    ) -> Self: ...
  def setpts(self, expr: str) -> Self: ...
  def trim(
    self,
    start: float = ..., end: float = ..., start_pts: float = ..., end_pts: float = ...,
    duration: float = ..., start_frame: int = ..., end_frame: int = ...,
    **kwargs
    ) -> Self: ...
  def vflip(self) -> Self: ...
  def zoompan(
    self,
    zoom: float = 1.,
    x = 0, y = 0, d: int = 0, s: str = "hd720",
    fps: int = 25, z: float = ...
    ) -> Self: ...

def cap_to_frame_iter(
  cap: VideoCapture,
  start: int | None = None,
  end: int | None = None,
  exception: bool = False
  
  ) -> Iterator[cv2.Mat]:
  """cv2.VideoCaptureからフレームのイテレーターを作成します

  Args:
      cap (VideoCapture): cv2.VideoCaptureのインスタンス
      start (int | None, optional): 開始フレーム. Defaults to None.
      end (int | None, optional): 修了フレーム. Defaults to None.
      exception (bool, optional): capが開いていないときに例外を創出するか. Defaults to False.

  Yields:
      Iterator[cv2.Mat]: _description_
  """
  
  if not cap.isOpened():
    if exception: raise ValueError(f"capture is closed")
    else: return

  cursor = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

  if isinstance(start, int): cap.set(cv2.CAP_PROP_POS_FRAMES, start)
  else: start = cursor
  
  if isinstance(end, int): _iter = range(start, end)
  else: _iter = count(start)

  for _ in _iter:

    ret, frame = cap.read()
    if not ret: break
    yield frame

  cap.set(cv2.CAP_PROP_POS_FRAMES, cursor)

def frame_iter_to_video_writer(frame_iter: Iterable[cv2.Mat], video_writer: VideoWriter, release: bool = True, exception: bool = False):

  if not video_writer.isOpened():
    if exception: raise ValueError(f"writer is closed")
    else: return

  for frame in frame_iter:
    yield video_writer.write(frame)

  if release:
    video_writer.release()

def video_or_imgdir_pathes(root: Path):

  if is_video(root):
    yield root

  for entry in chain((root,), root.glob("**/*")):

    if entry.is_file(): continue
    listdir = list(entry.iterdir())

    if all(is_image(file) for file in listdir):
      yield entry

    for file in listdir:

      if is_video(file):
        yield file

def is_image(path: PathLike) -> bool:
  return (mtype := mimetypes.guess_type(path)[0]) is not None and mtype.split("/")[0] == "image"
def is_video(path: PathLike) -> bool:
  return (mtype := mimetypes.guess_type(path)[0]) is not None and mtype.split("/")[0] == "video"