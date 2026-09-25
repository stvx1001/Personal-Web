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
  from `/personal-web/` on GitHub Pages today and from `/` on the custom domain
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
- **Second case study (Sept 22, 2026): `fulltimeworks/metrodataacademy/`**, from
  Figma `3950:12132` (desktop) and "Metrodata Academy page — Mobile 390". Same
  grid, nav and footer as Alomos, but in the Academy's own brand (Hedvig
  Letters Serif + Instrument Sans, blue #3056D3). The UI shown is Steven's
  *rebuild* of the homepage (`3950:12156`) — he has no original files, and the
  page says so in the credits. Keep that line; don't invent metrics for it.
  Images are `get_screenshot` renders of UI frames (1x is the cap), flattened
  onto their panel colour as JPEG.
- **Metrodata product film (Sept 24, 2026)** sits right under the 03 intro
  (`.film`, `assets/film.mp4`, 1280x720, no grain — grain costs bitrate and
  turns blocky). It follows Steven's reference video ("reference video.mp4",
  a 39s TAHL template film in `~/Downloads/MA/`) beat for beat. It plays only
  while on screen and not under reduced motion.
  **Current cut: 23s, ~6MB** (Sept 24, 2026). The live-action is two Gemini/Veo
  clips Steven generated (profile woman, sofa + laptop, students walking,
  woman at a train window, train view); they keep Gemini's ✦ watermark. What
  he rejected, and why the cut looks the way it does: an edit that laid text
  over the raw footage — "far different with my reference". The reference's
  grammar is that almost every shot is *the website* (Figma editor, image
  picker, font swap, breakpoints, Publish, then the live site with nav pill and
  thumbnail strip, page cards, floating screens); footage lives *inside* the UI
  as the hero image. He then asked for a slower pace: the 16s version was
  "too fast", so the same choreography is time-stretched ~1.4x to 23s with
  frame blending on the slowed footage. Source (`film.html` `render(t)` stage +
  `rec.mjs` Playwright capture + `sofa.py` laptop-screen tracking) was built in
  a cloud session and handed to Steven as a zip; the older 39s version's source
  is `~/Developer/Personal-Web-film/`.
- **Metrodata hero (Sept 25, 2026)** follows Figma "02 Hero" (`3953:1590`):
  a library photo (`assets/hero-library.jpg`, 2000px, the source max) under a
  black 62% → 34% → 66% wash, the white Academy logo (`logo-white.png`,
  32.86% wide = 460/1400) and "Digital learning provider — Indonesia" in
  Poppins Medium 20/28 at 86%. It replaced the homepage-in-a-browser hero.
- **Metrodata screen wall (Sept 24, 2026)**, `.wall` under the film, from
  Figma "03c Screens" (`4090:1611`): ten screens in three offset columns on
  #161618, running off every edge. Each `<img>` sits at its Figma x/y/w/h as
  a percentage of the 1400x900 stage, so it scales with the page; on phones
  the stage is 184% wide and centred on the middle column. Images are the
  raw Figma fills (`assets/wall-*.jpg`, ~2x, q82), not screenshots.
- **Third case study (Sept 23, 2026): `fulltimeworks/agriaku/`**, from Figma
  "AgriAku" (`3965:12496`) and "AgriAku — Mobile 390". It is the one with a
  different structure, at Steven's request: **three projects behind three
  cards, one panel visible at a time** (the others carry `hidden`), plus a
  **floating switcher** that slides in while a project is on screen so the
  reader can change project mid-scroll. Cards and switcher are two views of one
  state; `#bundling` / `#tempo` / `#search` deep-link a project. **The design
  system section is deliberately separate from the three feature projects**,
  and holds two dashed "Add export" slots waiting for Steven's DS exports.
  Screens are `get_screenshot` renders of his own older AgriAku frames
  (`3965:14155`, `3965:12595`, `3965:12517`), flattened to JPEG.
