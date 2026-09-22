# CLAUDE.md — Steven Charlino personal site

Handoff from the Cowork session that built this prototype (Sept 14–16, 2026).
Read this before changing anything in `index.html` — most of what's below was
learned the hard way and is easy to break by accident.

## What this is

Steven Charlino is a Product Designer in Jakarta (CBI, previously TADA, AgriAku,
Metrodata). This is the prototype of his personal site: portfolio, CV download,
and a shop for his MINIMAL UI kit. `index.html` is one self-contained file —
markup, CSS and JS together, no build step. Open it in a browser.

Deliberate for a prototype. **Not** the production architecture — the plan is
Next.js 15 + `motion` + Lenis + Tailwind v4 + MDX on Vercel. Treat this file as
the reference for how the page looks and behaves, not as the target structure.

Sections in order: navbar · banner/hero · Pixel Spell · MINIMAL · marquee ·
works rail + client logos · Hire Me · A Little About Me (stat cards) · footer.

## Case-study pages

Each project gets its own directory, mirroring the URL it will have on the
custom domain:

```
fulltimeworks/alomos/index.html   → /fulltimeworks/alomos/
fulltimeworks/alomos/assets/      → its images (real files, not base64)
```

- **Every path is relative** — no leading slash, anywhere. The site is served
  from `/Personal-Web/` on GitHub Pages today and from `/` on the custom domain
  later; relative paths work in both with no edits. The case study links home
  with `../../`; the Works card links in with `fulltimeworks/alomos/`.
- **Works cards link via a 4th field** in the `projects` array in `index.html`
  (`['Alomos', 'e-Commerce Web', 'w-alomos', 'fulltimeworks/alomos/']`). With it
  the card renders as an `<a>`, without it as a plain `<article>`. Adding the
  next case study is: make the directory, add the 4th field.
- **Assets are files, not base64**, unlike the main page. A case study is
  image-heavy; files cache and keep the HTML small. Same rules otherwise: JPEG
  q82 for opaque photos, PNG only when the image truly needs transparency
  (measure it — several Figma PNGs report alpha but are fully opaque), ~2x the
  rendered width, **never upscaled** (`sips --resampleWidth` will happily
  upscale; check the source width first).
- **Video**: Steven supplies it (he drops files in `~/Downloads/assets`). Use
  `<video autoplay muted loop playsinline>` with a `poster`, never a GIF: his
  two Alomos GIFs were 16.5MB and 14MB and became 1.0MB and 2.6MB MP4s.
  **Watch for Figma disguising animation:** it exported both GIFs as `.png`
  (same byte count), so an image that looks like a still may be a GIF — check
  the frame count before flattening it. No ffmpeg on this Mac: convert with an
  AVFoundation `AVAssetWriter` Swift script, and **encode at 16-pixel-aligned
  dimensions** (1280x768, not 1400x840) with BT.709 colour tags. Strip audio
  from muted loops and set `shouldOptimizeForNetworkUse` so it streams.
- **Page transition** home ⇄ case study is a cross-document View Transition:
  `@view-transition{navigation:auto}` on *both* pages. The arriving page owns
  the animation — the case study defines "rise from the bottom over a still
  home page", the home page defines the reverse "drop away and reveal home".
  Both set `mix-blend-mode:normal` on the old/new layers (the UA default,
  plus-lighter, washes the overlap to white). Chrome/Edge/Safari animate it;
  others just navigate. Off under `prefers-reduced-motion`.
- **Verifying either of the above: the in-app Browser pane can't.** It does not
  run cross-document view transitions at all (a bare two-page test fails), and
  it can't capture playing `<video>` frames — even Steven's own untouched MP4
  screenshots as a blank box. Don't debug encodes or CSS against it. Use real
  headless Chrome (`/Applications/Google Chrome.app`, with a throwaway
  `--user-data-dir`) driven over CDP from Node 24's built-in WebSocket: inject a
  `pagereveal`/`pageswap` probe with `Page.addScriptToEvaluateOnNewDocument`,
  click with `Input.dispatchMouseEvent`, and `Page.captureScreenshot`
  mid-transition. For video, prove playback by drawing the `<video>` to a canvas
  twice and diffing the pixels.
- Each page is self-contained (its own `<style>`), matching the main page. A
  shared stylesheet belongs to the Next.js migration, not this prototype.
