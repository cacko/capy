from PyQt6.QtGui import QIcon
from gui import App
from PyQt6.QtWidgets import QApplication
import sys
import argparse
import sounddevice as sd

PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    "-i", "--audio_input", type=int, help="audio input index", default=4
)
PARSER.add_argument(
    "-o", "--audio_output", type=int, help="audio ouput index", default=1
)
PARSER.add_argument(
    "-c", "--video_input", type=int, help="video input index", default=1
)
PARSER.add_argument("action", nargs="?", default="app", help="action")


class Capy:
    def run(self):
        return getattr(self, f"action_{self.action}")()

    def action_app(self):
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        icon = QIcon()
        icon.addFile("capy.png")
        app.setWindowIcon(icon)
        a = App(
            videoInput=self.video_input,
            audioInput=self.audio_input,
            audioOutput=self.audio_output,
        )
        a.show()
        sys.exit(app.exec())

    def action_list_audio(self):
        for idx, d in enumerate(sd.query_devices()):
            print(idx, d)

    def action_list_video(self):
        pass


if __name__ == "__main__":
    try:
        capy = Capy()
        PARSER.parse_args(namespace=capy)
        capy.run()
    except KeyboardInterrupt:
        pass
