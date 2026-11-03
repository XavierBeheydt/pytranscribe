# Copyright (c) 2026 Xavier Beheydt <xavier.beheydt@gmail.com>
# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = [
#     "whisperx>=3.8.6",
# ]
# ///

import argparse
import itertools
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Self

# Languages with an alignment model in whisperx 3.8.6 (whisperx/alignment.py).
LANGUAGES = (
    "ar", "ca", "cs", "da", "de", "el", "en", "es", "eu", "fa", "fi", "fr", "gl", "he",
    "hi", "hr", "hu", "id", "it", "ja", "ka", "ko", "lv", "ml", "nl", "nn", "no", "pl",
    "pt", "ro", "ru", "sk", "sl", "sv", "te", "tl", "tr", "uk", "ur", "vi", "zh",
)


@dataclass
class Args:
    audio: Path
    output_dir: Path
    lang: str
    format: str
    diarize: bool

    @classmethod
    def parse(cls) -> Self:
        parser = argparse.ArgumentParser(description="Transcribe an audio file with WhisperX.")
        parser.add_argument("audio", type=Path, help="audio file to transcribe")
        parser.add_argument(
            "-o", "--output-dir", type=Path, help="output directory (default: the audio's)"
        )
        parser.add_argument(
            "-l", "--lang", default="fr", choices=LANGUAGES, help="audio language (default: fr)"
        )
        parser.add_argument(
            "--format", default="md", choices=("md", "txt"), help="output format (default: md)"
        )
        parser.add_argument(
            "--no-diarize", dest="diarize", action="store_false",
            help="skip speaker diarization (no Hugging Face token needed)",
        )
        ns = parser.parse_args()
        return cls(ns.audio, ns.output_dir or ns.audio.parent, ns.lang, ns.format, ns.diarize)


def progress(step: str) -> Callable[[float], None]:
    spinner = itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")

    def show(percent: float) -> None:
        done = percent >= 100
        mark, end = ("✓", "\n") if done else (next(spinner), "")
        print(f"\r{mark} {step}: {percent:5.1f}%", end=end, file=sys.stderr, flush=True)

    return show


def transcribe(args: Args) -> list[dict]:
    import torch
    import whisperx
    from whisperx.diarize import DiarizationPipeline

    device = "cuda" if torch.cuda.is_available() else "cpu"
    audio = whisperx.load_audio(str(args.audio))
    compute_type = "float16" if device == "cuda" else "int8"
    model = whisperx.load_model("medium", device, compute_type=compute_type, language=args.lang)
    result = model.transcribe(audio, batch_size=16, progress_callback=progress("transcribe"))
    align_model, meta = whisperx.load_align_model(language_code=args.lang, device=device)
    result = whisperx.align(
        result["segments"], align_model, meta, audio, device, progress_callback=progress("align")
    )
    if args.diarize:
        diarize = DiarizationPipeline(token=os.environ.get("HF_TOKEN"), device=device)
        segments = diarize(audio, progress_callback=progress("diarize"))
        result = whisperx.assign_word_speakers(segments, result)
    return result["segments"]


def render(segments: list[dict], fmt: str) -> str:
    line, sep = ("**{}**: {}", "\n\n") if fmt == "md" else ("[{}] {}", "\n")
    return sep.join(
        line.format(s["speaker"], s["text"].strip()) if "speaker" in s else s["text"].strip()
        for s in segments
    ) + "\n"


def main() -> None:
    args = Args.parse()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"{args.audio.stem}.{args.format}"
    output.write_text(render(transcribe(args), args.format))
    print(output)


if __name__ == "__main__":
    main()
