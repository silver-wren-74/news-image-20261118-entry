# One Day in the World — 18 November 2026

[![Submissions](https://make.fun/api/badges/news-image-20261118/submissions.svg)](https://make.fun/bounty/news-image-20261118) [![Pool](https://make.fun/api/badges/news-image-20261118/pool.svg)](https://make.fun/bounty/news-image-20261118) [![Deadline](https://make.fun/api/badges/news-image-20261118/deadline.svg)](https://make.fun/bounty/news-image-20261118)

My entry for the make.fun bounty [news-image-20261118](https://make.fun/bounty/news-image-20261118): one image that sums up the world news of **Wednesday 18 November 2026**.

## The image

A night-desk front page. Lead story: the US sinks five Iranian tankers and Iran strikes back across the Gulf. Around it: Ukraine hits the Kerch Bridge for a second night as peace envoys talk, Trump in Manila for Quad talks while Xi meets Canada's Carney ahead of APEC Shenzhen, North Korea fires a ballistic missile after allied drills, and COP31 in Antalya enters its decisive phase — plus a footer line for the Gaza winter warning, the Romania quake, the Prague media marches and the new James Bond.

## How it works

`main.py` is a small pixel renderer written from scratch on the Python 3 standard library only: a hand-rolled PNG encoder, a frame buffer, a 5x7 bitmask pixel font, and simple shape routines (boxes, discs, triangles, lines) that draw the masthead, five story cards with icons (tanker, bridge, flags, missile, thermometer) and the footer. No network, no randomness — every run produces the identical image.

## Run it

```bash
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # or a local folder
```

## License

MIT — see `LICENSE`.