- **Phone layout (Sept 22, 2026)** follows the Figma frames "Home — Mobile 390"
  and "Alomos Page — Mobile 390" (SkorKu file, page "Sum", right of the desktop
  frames). Both pages now have `<meta name="viewport">`. Below 760px the home
  page runs **unpinned** (`body.no-pin`, via `noPin = reduce || phone` in the
  script, decided on load): the stepped intro hijacks touch scrolling and its
  100vh stages jump with the phone address bar. Desktop and tablet keep the
  pinned intro. The Alomos process map has a separate phone chain (`.flow-m`)
  because the scaled 700x900 drawing is unreadable at 0.5x.
- Screenshotting a full page in headless Chrome by growing the viewport to the
  page height inflates every `vh` (the Hire Me section becomes 8000px tall). Pin
  those heights with injected CSS for the capture; it is not a real bug.

## The scroll interaction — read this before touching the JS

This is the most fragile and most iterated part of the build. Steven rejected
three earlier attempts; the current behaviour is what he signed off on.

**It is STEPPED, not a continuous scroll-scrub.** The Figma storyboard frames
are discrete states. One gesture advances one stage and then *holds*. Building
it as a continuous scrub (expansion spread over screens of scrolling) reads as
"nothing is happening" — that exact mistake was made and rejected twice.

Stages:

| Stage | State | How you get there |
|---|---|---|
| 0 | Banner as a rounded card, headline + 3 float cards visible | initial |
| 1 | Pixel Spell filling the viewport | **one gesture**, chained (see below) |
| 2 | MINIMAL filling the viewport | one gesture |
| — | released to native scroll + inertial glide | one more gesture |

**Stage 0 → 1 is one gesture but two beats:** the banner grows to full screen
(720ms), holds 260ms so the full-bleed state actually reads, then carries itself
into Pixel Spell (680ms). Steven asked for this explicitly — originally it was
two separate gestures. Reversed on the way back up.

### Implementation, and why each piece is the way it is

- **A `requestAnimationFrame` loop drives everything — never scroll events.**
  When the page is embedded (artifact iframe, preview pane, any `overflow:auto`
  wrapper) the scrolling element isn't `window`, so a `window` scroll listener
  never fires and every effect silently dies while the page still scrolls. It
  looks exactly like "the animation is broken". The loop measures
  `getBoundingClientRect()` on the elements themselves, so it doesn't care what
  scrolls. Keep it that way.
- **Gestures are detected by accumulated delta, not by pauses between events.**
  A trackpad fires one unbroken stream of wheel events per swipe, so "wait for a
  gap" never fires while the user keeps swiping — the page feels frozen and
  blocks native scroll at the same time. Thresholds: 24 (wheel), 40px (touch).
  `quietUntil` (220ms after each transition) absorbs the momentum tail so one
  swipe can't run through several stages.
- **Testing momentum: Playwright's `mouse.wheel` cannot reproduce it** — CDP
  latency between calls exceeds any realistic gap threshold, so the bug hides.
  Dispatch `WheelEvent`s in-page at ~10–14ms intervals with a decaying tail.
- **Banner expansion** interpolates `width/height/top/left/borderRadius` with
  smoothstep easing. Start values are derived from the viewport each frame, so
  it's resolution-independent.
- **The headline fades late — 45% → 80% of progress.** It must stay sharp
  through the first half. Fading it early was a rejected version.
- **The headline is counter-translated** by `drift = vh - (startTop + startH)`,
  because it's anchored to the banner's bottom edge, which moves down as the
  banner grows. Without this it visibly slides down during the expansion.
- **The dot grid stays visible** on the full-bleed banner. Don't fade it out.
- **The navbar pill turns on at `p > 0.32`**, i.e. when the growing banner
  reaches up behind it — not at a fixed scroll offset.
- **Every handoff — banner → Pixel Spell → MINIMAL — is one pure-CSS sticky
  stack.** Each panel is `position:sticky; top:0` inside its own tall wrapper,
  and each wrapper carries `margin-top:-100vh`, which slides it up over the
  last screen of the previous section's sticky range. So the section you are
  leaving *stays pinned* while the next one travels from the bottom edge to the
  top edge in front of it — it never scrolls away underneath. Each panel is
  *later in the DOM* than the one it covers — mirroring the Figma layer order —
  so it paints on top with no z-index. No JS involved. **That DOM order and
  those negative margins are the mechanism; don't "fix" either.**
