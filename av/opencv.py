import concurrent.futures
import pyaudio
import cv2
import numpy as np
from dataclasses import dataclass, asdict
from stringcase import camelcase
import time


class Player:

    CHUNK = int(44100 / 15)
    CHANNELS = 1
    RATE = 44100
    FORMAT = pyaudio.paInt16

    video: cv2.VideoCapture = None
    audio: pyaudio.PyAudio = pyaudio.PyAudio()
    instream: pyaudio.Stream = None
    outstream: pyaudio.Stream = None

    __fps = 30
    __prev = 0
    __callback = None

    def __init__(self, callback, fps=30, *args, **kwargs):
        self.__fps = fps
        self.__callback = callback
        self.CHUNK = int(self.RATE / (self.__fps / 2))
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

    @property
    def waitfor(self) -> int:
        if not self.__prev:
            return None
        elapsed = time.time() - self.__prev
        res = 1 / self.__fps - elapsed
        if res > 0:
            return int(res * 1000)
        return None

    def _videoDisplay(self, tv):
        _, frame = tv.result()
        self.__prev = time.time()
        return self.__callback(frame)

    def _audioPlay(self, ta):
        aud = ta.result()
        self.outstream.write(np.frombuffer(aud, dtype="int16"), self.CHUNK)

    def _toggle(self, toggles: dataclass, mode: int):
        for (fn, args) in asdict(toggles).items():
            getattr(cv2, camelcase(fn))(self.WINDOW_NAME, *args[mode])

    def __iter__(self):
        return self

    def __next__(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tv = executor.submit(self.video.read)
            ta = executor.submit(
                self.instream.read, self.CHUNK, exception_on_overflow=False
            )
            return self._videoDisplay(tv), self._audioPlay(ta)

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()
        self.instream.close()
        self.outstream.close()
