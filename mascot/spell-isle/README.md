# Spell Isle — footer diorama

Isometric island for the Pixel Spell footer (Figma: SkorKu file, Ref page, Footer → "Spell Isle").

- `isle.py` draws it as a flat SVG (fills + linear gradients only, so Figma imports editable vectors)
  and writes `anchors.json`: the feet point of each mascot on the island's grid.
- `preview.py` + `render.mjs` composite the mascot cutouts (`../*/`) over the SVG in headless Chromium
  (`node render.mjs $PWD/preview.html $PWD/preview.png 1440 1000`) — iterate here, not in Figma.
- In Figma the mascots are component instances placed with the same math:
  box x = anchor x − 200·k, box y = anchor y − 384·k, k = size / 400.
