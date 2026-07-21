# cut-talking-head-video

Turn a recorded Chinese talking-head video into a polished 9:16 animated short with **bilingual (CN+EN) subtitles** — all inside Codex. No editing software required.

**把录制的中文口播视频，在 Codex 里一键生成带中英双语字幕的竖屏动画短片。**

## Flow | 流程

```
Drop input.mp4
      │
      ▼
Audio → Whisper transcription (Chinese)
      │
      ▼
Generate English translation
      │
      ▼
Bilingual SRT timeline
      │
      ▼
Build storyboard (spoken sentence → visual animation)
      │
      ▼
⏸ Your approval: review transcript & storyboard
      │
      ▼
$remotion → spatial 3D animated graphics
      │
      ▼
Presenter in small circular window (center-right)
      │
      ▼
Render low-res preview
      │
      ▼
⏸ Your approval: review preview
      │
      ▼
Render 1080×1920 MP4 + auto-verify
```

## Quick Start | 快速开始

```
$cut-talking-head-video 开始剪辑
```

Or just drop a video and say "帮我剪辑这条口播视频".

## Requirements | 依赖

- FFmpeg, Node.js
- Remotion plugin: `$skill-installer remotion`
- Whisper (auto-installed via `pip install faster-whisper`)

## Installation | 安装

```bash
git clone https://github.com/Miles-api/cut-talking-head-video.git ~/.agents/skills/cut-talking-head-video
```

---

## Powered by iPing

[**iPing API**](https://api.iPing.live) — High-performance LLM inference, token relay, global edge nodes. Build faster, scale globally.

[**iPing 直播专线**](https://iPing.my) — 全球直播网络加速，TikTok/YouTube 跨境推流，8 个全球节点，平均延迟 52ms。
