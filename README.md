# pytranscribe

[![Python 3.13](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/github/license/XavierBeheydt/pytranscribe)](LICENSE)
[![Version](https://img.shields.io/github/v/tag/XavierBeheydt/pytranscribe?sort=semver&label=version)](https://github.com/XavierBeheydt/pytranscribe/tags)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fpytranscribe.beheydt.dev&label=website)](https://pytranscribe.beheydt.dev)

Audio transcription scripts, each one a standalone [uv](https://docs.astral.sh/uv/)
script: dependencies are declared inline (PEP 723) and installed by `uv run`.
Scripts are named after their use case:

| Script | Use case | Engine | Status |
|---|---|---|---|
| `pytranscribe-meeting.py` | recordings with several speakers, named | WhisperX | available |
| `pytranscribe-live.py` | real time, from a microphone or a stream | faster-whisper | planned ([#5](https://github.com/XavierBeheydt/pytranscribe/issues/5), [#6](https://github.com/XavierBeheydt/pytranscribe/issues/6)) |
| `pytranscribe-bot.py` | voice messages from a chat | faster-whisper | planned ([#7](https://github.com/XavierBeheydt/pytranscribe/issues/7)) |

## pytranscribe-meeting

Transcribes an audio file with [WhisperX](https://github.com/m-bain/whisperX):
transcription, word alignment, then speaker diarization with
[pyannote](https://github.com/pyannote/pyannote-audio).

### Requirements

- [uv](https://docs.astral.sh/uv/) and [ffmpeg](https://ffmpeg.org/).
- An NVIDIA GPU with CUDA is used when available; otherwise the CPU (much
  slower).
- For diarization, once:
  1. accept the terms of
     [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1);
  2. create a Hugging Face **read** token and log in with
     `uvx --from huggingface_hub hf auth login` (or export it as `HF_TOKEN`).

### Usage

```sh
uv run pytranscribe-meeting.py reunion.m4a
```

Any format ffmpeg reads works (m4a, mp3, wav, mp4…). The transcript is written
next to the audio, with the same name (`reunion.md`):

```md
**SPEAKER_00**: Bonjour à tous, merci d'être présents.

**SPEAKER_01**: Merci, j'ai préparé un tableau.
```

| Option | Default | |
|---|---|---|
| `-l`, `--lang` | `fr` | audio language, among those WhisperX can align (`--help` lists them) |
| `-o`, `--output-dir` | the audio's directory | where to write the transcript |
| `--format` | `md` | `md` or `txt` (`[SPEAKER_00] text` lines) |
| `--no-diarize` | | skip diarization: no speakers, no token needed |

### Naming the speakers

After the transcription, the script prints the speakers found, with their
speaking time and first sentence, then asks a name for each one (Enter keeps
the label):

```text
2 speakers found:
  SPEAKER_00  0:42:10  "Bonjour à tous, merci d'être présents."
  SPEAKER_01  1:51:03  "Merci, j'ai préparé un tableau."
Name for SPEAKER_00 (Enter to keep): Xavier
Name for SPEAKER_01 (Enter to keep): Guillaume
```

To rename them later, without transcribing again (the file comes first):

```sh
uv run pytranscribe-meeting.py reunion.md --rename SPEAKER_00=Xavier SPEAKER_01=Guillaume
```

## License

[MIT](LICENSE)
