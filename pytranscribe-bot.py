# Copyright (c) 2026 Xavier Beheydt <xavier.beheydt@gmail.com>
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "av<19",
#     "faster-whisper>=1.2.1",
#     "neonize>=0.10.0",
#     "nvidia-cublas-cu12>=12.9.3.13 ; sys_platform == 'linux'",
#     "nvidia-cudnn-cu12>=9.28.0.42 ; sys_platform == 'linux'",
# ]
# ///

import argparse
import io
import re
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Self

SESSION = Path.home() / ".cache" / "pytranscribe" / "bot-session.db"


@dataclass
class Args:
    allow: set[str]
    lang: str | None

    @classmethod
    def parse(cls) -> Self:
        parser = argparse.ArgumentParser(description="Transcribe WhatsApp voice messages.")
        parser.add_argument(
            "--allow", action="append", required=True, metavar="NUMBER",
            help="number allowed to use the bot, e.g. +33612345678 (repeatable)",
        )
        parser.add_argument(
            "-l", "--lang", metavar="CODE",
            help="language code, e.g. fr (default: detected for each message)",
        )
        ns = parser.parse_args()
        return cls({re.sub(r"\D", "", number) for number in ns.allow}, ns.lang)


def preload_cuda() -> None:
    # faster-whisper needs the CUDA 12 libraries; the pip ones are not on the loader path
    import ctypes

    import nvidia.cublas
    import nvidia.cudnn

    for package, name in ((nvidia.cublas, "libcublas.so.12"), (nvidia.cudnn, "libcudnn.so.9")):
        ctypes.CDLL(Path(package.__path__[0]) / "lib" / name, ctypes.RTLD_GLOBAL)


class Transcriber:
    def __init__(self, lang: str | None) -> None:
        import ctranslate2
        from faster_whisper import WhisperModel

        if sys.platform == "linux": preload_cuda()
        gpu = ctranslate2.get_cuda_device_count() > 0
        self.model = WhisperModel(
            "medium" if gpu else "small",
            device="cuda" if gpu else "cpu",
            compute_type="float16" if gpu else "int8",
        )
        self.lang = lang
        self.lock = threading.Lock()

    def __call__(self, audio: bytes) -> str:
        with self.lock:
            segments, _ = self.model.transcribe(io.BytesIO(audio), language=self.lang)
            return " ".join(s.text.strip() for s in segments).strip()


def reply(client, message, allow: set[str], transcriber: Transcriber) -> None:
    source = message.Info.MessageSource
    if source.IsFromMe or source.IsGroup or not message.Message.HasField("audioMessage"): return
    if not {source.Sender.User, source.SenderAlt.User} & allow: return
    print(f"◂ voice message ({message.Message.audioMessage.seconds} s)", flush=True)
    text = transcriber(client.download_any(message.Message))
    client.reply_message(text or "(no speech detected)", message)
    print("▸ replied", flush=True)


def main() -> None:
    from neonize.client import NewClient
    from neonize.events import ConnectedEv, MessageEv

    args = Args.parse()
    transcriber = Transcriber(args.lang)
    SESSION.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    client = NewClient(str(SESSION))

    @client.event(ConnectedEv)
    def on_connected(client: NewClient, _: ConnectedEv) -> None:
        print("✓ connected — waiting for voice messages", flush=True)

    @client.event(MessageEv)
    def on_message(client: NewClient, message: MessageEv) -> None:
        reply(client, message, args.allow, transcriber)

    client.connect()


if __name__ == "__main__":
    main()