- **Inertial smooth scrolling after release** (`LERP = 0.11`, lower is heavier).
  Written inline rather than pulling in Lenis so the file works with no network.
  Pointer-fine only — touch devices have native inertia and hijacking it there
  makes things worse. Reference Steven liked: fudali.studio (a Framer site).
- **`prefers-reduced-motion`** adds `body.no-pin`, which drops the whole thing
  back to plain static scrolling. Preserve this.

Stage offsets come from tall wrappers: hero pin 340vh (140vh of banner
expansion + 100vh held full-bleed while Pixel Spell covers it), Pixel Spell
230vh (130vh held + 100vh while MINIMAL covers it), MINIMAL 130vh. A gesture
tweens the scroll position to the next offset (easeInOutCubic) and the rAF
engine turns that movement into the animation. The JS reads the offsets from
the elements, so heights are safe to retune — with one exception: the banner's
expansion progress divides by `hero-pin height − 2×vh` (one screen for the
sticky stage, one for the hold), so if the hold changes, that changes too.

## Assets

**Every image is inlined in `index.html` as a base64 data URI** on a CSS
variable — there is no `assets/` directory any more, and no build step:

```css
--img-work-agriaku:url("data:image/jpeg;base64,…");
```

Groups: `work-*` (Works cards) · `logo-*` (client marks) · `minimal-*` (UI kit
screens) · `ps-*` (Pixel Spell gallery + watermark) · `pixelspell-logo` ·
`banner-*` (hero float cards).

Photographs go in as **JPEG q82**, UI screenshots and anything needing
transparency as **PNG**, both at roughly 2x their rendered size. This matters:
the Works card photos were 6 MB as PNG and are ~670 KB as JPEG with no visible
difference. `index.html` is ~8 MB; keep an eye on it.

**Never source assets from Figma via `get_screenshot`.** It bakes layer effects
(blur) into the pixels. Steven caught this and was clear about it: download the
raw asset and reapply the effect in CSS. The three banner float cards use raw
unblurred exports with `blur(1.5px)` / `blur(2.5px)` and `rotate(13.3deg)` on
Activity, sitting *behind* the dot grid.

`get_design_context` returns real asset URLs (`…/api/mcp/asset/…`) that you can
`curl` directly — no extra MCP call per file, which matters given the quota
below. They expire in ~7 days, so download and inline them the same session.
Steven often exports the same art himself into `~/Downloads`; prefer his files
when they are clean 2x crops, and **copy them to scratch immediately** — they
have vanished mid-task more than once.

## Figma

Current file: `zoJDbi6xzrKatioVqaC0xZ` ("01-Full-time-Design-Experience"),
page `1234:2` ("Personal Web v4"). An older file `4yBT1At7HkP6UN31TyrwBR` is
superseded — ignore it.

Scroll storyboard: section `2376:1056`, frames `2377:1358` (Home) →
`2377:1656` → `2377:1954` → `2377:2251` → `2377:2549`.
**Frames `2377:2251` and `2377:2549` were never inspected** — the MCP quota ran
out first. The interaction was reconstructed from the first three plus two
screen recordings Steven made.

**Access is tight, and the account matters.** The Figma MCP here is the *local
desktop-app* server — it authenticates as whoever is signed into the Figma
desktop app, not via a separate OAuth connector. The personal file above is
owned by `steven.charlino@gmail.com`; when the app was signed in as his work
account `steven.charlino@cbi.id`, **every** call (`get_design_context`,
`get_metadata`) failed with *"you don't have edit access to this file"*. That
error means the wrong account is signed in, not that the quota ran out — check
`whoami` first, and fix it by switching accounts in the Figma desktop app.

**Writes DO work** (Sept 21, 2026): `use_figma` successfully rebuilt a frame in
the SkorKu file despite `whoami` reporting `seat: "View"` everywhere, so the old
"Starter = read-only, no use_figma" note here was wrong.

