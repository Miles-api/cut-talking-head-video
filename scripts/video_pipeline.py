#!/usr/bin/env python3
"""Deterministic helpers for the cut-talking-head-video Codex skill.

Commands:
  preflight  Inspect source, normalize optional SRT, extract preview frames/contact sheet.
  transcribe Transcribe prepared speech WAV with faster-whisper.
  verify     Validate rendered MP4 against source and subtitle timeline.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)


def need(binary: str) -> None:
    if not shutil.which(binary):
        raise RuntimeError(f"Required command not found: {binary}")


def probe(path: Path) -> dict[str, Any]:
    need("ffprobe")
    p = run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path),
    ])
    return json.loads(p.stdout)


def duration(info: dict[str, Any]) -> float:
    try:
        return float(info.get("format", {}).get("duration", 0))
    except (TypeError, ValueError):
        return 0.0


def video_stream(info: dict[str, Any]) -> dict[str, Any] | None:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)


def audio_stream(info: dict[str, Any]) -> dict[str, Any] | None:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)


def parse_time(value: str) -> float:
    h, m, rest = value.replace(".", ",").split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")[:3]) / 1000


def format_time(value: float) -> str:
    value = max(0.0, value)
    ms_total = round(value * 1000)
    h, rem = divmod(ms_total, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", raw.strip()) if raw.strip() else []
    cues: list[dict[str, Any]] = []
    timeline = re.compile(r"(\d{2}:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{1,3})")
    for block in blocks:
        lines = [x.strip("\ufeff") for x in block.splitlines()]
        idx = next((i for i, x in enumerate(lines) if timeline.search(x)), None)
        if idx is None:
            continue
        match = timeline.search(lines[idx])
        assert match
        start, end = parse_time(match.group(1)), parse_time(match.group(2))
        text = "\n".join(x.strip() for x in lines[idx + 1:] if x.strip())
        cues.append({"index": len(cues) + 1, "start": start, "end": end, "text": text})
    return cues


def validate_cues(cues: list[dict[str, Any]], max_duration: float | None = None) -> list[str]:
    errors: list[str] = []
    previous = -1.0
    for cue in cues:
        if not cue["text"]:
            errors.append(f"cue {cue['index']}: empty text")
        if cue["start"] < 0 or cue["end"] <= cue["start"]:
            errors.append(f"cue {cue['index']}: invalid interval")
        if cue["start"] < previous - 0.001:
            errors.append(f"cue {cue['index']}: non-monotonic start")
        if max_duration and cue["end"] > max_duration + 0.5:
            errors.append(f"cue {cue['index']}: ends beyond video ({cue['end']:.3f} > {max_duration:.3f})")
        previous = cue["start"]
    return errors


def write_srt(cues: list[dict[str, Any]], path: Path) -> None:
    chunks = []
    for i, cue in enumerate(cues, 1):
        chunks.append(f"{i}\n{format_time(cue['start'])} --> {format_time(cue['end'])}\n{cue['text']}\n")
    path.write_text("\n".join(chunks), encoding="utf-8")


def extract_contact_sheet(media: Path, out: Path, count: int = 9) -> Path:
    need("ffmpeg")
    info = probe(media)
    dur = duration(info)
    frames = out / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    if dur <= 0:
        raise RuntimeError("Cannot extract previews: duration is zero")
    for i in range(count):
        t = dur * (i + 0.5) / count
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(media), "-frames:v", "1", "-vf", "scale=360:-2", str(frames / f"frame-{i+1:02d}.jpg")])
    sheet = out / "contact-sheet.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-pattern_type", "glob", "-i", str(frames / "frame-*.jpg"), "-vf", "tile=3x3:padding=8:margin=8:color=20242b", "-frames:v", "1", str(sheet)])
    return sheet


def cmd_preflight(args: argparse.Namespace) -> int:
    video = Path(args.video).resolve()
    if not video.is_file():
        raise RuntimeError(f"Video not found: {video}")
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    vs, aus = video_stream(info), audio_stream(info)
    if not vs:
        raise RuntimeError("Source has no video stream")
    if not aus:
        raise RuntimeError("Source has no audio stream; original voice cannot be preserved")
    cues: list[dict[str, Any]] = []
    cue_errors: list[str] = []
    normalized_srt = None
    if args.srt:
        src_srt = Path(args.srt).resolve()
        if src_srt.is_file():
            cues = parse_srt(src_srt)
            cue_errors = validate_cues(cues, duration(info))
            normalized_srt = out / "transcript.srt"
            write_srt(cues, normalized_srt)
        elif args.require_srt:
            raise RuntimeError(f"SRT not found: {src_srt}")
    sheet = extract_contact_sheet(video, out)
    report = {
        "source": str(video), "duration": duration(info),
        "video": {k: vs.get(k) for k in ("codec_name", "width", "height", "r_frame_rate", "avg_frame_rate")},
        "audio": {k: aus.get(k) for k in ("codec_name", "sample_rate", "channels", "channel_layout")},
        "transcript_source": "provided SRT" if cues else "audio transcription required",
        "subtitle_cues": len(cues), "subtitle_errors": cue_errors,
        "normalized_srt": str(normalized_srt) if normalized_srt else None,
        "contact_sheet": str(sheet),
    }
    (out / "preflight.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if cue_errors else 0


def cmd_transcribe(args: argparse.Namespace) -> int:
    audio = Path(args.audio).resolve()
    if not audio.is_file():
        raise RuntimeError(f"Audio not found: {audio}")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed. Install it in a project venv: python -m pip install faster-whisper") from exc
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    compute = args.compute_type
    model = WhisperModel(args.model, device=args.device, compute_type=compute)
    segments_iter, meta = model.transcribe(str(audio), language=args.language, vad_filter=True, word_timestamps=True, beam_size=5)
    segments, cues = [], []
    for seg in segments_iter:
        text = seg.text.strip()
        words = [{"start": w.start, "end": w.end, "word": w.word, "probability": w.probability} for w in (seg.words or [])]
        item = {"start": seg.start, "end": seg.end, "text": text, "avg_logprob": seg.avg_logprob, "no_speech_prob": seg.no_speech_prob, "words": words}
        segments.append(item)
        if text:
            cues.append({"index": len(cues)+1, "start": seg.start, "end": seg.end, "text": text})
    raw = {"language": meta.language, "language_probability": meta.language_probability, "duration": meta.duration, "segments": segments}
    (out / "transcript.raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    write_srt(cues, out / "transcript.srt")
    (out / "transcript.txt").write_text("".join(c["text"] for c in cues), encoding="utf-8")
    risky = []
    for s in segments:
        low_words = [w for w in s["words"] if w.get("probability") is not None and w["probability"] < 0.70]
        has_sensitive_token = bool(re.search(r"[A-Za-z0-9$¥￥%]", s["text"]))
        if s["avg_logprob"] < -0.8 or low_words or has_sensitive_token:
            risky.append(s)
    review = ["# Transcript Review", "", f"- Language: {meta.language} ({meta.language_probability:.3f})", f"- Segments: {len(segments)}", "", "## Items requiring human review", ""]
    if not risky:
        review.append("No segment was automatically flagged. Still review names, numbers, brands, and technical terms.")
    else:
        for s in risky:
            review.append(f"- {format_time(s['start'])}–{format_time(s['end'])}: {s['text']}")
    (out / "transcript_review.md").write_text("\n".join(review)+"\n", encoding="utf-8")
    print(json.dumps({"segments": len(segments), "srt": str(out / 'transcript.srt'), "review_items": len(risky)}, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    source, output = Path(args.source).resolve(), Path(args.output).resolve()
    if not source.is_file() or not output.is_file():
        raise RuntimeError("Source or output file missing")
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    src, dst = probe(source), probe(output)
    dsrc, ddst = duration(src), duration(dst)
    dvs, das = video_stream(dst), audio_stream(dst)
    errors = []
    if not dvs: errors.append("output has no video stream")
    if not das: errors.append("output has no audio stream")
    if abs(dsrc-ddst) > max(0.20, 1/30 + 0.05): errors.append(f"duration mismatch: source={dsrc:.3f}s output={ddst:.3f}s")
    if dvs and (int(dvs.get("width",0)) != 1080 or int(dvs.get("height",0)) != 1920): errors.append(f"wrong resolution: {dvs.get('width')}x{dvs.get('height')}")
    cues = []
    if args.srt and Path(args.srt).is_file():
        cues = parse_srt(Path(args.srt))
        errors.extend(validate_cues(cues, ddst))
    sheet = extract_contact_sheet(output, out)
    report = {
        "ok": not errors, "errors": errors,
        "source_duration": dsrc, "output_duration": ddst,
        "output_size_bytes": output.stat().st_size,
        "video": {k: dvs.get(k) if dvs else None for k in ("codec_name", "width", "height", "r_frame_rate")},
        "audio": {k: das.get(k) if das else None for k in ("codec_name", "sample_rate", "channels")},
        "subtitle_cues": len(cues), "contact_sheet": str(sheet),
        "note": "Stream/timeline checks are automatic. Visually inspect the contact sheet for subtitle clipping, crop instability, blank frames, and collisions.",
    }
    (out / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("preflight")
    a.add_argument("--video", required=True); a.add_argument("--srt"); a.add_argument("--out", required=True); a.add_argument("--require-srt", action="store_true")
    a.set_defaults(func=cmd_preflight)
    a = sub.add_parser("transcribe")
    a.add_argument("--audio", required=True); a.add_argument("--out", required=True); a.add_argument("--model", default="medium"); a.add_argument("--language", default="zh")
    a.add_argument("--device", default="auto"); a.add_argument("--compute-type", default="int8")
    a.set_defaults(func=cmd_transcribe)
    a = sub.add_parser("verify")
    a.add_argument("--source", required=True); a.add_argument("--output", required=True); a.add_argument("--srt"); a.add_argument("--out", required=True)
    a.set_defaults(func=cmd_verify)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or str(exc), file=sys.stderr); return exc.returncode or 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
