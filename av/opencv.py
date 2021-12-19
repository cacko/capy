import concurrent.futures
import sounddevice as sd
import cv2
from dataclasses import dataclass, asdict
from stringcase import camelcase
import time

class Player:

    CHUNK = int(44100 / 15)
    CHANNELS = 1
    RATE = 44100
    FORMAT = "int16"

    video: cv2.VideoCapture = None
    instream: sd.InputStream = None
    outstream: sd.OutputStream = None

    __fps = 30
    __prev = 0
    __callback = None

    def __init__(self, callback, videoInputIdx:int, audioInputIdx:int, audioOutputIdx: int, fps=30, *args, **kwargs):
        self.__fps = fps
        self.__callback = callback
        self.CHUNK = int(self.RATE / (self.__fps / 2))
        self.video = cv2.VideoCapture(videoInputIdx)
        self.instream = sd.InputStream(
            device=audioInputIdx,
            channels=self.CHANNELS,
            samplerate=self.RATE,
            blocksize=self.CHUNK,
            dtype=self.FORMAT,
        )
        self.outstream = sd.OutputStream(
            channels=self.CHANNELS,
            dtype=self.FORMAT,
            samplerate=self.RATE,
            blocksize=self.CHUNK,
            device=audioOutputIdx,
        )
        self.instream.start()
        self.outstream.start()

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
        aud, _ = ta.result()
        self.outstream.write(aud)

    def _toggle(self, toggles: dataclass, mode: int):
        for (fn, args) in asdict(toggles).items():
            getattr(cv2, camelcase(fn))(self.WINDOW_NAME, *args[mode])

    def __iter__(self):
        return self

    def __next__(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tv = executor.submit(self.video.read)
            ta = executor.submit(self.instream.read, self.CHUNK)
            return self._videoDisplay(tv), self._audioPlay(ta)

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()
        self.instream.close()
        self.outstream.close()
