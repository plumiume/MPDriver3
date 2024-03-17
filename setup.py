from setuptools import setup, find_packages

setup(
    name = "MPDriver3",
    summary = "MediaPipeによる姿勢推定アプリケーション",
    version = "0.0",
    author = "kimlab",
    author_email = "kimlab.nittc@gmail.com",
    packages = find_packages(),
    install_requires = [
        "typing_extensions",
        "opencv-python",
        "ffmpeg-python",
        "mediapipe",
        "tqdm"
    ],
    entry_points = {
        "console_scripts": [
            "mpdriver = mpdriver.__main__:main"
        ]
    }
)