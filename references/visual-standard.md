# Visual and Editorial Standard

Use this reference while writing the storyboard and implementing scenes.

## Editorial hierarchy

1. The spoken argument is primary.
2. Exact, readable subtitles are secondary.
3. Visual explanation supports comprehension.
4. Decoration is last and should be removed when it competes with meaning.

**Language rule:** All on-screen graphic text (labels, chart text, data overlays, callouts, UI text, scene titles) must be written in the detected spoken language (`$SRC_LANG`). Never generate Remotion visual labels in English for a non-English source video. Example: for a Chinese (`zh`) video, every `graphicLabel` string, every `<span>` inside a scene must be in Chinese.

## Semantic visual mapping

| Spoken concept | Prefer | Avoid |
|---|---|---|
| AI/model/parameters | spatial model core, connected nodes, restrained code/data grid | glowing brain, generic robot |
| coding/Codex | truthful editor/terminal/file-tree structure, execution/test feedback | fake unreadable code rain |
| performance/growth | spatial chart, stepped nodes, increasing gauge | arbitrary rocket |
| price/cost/token | meter, invoice structure, descending curve, numeric transition | unsupported fake prices |
| near-zero/free | descending sequence ending in a ring/zero, with caveat where needed | asserting free without evidence |
| company/competition | abstract product/system cards or approved real logos | fabricated executives or political flag fights |
| open/open weights | connected/open structure, weights-to-deployment flow | claiming open means zero cost |
| compute/server/network | real or abstract GPU rack, node map, data pulse | fantasy sci-fi server rooms |
| evidence/news/product | supplied/official screenshot with source note | fabricated article screenshot |
| comparison | one spatial world transforming between states | repetitive hard-cut split screens |

## Beat design

- Derive beats from meaning, not SRT line count.
- Usually hold a coherent visual world for 3–8 seconds.
- Start a visual transition 0.1–0.2 seconds before its keyword only when it helps anticipation.
- Give a sub-one-second cue one clear action, never a stack of effects.
- Strength should vary: conflict/data/turn/conclusion may be high; explanation is low or medium.
- Reuse a spatial motif to maintain continuity rather than resetting the entire screen.
- **Vertical rhythm: design for the 1080×1920 canvas.** Use the full height — push objects from bottom to top, cascade layers vertically, place key elements in the upper third and lower third with breathing room in between. Avoid centering everything; off-center placement with generous scale creates cinematic tension. Think of each beat as a vertical composition, not a landscape one squeezed into portrait.
- Minimum 3 spatial layers per beat. The presenter circle is not a layer — it's the final overlay.

## Presenter composition

- Default circle center around x=68–73% and y=43–52% of the canvas; adapt after inspecting source framing.
- Default diameter 20–25% of canvas width.
- Keep facial proportions unchanged.
- Prefer a stable crop. Tracking is allowed only when it improves framing without visible jitter.
- **Canvas rule: the presenter is a floating overlay, NOT a hard split.** BackgroundScene covers the ENTIRE 1080×1920 canvas — top to bottom, left to right. Never confine animations to one side to "make room" for the presenter. The presenter sits on top of a full-screen animated world, like a broadcast overlay, not a split-screen video call.
- **Presenter visibility is per-beat.** The presenter circle is NOT shown continuously. Fade it in (0.3-0.5s opacity) for key moments: hook, personal testimony, emotional peak, call-to-action. Fade it out when the viewer's attention should be on a full-screen visual. In a 2-minute video, the presenter should be visible for roughly 40-60% of the runtime. When absent, the full canvas belongs to the animation.
- Motion graphics should occupy significant portions of the canvas, using the full vertical height (1920px) and full width (1080px). Think widescreen cinematic composition adapted to vertical — sweeping camera moves, large-scale typography, deep parallax layers that fill the frame.
- The presenter circle may occasionally overlap with background elements — a slight overlap adds depth and feels intentional, not like a mistake.

## Subtitle integrity

Create a programmatic reconciliation check between source cues and rendered cue data. Concatenating rendered spoken-text cues after normalization of line breaks only must reproduce the source subtitle sequence. Graphic labels are stored separately and never mixed into that check.

### Bilingual layout (default)

By default, subtitles are bilingual:

- **Source language (top)**: bold white, ~26–30px, the primary spoken language detected from the audio.
- **Translation (bottom)**: regular weight, light grey (#B0B8C4), ~16–20px, placed directly below the source line with 4–8px gap.
- Both lines share a common dark semi-transparent backing strip.
- Keyword emphasis (model names, prices, technical terms, proper nouns) uses cyan-blue or warm-gold — applied to the source-language line only, never to the translation.
- Translation must be a natural rendering of the source text, not a machine-literal gloss.

### Single-language mode

When the user explicitly requests single-language (只说中文, English only, 不要英文, no bilingual):

- maximum two lines of the detected source language;
- sensible wrapping by measured width, not character count alone.

### General styling

Subtitle styling must prioritize readability:

- lower safe area, clear of platform controls;
- subtle dark backing/shadow behind both lines as one block;
- restrained transitions such as opacity, mask reveal, or a few pixels of lift;
- no high-frequency karaoke bounce.

## Image budget

The whole video may use 0, 1, or 2 external still images. An image is justified only when it anchors a real event, product, or environment more truthfully than generated graphics. Record source URL/file and usage in the storyboard. Do not use several crops of the same image as a loophole to create an image slideshow.

## Audio

The source voice is the master track. Optional music must be instrumental, unobtrusive, and ducked below speech. Sound effects should mark meaningful transitions only and must not mask consonants or numbers.
