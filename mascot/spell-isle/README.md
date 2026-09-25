# Spell Isle — footer diorama

Isometric island for the Pixel Spell footer (Figma: SkorKu file, Ref page, Footer → "Spell Isle").

- `isle.py` draws it as a flat SVG (fills + linear gradients only, so Figma imports editable vectors)
  and writes `anchors.json`: the feet point of each mascot on the island's grid.
- `preview.py` + `render.mjs` composite the mascot cutouts (`../*/`) over the SVG in headless Chromium
  (`node render.mjs $PWD/preview.html $PWD/preview.png 1440 1000`) — iterate here, not in Figma.
- In Figma the mascots are component instances placed with the same math:
  box x = anchor x − 200·k, box y = anchor y − 384·k, k = size / 400.

## Campfire (About section)

`camp.py` reuses the island helpers to draw the About illustration: a grass chunk with a stone ring,
log teepee, brand-colour flames, pixel embers and a firewood pile. `camp_items.json` places the mascots
and props (Fox staff, Cat sword) — in Figma they are component instances in the "Campfire" frame
(SVG shifted up 150px to crop the empty sky). Preview: `python3 camp_preview.py && node render.mjs
$PWD/camp_preview.html $PWD/camp_preview.png 600 640`.
