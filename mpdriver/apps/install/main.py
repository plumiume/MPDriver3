import ffmpeg

from ...core.main_base import Verbose
from .args import InstallArgs

def app_main(ns: InstallArgs):

    verbose = Verbose(ns.verbose)

    try:
        ffmpeg.probe("not_exists.mp4")
    except FileNotFoundError:
        verbose.error("ffmpeg is not installed")
        verbose.error("please check your system")
        verbose.info("This script tested by ffmpeg.probe")