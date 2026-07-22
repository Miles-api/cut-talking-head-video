---
name: cut-talking-head-video
version: 0.1.1
description: Turn a recorded talking-head video into a polished 9:16 animated short video with Remotion. Auto-detects the spoken language and generates subtitles, labels, and UI in that language by default. Trigger when the user drops a video file and asks to 剪辑口播视频, 做视频, 生成动画视频, or types $cut-talking-head-video. Works with or without subtitles.srt. Preserves the original voice track, uses verbatim subtitles, places the presenter in a small circular window at center-right, and generates spatial animated graphics with at most 1-2 context-relevant images.
---

# Cut Talking-Head Video

You are a video editing agent. When a user drops a `.mp4` file and invokes this skill (via `$cut-talking-head-video` or by saying 剪辑/做视频/生成动画), execute this pipeline without asking unnecessary questions. The only pauses are for transcript and preview approval.

## Quick start (what the user does)

1. Drop `input.mp4` into the Codex chat.
2. Optionally drop `subtitles.srt` too.
3. Type: `$cut-talking-head-video 开始剪辑`
4. Approve the transcript and storyboard when prompted.
5. Approve the preview when prompted.
6. Receive `output/final.mp4`.

## Non-negotiable rules

1. **Original voice only.** Never generate TTS, never clone or replace the voice, never alter speech speed.
2. **Verbatim subtitles.** Every spoken word must appear in the on-screen subtitles. Do not summarise, rewrite, omit, reorder, or add spoken claims.
3. **Small circular presenter — shown selectively, not continuously.** The presenter appears as a circular crop at center-right (x≈68-73%, y≈43-52%), 20-25% of canvas width. Never make the presenter full-screen. **The presenter is NOT a permanent fixture.** Fade it in during key statements, personal testimony, emotional peaks, or call-to-action — fade it out when the focus should be on the visuals. A typical 2-minute video should have the presenter visible for roughly 40-60% of the runtime. Use opacity transitions (0.3-0.5s fade), not hard cuts.
4. **Max 1-2 images per video — plus user-provided media.** Zero images is fine. Use them only when a real product, event, environment, or news item is explicitly referenced. Otherwise use code-generated 3D/motion graphics. **If the user explicitly provides images, screenshots, or product photos — use them.** Treat user-supplied media as high-priority scene elements: display them prominently, not as a tiny corner insert.
5. **Spatial, not flat.** Use depth, parallax, perspective, glass/metal surfaces, light and shadow. No cheap templates, no random particles, no cartoon robots, no fake news screenshots.
6. **Render, don't just code.** The task is incomplete until `output/final.mp4` is actually rendered and verified.
7. **Two approval gates.** Never start expensive rendering before the user approves the transcript/storyboard. Never deliver the final video without a preview check.
8. **Graphics language = source language.** All on-screen graphic text — labels, chart axes, data overlays, callouts, UI mockups, scene titles — must appear in the detected spoken language (`$SRC_LANG`). Never write Remotion visual text in English unless the speaker is speaking English.
9. **Full-canvas animation.** BackgroundScene must fill the entire 1080×1920 canvas — top to bottom, edge to edge. The presenter is a floating overlay on a rich full-screen world, NOT a split-screen partner. Graphics should occupy significant portions of the vertical frame with depth layers and cinematic scale. Never tuck animations into a corner to "leave room."

---

## Pipeline

### Step 1 — Identify inputs

Find the video file from the conversation. The user may have dropped it, mentioned it, or it may be at `./input.mp4`. Do not guess among multiple `.mp4` files — ask which one.

Look for `./subtitles.srt` or any dropped `.srt` file. Set `HAS_SRT=true` or `HAS_SRT=false`.

Create `./work/` directory for all intermediate files.

Also scan for any user-provided media files alongside the video — `.png`, `.jpg`, `.jpeg`, `.webp` files the user may have dropped. If found, note them as `USER_IMAGES` and use them as priority scene elements.

### Step 2 — Preflight (always run)

```bash
python3 "$SKILL_DIR/scripts/video_pipeline.py" preflight \
  --video ./input.mp4 \
  ${HAS_SRT:+--srt ./subtitles.srt} \
  --out ./work
```

