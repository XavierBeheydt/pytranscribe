# Copyright (c) 2026 Xavier Beheydt <xavier.beheydt@gmail.com>
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "faster-whisper>=1.2.1",
#     "nvidia-cublas-cu12>=12.9.3.13 ; sys_platform == 'linux'",
#     "nvidia-cudnn-cu12>=9.28.0.42 ; sys_platform == 'linux'",
#     "sounddevice>=0.5.6",
# ]
# ///

import argparse
import queue
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self

import numpy as np

SAMPLE_RATE = 16000
BLOCK = SAMPLE_RATE // 2  # audio is read half a second at a time
PAUSE = SAMPLE_RATE * 4 // 10  # silence that ends a sentence
KEEP = SAMPLE_RATE // 2  # silence kept before a sentence, so its start is not cut
MAX_SENTENCE = SAMPLE_RATE * 25
SWITCH_PROBABILITY = 0.8  # confidence needed to switch language


@dataclass
class Args:
    source: str | None
    lang: str | None
    output_dir: Path
    format: str

    @classmethod
    def parse(cls) -> Self:
        parser = argparse.ArgumentParser(description="Transcribe live audio with faster-whisper.")
        parser.add_argument(
            "source", nargs="?", help="stream URL or file read by ffmpeg (default: microphone)"
        )
        parser.add_argument(
            "-l", "--lang", metavar="CODE",
            help="language code, e.g. fr (default: detected for each sentence)",
        )
        parser.add_argument(
            "-o", "--output-dir", type=Path, default=Path(),
            help="output directory (default: the current one)",
        )
        parser.add_argument(
            "--format", default="md", choices=("md", "txt"), help="output format (default: md)"
        )
        ns = parser.parse_args()
        return cls(ns.source, ns.lang, ns.output_dir, ns.format)


def microphone() -> Iterator[np.ndarray]:
    import sounddevice

    blocks: queue.Queue[np.ndarray] = queue.Queue()
    with sounddevice.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=BLOCK,
        callback=lambda data, *_: blocks.put(data[:, 0].copy()),
    ):
        while True: yield blocks.get()


def stream(source: str) -> Iterator[np.ndarray]:
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", source,
           "-f", "f32le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        try:
            while data := proc.stdout.read(BLOCK * 4):
                yield np.frombuffer(data, np.float32)
        finally:
            proc.terminate()


def cut(
    buffer: np.ndarray, offset: int, spans: list[dict]
) -> Iterator[tuple[float, np.ndarray]]:
    for span in spans:
        yield (offset + span["start"]) / SAMPLE_RATE, buffer[span["start"]:span["end"]]


def sentences(blocks: Iterator[np.ndarray]) -> Iterator[tuple[float, np.ndarray]]:
    from faster_whisper.vad import VadOptions, get_speech_timestamps

    options = VadOptions(min_silence_duration_ms=500, speech_pad_ms=150)
    buffer = np.zeros(0, np.float32)
    offset = 0
    try:
        for block in blocks:
            buffer = np.concatenate([buffer, block])
            spans = get_speech_timestamps(buffer, options)
            ended = bool(spans) and len(buffer) - spans[-1]["end"] >= PAUSE
            if ended or len(buffer) >= MAX_SENTENCE:
                yield from cut(buffer, offset, spans)
                offset += len(buffer)
                buffer = buffer[:0]
            elif not spans and len(buffer) > KEEP:
                offset += len(buffer) - KEEP
                buffer = buffer[-KEEP:]
    except KeyboardInterrupt:
        pass
    yield from cut(buffer, offset, get_speech_timestamps(buffer, options))


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
        self.auto = lang is None
        self.lang = lang

    def __call__(self, audio: np.ndarray) -> str:
        if self.auto:
            lang, probability, _ = self.model.detect_language(audio)
            if self.lang is None or (lang != self.lang and probability >= SWITCH_PROBABILITY):
                self.lang = lang
        segments, _ = self.model.transcribe(
            audio, language=self.lang, condition_on_previous_text=False
        )
        return " ".join(s.text.strip() for s in segments).strip()


def clock(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes // 60:02}:{minutes % 60:02}:{seconds:02}"


def main() -> None:
    args = Args.parse()
    started = datetime.now()
    transcriber = Transcriber(args.lang)
    blocks = stream(args.source) if args.source else microphone()
    print("● listening — Ctrl-C to stop", flush=True)
    lines: list[str] = []
    try:
        for start, audio in sentences(blocks):
            text = transcriber(audio)
            if not text: continue
            stamp = clock(start)
            print(f"[{stamp}] {text}", flush=True)
            lines.append(f"**{stamp}**: {text}" if args.format == "md" else f"[{stamp}] {text}")
    except KeyboardInterrupt:
        pass
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"live-{started:%Y%m%d-%H%M%S}.{args.format}"
    output.write_text(("\n\n" if args.format == "md" else "\n").join(lines) + "\n")
    print(output)


if __name__ == "__main__":
    main()
