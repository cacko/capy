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

    def __init__(self, fps=30, *args, **kwargs):
        self.__fps = fps
        self.CHUNK = int(self.RATE / (self.__fps / 2))
        self.video = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
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

    def _videoDisplay(self, frame):
        self.__prev = time.time()
        return frame

    def _audioPlay(self, aud):
        self.outstream.write(aud, self.CHUNK)

    def _toggle(self, toggles: dataclass, mode: int):
        for (fn, args) in asdict(toggles).items():
            getattr(cv2, camelcase(fn))(self.WINDOW_NAME, *args[mode])

    def __iter__(self):
        return self

    def __next__(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if wf := self.waitfor:
                cv2.waitKey(wf)
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