Check `work/preflight.json`. Verify:
- Source has both video and audio streams
- Duration is reasonable (>3 seconds)
- Contact sheet at `work/contact-sheet.jpg` shows a visible person

If the source has no audio stream, stop and tell the user. Do not fabricate audio.

### Step 3 — Obtain transcript

**If SRT exists:**

Parse it, normalise encoding (UTF-8) and line endings. Validate timestamps are monotonic and don't exceed video duration. Write normalised SRT to `work/transcript.srt`.

**If NO SRT:**

Extract audio:
```bash
ffmpeg -y -i input.mp4 -vn -ac 1 -ar 16000 work/speech.wav
```

Transcribe with faster-whisper. Install it if needed (do NOT use a paid API without asking):
```bash
python3 -m venv .venv
.venv/bin/pip install faster-whisper
.venv/bin/python "$SKILL_DIR/scripts/video_pipeline.py" transcribe \
  --audio work/speech.wav --out work --model medium
```

Note: `--language` is omitted, so faster-whisper auto-detects the spoken language.

This creates:
- `work/transcript.raw.json` — segments with word-level timestamps; includes `language` field with the detected language
- `work/transcript.srt` — subtitle cues in the detected language
- `work/transcript.txt` — continuous text
- `work/transcript_review.md` — flagged uncertain items (brand names, English terms, numbers, low-confidence segments)

Read `work/transcript_review.md`. **Highlight every uncertain item prominently** when presenting to the user. Never silently guess a brand name or number.

**Language detection:** Read `work/transcript.raw.json` → `language` field. Store the detected language code (e.g. `"zh"`, `"en"`, `"ja"`) as `$SRC_LANG`. This drives all subsequent decisions — subtitle layout, translation direction, and Remotion UI labels.

### Step 3b — Generate bilingual subtitles

After the transcript is confirmed, **determine translation direction based on `$SRC_LANG`**:

- If `$SRC_LANG` is `"zh"` → translate Chinese → English
- If `$SRC_LANG` is `"en"` or another non-Chinese language → translate English/other → Chinese
- General rule: the translation target is the complement language (Chinese ↔ English/other)

Translate **sentence by sentence** to natural language. Preserve the original SRT timestamps — the translation cue boundaries must match the source ones exactly.

Create `work/transcript_tgt.srt` with the same cue count and identical timestamps as `work/transcript.srt`.

Translation rules:
- Translate meaning, not word-for-word. Target language should read naturally.
- Preserve brand names, product names, and proper nouns as-is (Kimi, iPing, Codex, etc.).
- For technical terms, use the standard equivalent in the target language.
- Keep numbers and units exactly as spoken.
- Never add explanations, caveats, or content not present in the original.

Create `work/transcript_bilingual.json`:
```json
[
  {"index": 1, "start": 0.0, "end": 1.5, "src": "大家好我是土狗", "tgt": "Hey everyone, I'm Tugou"},
  {"index": 2, "start": 1.5, "end": 3.2, "src": "今天聊AI", "tgt": "Today let's talk about AI"}
]
```
(Field names: `src` for the source/subtitle language, `tgt` for the translated language.)

This file drives the Remotion bilingual subtitle component.

If the user explicitly requests single-language (只说中文 / English only / 不用双语 / no bilingual), skip this step and only use `work/transcript.srt`.

### Step 4 — Build storyboard

Read the full transcript. Then read `references/visual-standard.md` for the semantic-to-visual mapping table and visual rules.

Create `work/storyboard.json` and `work/storyboard.md`:

