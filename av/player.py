import concurrent.futures
import pyaudio
import cv2
import numpy as np
from dataclasses import dataclass, asdict
from stringcase import camelcase


@dataclass
class FullscreenToggles:
    set_window_property: tuple[tuple] = (
        (cv2.WND_PROP_TOPMOST, 1),
        (cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN),
    )


@dataclass
class RatioToggles:
    set_window_property: tuple[tuple] = (
        (cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO),
        (cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_FREERATIO),
    )


@dataclass
class TopMostToggles:
    named_window: tuple[tuple] = (
        (cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO,),
        (cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO,),
    )
    set_window_property: tuple[tuple] = (
        (cv2.WND_PROP_TOPMOST, 0),
        (cv2.WND_PROP_TOPMOST, 1),
    )


class Player:

    CHUNK = int(44100 / 30)
    CHANNELS = 1
    RATE = 44100
    FORMAT = pyaudio.paInt16
    WINDOW_NAME = "CAPY"

    video: cv2.VideoCapture = None
    audio: pyaudio.PyAudio = pyaudio.PyAudio()
    instream: pyaudio.Stream = None
    outstream: pyaudio.Stream = None

    ir = None
    shape = None

    __is_fullscreen = 0
    __is_topmost = 1
    __pause = False

    def __init__(self, *args, **kwargs):
        self.video = cv2.VideoCapture(0)
        self.instream = self.audio.open(
            format=self.FORMAT,
            input_device_index=4,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        self.outstream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK,
            output_device_index=1,
        )

    def _videoDisplay(self, frame):
        return frame

    def _audioPlay(self, aud):
        self.outstream.write(aud, self.CHUNK)

    def _toggle(self, toggles: dataclass, mode: int):
        for (fn, args) in asdict(toggles).items():
            getattr(cv2, camelcase(fn))(self.WINDOW_NAME, *args[mode])

    def toggleFullScreen(self):
        self.__is_fullscreen = 1 ^ self.__is_fullscreen
        self._toggle(RatioToggles(), self.__is_fullscreen)
        self._toggle(FullscreenToggles(), self.__is_fullscreen)

    def toggleTopmost(self):
        if self.__is_fullscreen:
            return
        self.__is_topmost = 1 ^ self.__is_topmost
        cv2.destroyAllWindows()
        self._toggle(TopMostToggles(), self.__is_topmost)

    def __iter__(self):
        return self

    def __next__(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if self.__pause:
                return
            tv = executor.submit(self.video.read)
            ta = executor.submit(
                self.instream.read, self.CHUNK, exception_on_overflow=False
            )
            _, frame = tv.result()
            aud = ta.result()
            return self._videoDisplay(frame), self._audioPlay(
                np.frombuffer(aud, dtype="int16")
            )

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()
        self.instream.close()
        self.outstream.close()
