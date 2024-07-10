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