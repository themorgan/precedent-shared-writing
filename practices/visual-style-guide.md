---
slug:        visual-style-guide
title:       A project's look is four repo-local practices in a fixed shape, with the style guide generated from them
tier:        on-demand
severity:    default
applies_to:  ["local/practices/visual-*.md", "**/VISUAL_STYLE_GUIDE.md", "**/*.html", "**/*.svg", "**/*.css"]
occasion:    "writing down a project's logo, colors, fonts or imagery, or changing its style guide"
gates:       ["push"]
index_clause: "a project's look is four local practices in one shape; the guide is generated"
index_required: false
checked_by:  tools/checks/check_style_guide.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       "2026-09-30"
approved_by: "Morgan F, 2026-09-30: \"Shared-writing is fine, go\" (strength: decided), after a brainstorm on standardizing the format of a project's visual style guide"
strength:    decided
---
## Rule
**A project that has a visual identity writes it down as four repo-local
practices, with these exact slugs, and never as a hand-written document.**
The values are the project's own; the shape below is shared, so every
project's guide reads the same way and the same check can hold each one to
its own values.

- **`visual-logo`**: opens with `**The mark is NAME:**` and one sentence on
  what it looks like. Then a `| File | Use |` table, with at least a light,
  a dark and a small-size row, each linking the file. Then one bold-led line
  each for **Two colors** (or however many), **One color**, **Smallest
  size** (in px), **Clear space**, **Lockup** and **Don't**. If sketches
  live beside the finished files, a line in exactly this form:
  `**Sketches:** files in `<folder>/` not named `<prefix>*` are exempt from the color and type rules.`
- **`visual-palette`**: a `| Name | Light | Dark | Use |` table, every
  Light and Dark cell a six-digit hex in backticks. Then either
  `No gradients.` or `Gradients allowed.` on a line of its own. Its
  `applies_to` names the files that count as finished visual work; that is
  what gets checked.
- **`visual-type`**: a `| Role | Face |` table, each face in backticks,
  with at least a headings row and a body row, and a line saying where the
  faces come from and whether they are free.
- **`visual-imagery`**: bullets, at least one opening `**Show` and at least
  one opening `**No` or `**Avoid`.

**The style guide is generated, never edited:**
`python3 tools/checks/check_style_guide.py --write` builds
`content/VISUAL_STYLE_GUIDE.md` (or `VISUAL_STYLE_GUIDE.md` at the root
when there is no `content/`) from the four `## Rule` sections, in the order
Logo, Color, Type, Imagery, with the light logo on top and a status line
taken from the logo practice's approval. Change a practice, then regenerate
in the same commit.

The check refuses a missing or misshapen practice, a stale guide, a color
outside the palette or a gradient where the palette says none, a font
outside the type table, and a logo shown smaller than its smallest size.
**Whether an image is on-brand, or the logo was stretched, is still
judgment**: read `visual-imagery` and `visual-logo` before making either.

## Detail
**Where the values live.** In the project's own repo-local set (the
`repo-local` source in its `precedent.json`, normally `local/practices/`).
Never here: a hex code belongs to one project, and a shared set holding one
would check every other project against it. A project with no visual
identity has none of the four files, and the check skips it.

**What is checked, and against what.** Every file the palette's
`applies_to` matches, minus the sketches:

- a hex color outside the palette's Light and Dark columns (three-digit
  forms count only where a color is set, so `href="#top"` is not read as
  one);
- a CSS or SVG gradient, when the palette says `No gradients.`;
- a Google Fonts family loaded, or the first face of a `font-family`, not
  in the type table (fallbacks after the first face are fine);
- an `<img>` of a logo file other than the small-size one, with a `width`
  or `height` under the smallest size.

**What the generator does with links.** A link the practices write as a
full GitHub URL into the same repository (they do, because materialized
copies move) becomes a relative link in the guide, so it works on whatever
branch the guide is read from.

**Extra sections.** A project that wants more (icons, charts, motion) adds
a `visual-<topic>` practice of its own. The guide does not include it and
the check does not read it; point to it from `visual-imagery` if a reader
needs it.

**The upstream entry point.** Precedent installs a `project-visual-identity`
practice in every repo. Once the four practices exist, its `## Detail`
points at each of them rather than repeating them.

## Why
Every project's style guide was going to be written from scratch, in its
own shape, and checked (if at all) by its own scripts. A fixed shape means
one generator, one check and one way to read any project's guide, and it
keeps the guide in step with the rules sessions actually load, because the
guide is built from them.

## Story
2026-09-29: one project picked a logo, had a one-page style guide
hand-written, and within the hour chose to make it practices with checks,
with the guide generated from them; its own mockup sheet had already
drifted to two grays outside the palette the same day. 2026-09-30: Morgan
asked for that format to become a shared standard every project follows,
with the first project updating its own practices to match. This file is
that standard, generalized: the project's own names, colors, file prefixes
and paths became things each project declares.
