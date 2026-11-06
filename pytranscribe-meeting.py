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
from datetime import timedelta
from pathlib import Path
from typing import Self

# Languages with an alignment model in whisperx 3.8.6 (whisperx/alignment.py).
LANGUAGES = (
    "ar",
    "ca",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "eu",
    "fa",
    "fi",
    "fr",
    "gl",
    "he",
    "hi",
    "hr",
    "hu",
    "id",
    "it",
    "ja",
    "ka",
    "ko",
    "lv",
    "ml",
    "nl",
    "nn",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sv",
    "te",
    "tl",
    "tr",
    "uk",
    "ur",
    "vi",
    "zh",
)


@dataclass
class Args:
    file: Path
    output_dir: Path
    lang: str | None
    format: str
    diarize: bool
    rename: dict[str, str]

    @classmethod
    def parse(cls) -> Self:
        parser = argparse.ArgumentParser(description="Transcribe an audio file with WhisperX.")
        parser.add_argument(
            "file", type=Path, help="audio file to transcribe, or transcript to edit with --rename"
        )
        parser.add_argument(
            "-o", "--output-dir", type=Path, help="output directory (default: the audio's)"
        )
        parser.add_argument(
            "-l", "--lang", choices=LANGUAGES, help="audio language (default: detected)"
        )
        parser.add_argument(
            "--format", default="md", choices=("md", "txt"), help="output format (default: md)"
        )
        parser.add_argument(
            "--no-diarize",
            dest="diarize",
            action="store_false",
            help="skip speaker diarization (no Hugging Face token needed)",
        )
        parser.add_argument(
            "--rename",
            nargs="+",
            default=[],
            metavar="OLD=NEW",
            type=lambda pair: pair.split("=", 1),
            help="rename speakers in an existing transcript, without transcribing",
        )
        ns = parser.parse_args()
        return cls(
            ns.file,
            ns.output_dir or ns.file.parent,
            ns.lang,
            ns.format,
            ns.diarize,
            dict(ns.rename),
        )


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
    audio = whisperx.load_audio(str(args.file))
    compute_type = "float16" if device == "cuda" else "int8"
    model = whisperx.load_model("medium", device, compute_type=compute_type, language=args.lang)
    result = model.transcribe(audio, batch_size=16, progress_callback=progress("transcribe"))
    lang = result["language"]
    print(f"language: {lang}", file=sys.stderr)
    if lang in LANGUAGES:
        align_model, meta = whisperx.load_align_model(language_code=lang, device=device)
        result = whisperx.align(
            result["segments"],
            align_model,
            meta,
            audio,
            device,
            progress_callback=progress("align"),
        )
    else:
        print(f"no alignment model for '{lang}': word timestamps skipped", file=sys.stderr)
    if args.diarize:
        diarize = DiarizationPipeline(token=os.environ.get("HF_TOKEN"), device=device)
        segments = diarize(audio, progress_callback=progress("diarize"))
        result = whisperx.assign_word_speakers(segments, result)
    return result["segments"]


def render(segments: list[dict], fmt: str) -> str:
    line, sep = ("**{}**: {}", "\n\n") if fmt == "md" else ("[{}] {}", "\n")
    return (
        sep.join(
            line.format(s["speaker"], s["text"].strip()) if "speaker" in s else s["text"].strip()
            for s in segments
        )
        + "\n"
    )


def report(segments: list[dict]) -> list[str]:
    time: dict[str, float] = {}
    quote: dict[str, str] = {}
    for s in segments:
        if "speaker" not in s:
            continue
        time[s["speaker"]] = time.get(s["speaker"], 0) + s["end"] - s["start"]
        quote.setdefault(s["speaker"], s["text"].strip())
    speakers = sorted(time)
    print(f"{len(speakers)} speakers found:")
    for speaker in speakers:
        duration = timedelta(seconds=round(time[speaker]))
        print(f'  {speaker}  {duration}  "{quote[speaker][:60]}"')
    return speakers


def ask_names(speakers: list[str]) -> dict[str, str]:
    names = {s: input(f"Name for {s} (Enter to keep): ").strip() for s in speakers}
    return {s: name for s, name in names.items() if name}


def rename(path: Path, names: dict[str, str]) -> None:
    text = path.read_text()
    for old, new in names.items():
        text = text.replace(f"**{old}**:", f"**{new}**:").replace(f"[{old}] ", f"[{new}] ")
    path.write_text(text)


def main() -> None:
    args = Args.parse()
    if args.rename:
        rename(args.file, args.rename)
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"{args.file.stem}.{args.format}"
    segments = transcribe(args)
    output.write_text(render(segments, args.format))
    print(output)
    if args.diarize:
        rename(output, ask_names(report(segments)))


if __name__ == "__main__":
    main()
