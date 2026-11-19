# The World in One Day — 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/c/news-image-20261119)
[![Rank](https://make.fun/badge/news-image-20261119/rjrajput-web3/news-image-20261119-entry/rank.svg)](https://make.fun/c/news-image-20261119)
[![Reward](https://make.fun/badge/news-image-20261119/rjrajput-web3/news-image-20261119-entry/reward.svg)](https://make.fun/c/news-image-20261119)

A program that draws one front-page image summing up the world's news of
Thursday, 19 November 2026 — 36 stories from six continents, all from
that one day. The bounty page for this competition is
https://make.fun/bounty/news-image-20261119

Run it with:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` (1024×1024 PNG, under 1 MiB). Fully
deterministic — two runs write byte-identical output. It needs PIL
(Pillow) and the DejaVu / Liberation system fonts; where those are
missing it copies the committed `entry.png` instead, which is the
exact same rendering. No network, no randomness, no timestamps.

## How it is drawn

`main.py` draws the whole front page itself with PIL: a serif masthead
naming the date, a six-number stats strip, a region-count bar, three
hero panels (the Shenzhen summit, GTA VI, Anthropic's Nasdaq debut),
ten illustrated story cards with flat drawn scenes (the World Court's
Rohingya judgment, tankers on fire after mine strikes east of Hormuz,
Ukraine's third strike on the Crimean Bridge in a week, unrest in
Bangladesh, Israel's ground operation in central Gaza, COP31's final
48 hours, the Houthi missile that damaged Riyadh's tallest tower, the
record $190.4m Van Gogh sale, Cyclone Akvan, the APEC Shenzhen
Declaration), a world map with the 13 illustrated stories pinned, and
29 numbered briefs. A DATE CHECK box names the stories first reported
before 19 November (the Jeffries nomination, the EU's €45bn Ukraine
loan plan, Voyager 1 crossing one light-day, Pew's 2035 projection)
and keeps them off the page as news. Nothing is fetched or copied in
at run time, and every story was checked against wire reporting of
19 November 2026.