Each beat (3-8 seconds, grouping adjacent SRT cues by meaning) must include:
- `start` / `end` (seconds)
- `spoken_text` (exact transcript for this beat)
- `semantic_purpose` (what this segment is doing: hook, evidence, reversal, explanation, conclusion, CTA)
- `visual_scene` (what the viewer sees — specific, not generic)
- `animation_events` (list of timed visual actions)
- `graphic_labels` (on-screen labels separate from spoken subtitles — **MUST be written in `$SRC_LANG`, the detected spoken language, NOT in English by default**)
- `intensity` (low/medium/high)
- `image_required` (true/false + justification + source if true; prioritize any `USER_IMAGES` found in Step 1)
- `show_presenter` (true/false — only show the presenter circle in this beat if there's a reason: personal statement, emotional peak, direct address to viewer, call-to-action)
- `presenter_note` (any collision or special handling)

Also create `work/cue-visual-matrix.json` — one row per SRT cue, mapping each spoken sentence to its exact visual representation. This matrix is the contract: every spoken claim must have a corresponding visual action, and no visual may introduce claims absent from the transcript.

### Step 5 — Approval gate 1: transcript + storyboard

**STOP HERE.** Present the user with:

1. Full transcript text (or a clear summary if it's very long)
2. Every uncertain recognition item from `transcript_review.md`
3. Storyboard beat table (compact: time, first words, visual scene, intensity)
4. Image count and justification
5. Ask: **请确认字幕和分镜。回复"继续剪辑"，或直接指出要改的字和镜头。**

Do NOT proceed until the user replies. If they send corrections, update the transcript/SRT and affected storyboard beats, then ask again.

Skip this gate only if the user explicitly says "全自动" or "不用确认直接做".

### Step 6 — Load Remotion skill

Before writing any video code, load the Remotion best-practices skill. In Codex, invoke:

```
$remotion-best-practices
```

Or if the plugin is named differently, try:
```
$remotion
```

Read the relevant rules for: captions (`rules/subtitles.md` or `rules/display-captions.md`), audio (`rules/audio.md`), video embedding (`rules/videos.md`), timing (`rules/timing.md`), sequencing (`rules/sequencing.md`), compositions (`rules/compositions.md`), animations (`rules/animations.md`), text (`rules/text-animations.md`), and measuring text (`rules/measuring-text.md`).

If the Remotion skill/plugin is not installed, tell the user to install it first:
```
$skill-installer remotion
```

Then proceed.

### Step 7 — Scaffold Remotion project

```bash
npx create-video@latest --yes --blank --no-tailwind talking-head-video
cd talking-head-video
npm install
```

Create these components (separate files, not one monolith):
- `src/VideoPlayer.tsx` — `<Video>` from `@remotion/video` playing `input.mp4`, circular crop
- `src/PresenterCircle.tsx` — mask, border glow, shadow, optional breathing scale. **Accepts an `opacity` prop controlled by the beat's `show_presenter` field.** Fade in/out over 0.3-0.5s using Remotion's `useCurrentFrame()` + `interpolate()`. When hidden, the presenter takes zero visual space — the full background animation fills the canvas.
- `src/Subtitles.tsx` — reads `transcript_bilingual.json`, renders verbatim bilingual captions (source language on top, larger; translation below, smaller) at correct times
- `src/BackgroundScene.tsx` — renders the semantic visual for the current beat. **Fills the ENTIRE 1080×1920 canvas (not just a portion).** Uses depth layers (background → midground → foreground) to create spatial richness. Should feel like a cinematic vertical world, not a corner decoration.
- `src/Composition.tsx` — main composition, 1080×1920, 30fps, layers in order

Layer order (bottom to top), ALL layers are full-canvas unless noted:
1. Background scene (animated graphics — FULL CANVAS)
2. Content images (if any, max 2 — can be large, not thumbnails)
3. Graphic labels and data overlays (large-scale typography, significant screen real estate)
4. Verbatim subtitles (lower safe area only)
5. Presenter circle (center-right — floating overlay on top of the scene)

### Step 8 — Implement scenes per beat

For each beat in `storyboard.json`, create a visual scene that matches its `semantic_purpose` and `animation_events`. Follow `references/visual-standard.md` for the semantic mapping.

Key rules:
- **Canvas scale: animations must occupy significant portions of the 1080×1920 frame.** Use the full width and height. Large typography, sweeping camera pushes across the full vertical space, parallax layers that span edge to edge. Avoid small isolated elements floating in empty space.
- **Depth architecture: every scene needs at minimum 3 spatial layers** — background (atmosphere, gradients, subtle motion), midground (primary visual element like a chart, model core, node map), foreground (sharp data callouts, large labels). Each layer fills the canvas independently.
- **Language rule: ALL on-screen graphic text in Remotion components (`<div>`, `<span>`, `<p>`, labels, chart axes, data callouts, UI mockups, scene titles) must be written in `$SRC_LANG`.** If `$SRC_LANG` is `"zh"`, every graphic label is Chinese. If `$SRC_LANG` is `"en"`, every graphic label is English. Never default to English for a non-English video.
- Animations start 0.1-0.2s before their keyword
- Hold a coherent visual world for 3-8 seconds (not one per SRT line)
- Vary intensity: high for hook/data/turn/conclusion, low/medium for explanation
- Use continuous spatial motion (camera push, parallax, layer reveal) instead of hard cuts
- Short beats get one clear action, not a pile of effects
- Presenter circle may slightly overlap background elements — this creates depth, not a bug
- **Presenter toggle: use `show_presenter` from the storyboard to control visibility per beat.** Fade out the presenter when the focus shifts to a full-screen visual (data chart, product image, comparison). Fade back in for personal testimony, hook, and call-to-action. Beats without the presenter should feel immersive and cinematic — the whole canvas belongs to the visual story.

### Step 9 — Render low-res preview

```bash
npx remotion render Composition output/preview.mp4 --scale=0.5
```

Extract contact sheet:
```bash
python3 "$SKILL_DIR/scripts/video_pipeline.py" verify \
  --source input.mp4 --output output/preview.mp4 \
  --srt work/transcript.srt --out work/preview-check
```

### Step 10 — Approval gate 2: preview

**STOP HERE.** Show the user:

1. Preview video path
2. Contact sheet at `work/preview-check/contact-sheet.jpg`
3. Any issues found (black frames, subtitle clipping, presenter drift, missing cues)
4. Ask: **预览已生成，请检查。回复"继续渲染"输出成片，或指出要改的问题。**

If the user reports issues, fix them and re-render the preview. Do not proceed to full render until approved.

### Step 11 — Final render

```bash
npx remotion render Composition output/final.mp4 --codec=h264
```

### Step 12 — Verify

```bash
python3 "$SKILL_DIR/scripts/video_pipeline.py" verify \
  --source input.mp4 --output output/final.mp4 \
  --srt work/transcript.srt --out work/verification
```

Check:
- Resolution is 1080×1920
- Both video and audio streams present
- Duration matches source (within tolerance)
- All subtitle cues accounted for
- No black/broken frames in contact sheet
- Presenter circle stable and in correct position
- Subtitles not clipped or overlapping presenter
- Original voice audible and synchronised

### Step 13 — Report

Tell the user:

```
✅ 成片已完成

📁 文件：output/final.mp4
⏱ 时长：X分X秒
📐 分辨率：1080×1920
🎵 音轨：原始口播声音
📝 字幕：X条（来源：SRT / Whisper识别）
🖼 图片：X张（来源：xxx）
🔍 验证：通过

🔁 重新渲染：
npx remotion render Composition output/final.mp4 --codec=h264
```

---

## Visual defaults

Refer to `references/visual-standard.md` for the full specification. Quick reference:

- **Canvas**: 1080×1920, 9:16, 30fps, H.264 + AAC
- **Palette**: graphite/black-blue background, cool white text, cyan-blue emphasis, warm gold for turns, orange/red sparingly for warnings
- **Presenter**: circle at center-right, cool-white rim, blue-purple edge light, soft shadow, subtle 1.00-1.025 breathing scale
- **Subtitles**: lower safe area, bilingual (source language on top bold white ~28px, translation below ~18px light grey), max 1 line each, keyword emphasis (cyan/gold) on source-language line only, dark semi-transparent backing, no karaoke bounce
- **Images**: max 2 total, only when directly relevant, always with source attribution

## When blocked

- **No audio stream**: stop, don't fake it
- **Low-confidence transcription**: highlight all uncertain items, ask user to correct
- **Whisper not installed**: install it (free, local), don't use a paid API unless the user approves
- **Remotion not installed**: tell the user to run `$skill-installer remotion` first
- **Wrong image claim**: use an abstract graphic instead of a fake screenshot
- **Render error**: read the error, fix the code, re-render, don't give up after one failure
