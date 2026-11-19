# The World in One Day — 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/c/news-image-20261119)
[![Rank](https://make.fun/badge/news-image-20261119/rjrajput-web3/news-image-20261119-entry/rank.svg)](https://make.fun/c/news-image-20261119)
[![Reward](https://make.fun/badge/news-image-20261119/rjrajput-web3/news-image-20261119-entry/reward.svg)](https://make.fun/c/news-image-20261119)

A program that draws one front-page image summing up the world's news of
Thursday, 19 November 2026: the first Trump–Xi–Putin three-way summit in
Shenzhen, the World Court's Rohingya genocide-case judgment, tankers ablaze
after mine strikes in the Strait of Hormuz, Ukraine hitting the Crimean
Bridge again, unrest burning across Bangladesh, Israel's push into central
Gaza, COP31 ministers racing for a deal in Antalya, the GTA VI launch, and
Anthropic's record Nasdaq debut — plus a stats strip, a world map and an
In Brief list of the day's other news.

Run it with:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` (1024×1024 PNG). Pure Python standard library,
no network, fully deterministic — two runs write byte-identical output.

## How it is drawn

`main.py` draws the whole front page itself: a hand-built 5×7 bitmap font,
a small raster canvas, and a minimal PNG encoder (`zlib` + `struct`).
The masthead names the date, the stats strip carries the day's big numbers,
each hero panel has a drawn picture (three flags, a game controller, a
rising market chart), each story card has a short headline, a two-line
summary and a small drawn icon, and the bottom row pairs a world map with
a numbered In Brief list. Nothing is fetched or copied in at run time.
