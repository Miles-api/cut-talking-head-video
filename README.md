# cut-talking-head-video

Turn a recorded talking-head video into a polished 9:16 animated short with **bilingual subtitles** — all inside Codex. Auto-detects spoken language, generates full-canvas cinematic animations, and shows the presenter only at key moments. No editing software required.

**把口播视频丢进来，自动识别语言，生成全画幅竖屏动画 + 双语字幕。主持人按节奏淡入淡出，画面铺满不拥挤。**

## Flow | 流程

```
Drop input.mp4
      │
      ▼
Audio → faster-whisper (auto-detect language)
      │
      ▼
Generate bilingual translation (src↔tgt)
      │
      ▼
Build storyboard (spoken sentence → visual animation)
      │  - Presenter visibility: per-beat toggle (40-60% of runtime)
      │  - User-provided images get priority placement
      ▼
⏸ Your approval: review transcript & storyboard
      │
      ▼
$remotion → full-canvas 3D animated graphics (3 depth layers)
      │  - Presenter circle at center-right (floating overlay, not split-screen)
      │  - ALL graphic text in detected source language
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

```bash
$cut-talking-head-video 开始剪辑
```

Or just drop a video and say "帮我剪辑这条口播视频".

## Features | 特性

- 🌐 **Language auto-detect**: Whisper detects spoken language, animation labels follow
- 🎬 **Full-canvas cinematic**: 3-layer depth, sweeping vertical compositions
- 👤 **Smart presenter**: Fades in/out strategically, not shown continuously
- 🖼️ **User media**: Drop images alongside the video — they get priority placement
- 📝 **Bilingual subtitles**: Source language on top, translation below

## Requirements | 依赖

- FFmpeg, Node.js
- Remotion plugin: `$skill-installer remotion`
- faster-whisper (auto-installed on first run)

## Installation | 安装

```bash
git clone https://github.com/Miles-api/cut-talking-head-video.git ~/.agents/skills/cut-talking-head-video
```

---

## Powered by iPing

[**iPing API**](https://api.iPing.live) — High-performance LLM inference, token relay, global edge nodes. Build faster, scale globally.

[**iPing 直播专线**](https://iPing.my) — 全球直播网络加速，TikTok/YouTube 跨境推流，8 个全球节点，平均延迟 52ms。