- **Alomos tweaks (Sept 25, 2026, Steven's calls):** the bento is 48px padding
  with 32px gaps on desktop (16/16 on phones); "Secure payment" has a white
  lock inside its ring (`assets/icon-lock.svg`); the persona carousel holds
  1.8s (was 3.8s); each Design-in-detail panel wraps screen + notes in one
  centred `.screen-wrap`, 40px apart, notes hugging at 460px instead of
  filling. The "Added to cart" check was stuck at the top of its circle
  because `.t-cart span` also hit the badge `<span>` — caption rules are now
  scoped to `.t-cart div span`.
- **Alomos no longer has Design system or Outcome sections** (Sept 25, 2026,
  Steven deleted 08 and 09 in Figma, desktop and mobile); the page ends
  Design in detail → mockup → scroll video → footer. The scroll video is now
  60fps: the 15fps source was motion-interpolated with ffmpeg `minterpolate`
  (mci/aobmc/bidir), x264 crf 16, BT.709, faststart — `imageio-ffmpeg` via
  pip provides an ffmpeg in the cloud container.
- **Case-study margins are a flat 24px at every width** (Sept 23, 2026): `.page`
  and `.nav` are `calc(100% - 48px)` with **no max-width cap** — the old
  `min(1400px, …)` / `min(1248px, …)` made the margin grow on screens wider
  than ~1450, which is what Steven was seeing.
- **The case-study navbar is the home navbar's box** (Sept 24, 2026, Steven's
  call): `width:min(1248px, 100% - 2*clamp(24px,6.6vw,96px))`, padding 8/16,
  radius 16 → 32 when stuck — so on wide screens the nav sits in the home
  page's 1248px column while the content below still runs 24px from the edge.
  Phones (≤640px) keep the nav on the 24px content edge.
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
- For headless-Chrome checks of a case study, load it as a `file://` URL.
  Serving it with `python3 -m http.server` randomly failed image requests
  while the page's videos streamed, which looked like broken images.
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
- **Coming back from a case study restores the scroll position** (Sept 24,
  2026, Steven's call). `pagehide` saves `scrollY` in sessionStorage;
  `restoreReturn()` puts it back when the load is a Back/Forward or the
  referrer is a `/fulltimeworks/` page (the back arrow is a plain link, not
  history). A reload still starts at the top. A spot inside the stepped intro
  lands on the stage at or above it, with `stage`/`locked` set to match.
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

## The Works rail drags (Sept 23, 2026)

On pointer devices the home page's Works rail is **dragged with the mouse**, so
the CSS marquee hands over to a small rAF engine (`.rail--drag`, right after the
cards are rendered): same drift speed as the CSS (one card set per 46s), pointer
drag on top, momentum on release, and a wrap at half the track width — which is
why the card set is still in the DOM twice. A drag of more than 6px swallows the
following click, so dragging never opens a case study. **Do not call
`setPointerCapture` or `preventDefault()` on that pointerdown** — either one
retargets the click to the rail and the card never opens (that bug shipped once;
the move/up listeners live on `window` instead). With JS off, the CSS
marquee still runs. Below 760px that engine bails out (dragging a native
scroller fights the browser's own gesture) and a separate phone engine (5c)
takes over (Sept 24, 2026, Steven's call — he wanted it moving on phones
too): the rail is a native horizontal scroller with **no scroll-snap**, the
script drifts `scrollLeft` at the same one-set-per-46s speed and wraps it by
one card set inside [period/2, 1.5×period) so a swipe works both ways. Touch
pauses it; it resumes 1.5s after the swipe and its momentum settle, and the
wrap waits too, because setting `scrollLeft` mid-fling kills iOS momentum.

## Typography — one family, site-wide

**Radio Canada Big is the typeface for everything Steven's** (Sept 23, 2026, his
call): home page, every case study, and every Figma frame of them. Use it for
anything new — don't introduce a second family. Web:
`https://fonts.googleapis.com/css2?family=Radio+Canada+Big:ital,wght@0,400..700;1,400..700`.
**It stops at 700**, so the old 800/900 weights are now 700; in Figma its styles
are Regular / Medium / SemiBold / Bold (+ italics). The `--display`, `--poster`,
`--serif` and `--inter` variables still exist on the pages but all alias the one
family, so old rules keep their sizes.

**Process/stage cards were removed from both Alomos and Metrodata (Sept 24,
2026, Steven's edit in Figma, mirrored on the live pages and the mobile frames)**,
along with Metrodata's section headers (Audiences, Design in detail, Design
system, Outcome). If process cards come back, the agreed scale was number 44
bold #000, title 18 #000, body 14 #485359, with white text on a coloured card.

**Case-study text colours (Sept 23, 2026, Steven's call — case studies only,
never the home page):** every title, headline and section header is **#000**;
every subtitle, lead and body paragraph is **#485359**. On the Alomos page that
made `--text` and `--black` #000 and moved `.t-lead` onto `--text-2`; on the
Metrodata page `--ink` is #000 and `--body` #485359. Colour *tokens documented
inside a case study* (e.g. the Academy's own "Body #5C5C5C" swatch) are content
— leave them. Its intro title is 24/32, matching Alomos.

The home page's **marquee band is one deliberate exception on Steven's own
pages**: black (#000) with Days One, his call on Sept 23, 2026 — keep it.

The other is the **home page's Pixel Spell panel (Sept 24, 2026, Steven's
call)**: he wanted visitors to "feel the spell", so it wears the studio site's
own skin, taken from `github.com/stvx1001/pixel-spell` (`app/globals.css`,
`components/`): cream `#fbf8f2`, ink `#0d0e1a`, pink `#f2549e`, Shrikhand
headline, Geist Mono eyebrow/body, a Caveat sticker, bobbing pastel pixels,
white tilted work-card frames on the gallery tiles, and the fox from its cast
(`--img-ps-fox`, `fox-casting.png` at 600px) standing in front of the tiles.
The tokens are scoped to `.ps-panel` (`--ps-*`); nothing else on the page uses
those fonts. The logo is the studio's current `logo.svg`. The old peach
gradient, blobs and PIXEL watermark are gone. The copy column is
`minmax(0,520px) auto` so it shrinks beside the fixed-width gallery, and the
headline size follows that column (`(100vw - 952px - 4vw) / 8`, 802px ≤1300).

One more exception, in both Figma and the HTML: **type specimens inside a case
study keep the client's own typeface** — the ALOMOS ramp stays Poppins, and the
**Metrodata Academy UI is Poppins too** (Steven's call, Sept 24, 2026: every
text *inside* his rebuilt Academy UI is Poppins, while the case-study page
around it stays Radio Canada Big). The Figma frame `4004:5828` was converted,
and the six exported UI images in `metrodataacademy/assets/` were re-rendered
from it — re-export them if that frame changes again. The embedded product UI (screenshots and the
Figma clones of the Metrodata homepage) is left alone for the same reason.

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

Repo: `github.com/stvx1001/personal-web` — **public**. It was renamed from
`Personal-Web` on Sept 25, 2026; GitHub redirects the old URL, but use the new
lowercase name everywhere. Claude cloud sessions work on `claude/*` branches
and push there; `main` is the published branch.

Hosting: the repo being public means GitHub Pages can serve it on a free
account, at `/personal-web/` (the repo name, lowercase since the rename).
Vercel is where the Next.js plan is headed.

## Open items

- Pixel Spell's gallery is still gradient placeholder tiles, not the real
  photography in the Figma frame. Most obvious next asset job.
- Shop/products section not built. Three cover images exist (pixel-spell,
  stvx1001, minimal) but aren't wired in.
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
