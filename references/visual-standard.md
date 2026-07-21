# Visual and Editorial Standard

Use this reference while writing the storyboard and implementing scenes.

## Editorial hierarchy

1. The spoken argument is primary.
2. Exact, readable subtitles are secondary.
3. Visual explanation supports comprehension.
4. Decoration is last and should be removed when it competes with meaning.

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

## Presenter composition

- Default circle center around x=68–73% and y=43–52% of the canvas; adapt after inspecting source framing.
- Default diameter 20–25% of canvas width.
- Keep facial proportions unchanged.
- Prefer a stable crop. Tracking is allowed only when it improves framing without visible jitter.
- Keep important motion graphics mainly in the left/center-left field.

## Subtitle integrity

Create a programmatic reconciliation check between source cues and rendered cue data. Concatenating rendered spoken-text cues after normalization of line breaks only must reproduce the source subtitle sequence. Graphic labels are stored separately and never mixed into that check.

### Bilingual layout (default)

By default, subtitles are bilingual:

- **Chinese (top)**: bold white, ~26–30px, the primary spoken language.
- **English (bottom)**: regular weight, light grey (#B0B8C4), ~16–20px, placed directly below the Chinese line with 4–8px gap.
- Both lines share a common dark semi-transparent backing strip.
- Chinese keywords (model names, prices, technical terms, proper nouns) may use cyan-blue or warm-gold emphasis — applied to the Chinese line only, never to English.
- English line must be a natural translation of the Chinese spoken text, not a machine-literal gloss.

### Single-language mode

When the user explicitly requests Chinese-only (只说中文, 不要英文):

- maximum two lines of Chinese;
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
