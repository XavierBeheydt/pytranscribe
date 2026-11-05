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

| Script | Use case | Engine |
|---|---|---|
| [`pytranscribe-meeting.py`](#pytranscribe-meeting) | recordings with several speakers, named | WhisperX |
| [`pytranscribe-live.py`](#pytranscribe-live) | real time, from a microphone or a stream | faster-whisper |
| [`pytranscribe-bot.py`](#pytranscribe-bot) | voice messages from WhatsApp | faster-whisper |

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

## pytranscribe-live

Transcribes in real time, from a microphone or a stream, with
[faster-whisper](https://github.com/SYSTRAN/faster-whisper). A voice activity
detector cuts the audio at each pause, and each sentence is printed a moment
after it is spoken.

### Requirements

- [uv](https://docs.astral.sh/uv/). [ffmpeg](https://ffmpeg.org/) for streams
  and files.
- For the microphone, [PortAudio](https://www.portaudio.com/): bundled on
  Windows and macOS, a system package on Linux (`libportaudio2`, `portaudio`…).
- No Hugging Face token: there is no speaker detection.

### Usage

```sh
uv run pytranscribe-live.py                          # default microphone
uv run pytranscribe-live.py https://example.com/radio.m3u8   # stream or file (ffmpeg)
```

```text
● listening — Ctrl-C to stop
[00:00:03] Bonjour à tous, merci d'être là.
[00:00:08] On commence par le budget de l'année prochaine.
```

On Ctrl-C, the full transcript is written to `live-<date>-<time>.md`.

| Option | Default | |
|---|---|---|
| `-l`, `--lang` | detected for each sentence | force a language |
| `-o`, `--output-dir` | the current directory | where to write the transcript |
| `--format` | `md` | `md` or `txt` |

## pytranscribe-bot

A WhatsApp bot: send it a voice message, it replies with the transcript.
Transcription uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
on your machine, so the audio goes through no transcription service.

> **Unofficial.** The bot is a linked device of a WhatsApp account, through
> [neonize](https://github.com/krypton-byte/neonize) (WhatsApp Web protocol).
> This is against WhatsApp's terms of service: the number can be banned. Use a
> dedicated number, not your main one.

### Requirements

- [uv](https://docs.astral.sh/uv/) and [ffmpeg](https://ffmpeg.org/).
- A WhatsApp account for the bot, on a phone you can scan a QR code with.
- The session file gives full access to that account: it lives in your home
  directory (`~/.pytranscribe-bot/`), never in the repo.

### Usage

```sh
uv run pytranscribe-bot.py --allow +33612345678
```

On the first run, a QR code is printed: scan it in WhatsApp → *Linked
devices*. The bot then replies to the voice messages of the allowed numbers
only, with the transcript.

| Option | Default | |
|---|---|---|
| `--allow` | required | a number allowed to use the bot (repeat for several) |
| `-l`, `--lang` | detected for each message | force a language |

## License

[MIT](LICENSE)