**The call cap is real, though — budget hard.** Roughly 20-25 calls exhausted it
in one day and the next call failed outright with *"You've reached the Figma MCP
tool call limit on the Starter plan."* Every call counts: reads, writes, failed
calls and `whoami` alike. When it runs out there is no workaround but upgrading
or waiting for the reset, so **ask Steven for PNG exports instead of browsing
the file** — he exports quickly and does it happily, and it costs nothing.

Two real limits, both hit in practice:
- **`get_design_context` on a *section* returns sparse structure-only metadata**,
  and on a whole *page* it fails outright ("nothing selected"). Aim at a frame.
- **`get_metadata` on a big page breaks the transport** — the XML exceeds the
  SSE buffer and dies with a JSON parse error at ~123KB. When you cannot
  enumerate a page to find a node by name, `get_screenshot` the whole thing at a
  high `maxDimension`, download it, and crop locally with
  `sips -c H W --cropOffset Y X`. That found a reference image in one call where
  metadata could not.

### Building a page from a tall Figma frame

For something like the Alomos page (1440x13016): `get_design_context` on the
whole frame truncates at ~100KB, so call it per section node and save the
output. For the visual, one `get_screenshot` at `maxDimension` equal to the
frame height gives a 1:1 render; slice it with a small Swift/CoreGraphics
script (`CGImage.cropping(to:)`). **Don't use `sips --cropOffset` on tall
images** — it produced slices from the wrong offsets.

### The SkorKu file

`YUZMDH5kqna1441GZLvRPm` ("01. SkorKu Website 3.0"), page `3448:38297` ("Sum").
Despite the name it holds the **personal site** mockup too: frame `3854:1595`
("Home") is the full page, with children Navbar / Banner / Featured / Marquee /
Works / Hireme / Currently / Footer. **`Home` has `layoutMode: "NONE"`** — the
sections are absolutely positioned, so if you change one section's height you
must move every sibling below it and resize `Home`, or it silently overlaps.
That bit the Currently rebuild (76px into the Footer) and was fixed by hand.

Also on page "Sum": `3877:2487` is the **Alomos case study** design, built as
`fulltimeworks/alomos/`; `3867:2494` is the full ALOMOS project archive (design
system, storefront pages, marketing shots) to pull assets from.

Steven's prototype recordings are `.mov`. Extract frames with ffmpeg rather than
guessing — `ffmpeg -i in.mov -vf "fps=2,scale=620:-1,tile=4x4" -frames:v 1
grid.png` gives a readable contact sheet in one image. Note his Figma prototype
timing is Smart Animate transition timing, not scroll-linked: match the sequence
of states, not the literal seconds.

## GitHub and hosting

Repo: `github.com/stvx1001/Personal-Web` — **private**, and empty as of this
handoff. This folder's first commit is ready to push:

```bash
git remote add origin https://github.com/stvx1001/Personal-Web.git
git push -u origin main
```

Don't create files through GitHub's web UI before that first push — it makes the
histories diverge and the push gets rejected.

Hosting: GitHub Pages does **not** serve private repos on a free account
(needs Pro/Team/Enterprise). So either make the repo public, or use Vercel,
which deploys private repos on its free tier and is where the Next.js plan is
headed anyway.

## Open items

- Pixel Spell's gallery is still gradient placeholder tiles, not the real
  photography in the Figma frame. Most obvious next asset job.
- Shop/products section not built. Three cover images exist (pixel-spell,
  stvx1001, minimal) but aren't wired in.
- Instagram handle never provided.
- Works: Figma's base frame omits the Alomos card label, though all five hover
  frames have it — implemented as present. Worth confirming with Steven.
- The PointStar client mark is only a 440x160 export; fine at its 220x80 box
  but there is no headroom above 2x.
- NDA status on the CBI (SkorKu / ASWA) work is unresolved and blocks the case
  study template.
- Domain undecided: `stevencharlino.com` vs `charlino.design`.
- STVX1001 appeared in an old wireframe but not the current design — dropped or
  still coming, unconfirmed.

## Working with Steven

He's a designer, not a developer — new to git, and said so. Explain in plain
terms and don't assume CLI comfort. He asked for direct answers without long
preamble, and that preference is worth keeping.

He gives precise visual feedback and will tell you when something is wrong, but
not always why — when he says an interaction "has no effect," verify the
mechanism yourself rather than assuming it's a settings issue on his end. That
mistake cost a round trip here: the real cause was a `window` scroll listener
that never fired.
