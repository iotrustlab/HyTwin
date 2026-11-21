# Illustrative safety-impact animation

The [README animation](../assets/media/hytwin-impact.gif) explains a practical question behind HyTwin: **how can an altered actuator command become a physical safety hazard, and when must a defender intervene?** It compares the same pump-and-valve attack under three response strategies. It is a schematic synthetic simulation, not original experiment footage.

- [Looping GIF](../assets/media/hytwin-impact.gif): displayed inline in the GitHub README.
- [30-second MP4](../assets/media/hytwin-impact.mp4): silent, captioned video suitable for playback or sharing.
- [Still image](../assets/media/hytwin-impact-poster.png): the final comparison for readers who prefer a static view.
- [Generation script](../scripts/render_animation.py): renders the schematic directly from the local synthetic traces.
- [Media manifest](../assets/media/manifest.json): source and output hashes, file sizes, fonts, dependencies, and scope.

## What the viewer sees

The three panels use `transfer-unmitigated`, `transfer-mitigated`, and `transfer-late` from [`results/demo/traces.csv`](../results/demo/traces.csv). Source- and receiving-tank levels are interpolated within the trace's constant-rate scan segments. Pump and valve states come from the recorded commands at each scan timestamp.

| Event | Simulation time | Meaning |
| --- | ---: | --- |
| Attack begins | 2 s | The transfer pump and valve are forced open |
| Timely shutdown | 4 s | Two-second response; receiving-tank level holds at 6.8 |
| Upper boundary reached under continued transfer | 17 s | The closed safety bound `x2<=12` still holds at the boundary |
| Delayed shutdown | 18 s | Sixteen-second response; level holds at 12.4, already outside the safe range |
| End of run without intervention | 20 s | Receiving-tank level reaches 13.2 |

The main run uses one second of video per second of simulation. A four-second introduction and six-second conclusion hold the simulation clock still, making the complete video 30 seconds long. The GIF loops; the MP4 plays once. Text captions carry the explanation, so audio is unnecessary.

The upper-bound violation is presented as **an unsafe level and overflow risk**. Tank drawings use a schematic display scale and do not encode real dimensions, spill dynamics, or measured spill volume. The response delays are chosen experimental schedules in the synthetic reconstruction, not measured detection latencies. Timely shutdown freezes the process rather than guaranteeing continued production or availability.

## Regenerate the media

The core Python demonstration still requires no pip dependencies. Animation rendering is an optional, separate path, tested with Python 3.12 on Linux and DejaVu Sans fonts:

```bash
python3 -m venv .venv-media
.venv-media/bin/python -m pip install -r requirements-media.txt
.venv-media/bin/python scripts/render_animation.py
```

The pinned `imageio-ffmpeg` package supplies the encoder binary. Pillow draws the frames, and FFmpeg encodes H.264 MP4 and an optimized GIF. Install `fonts-dejavu-core` if `/usr/share/fonts/truetype/dejavu/` is unavailable on your Linux system. Frames are rendered in a temporary directory and removed after encoding. Final files are written to `assets/media/`; use `--output` to choose a different directory.

To also save selected keyframes for visual inspection:

```bash
.venv-media/bin/python scripts/render_animation.py --qa-dir /tmp/hytwin-animation-qa
```

Regenerate the source demo with `python3 -m hytwin demo --output results/demo` if its settings have changed, then rebuild the media and inspect the result. The manifest records source hashes so an animation can be checked against the traces it illustrates. Byte-identical encoding across different operating systems, fonts, or encoder builds is not assumed.

## Connection to the experimental project

The companion [OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main) was used to collect and validate HyTwin's experimental process traces. This animation makes the intervention-timing mechanism accessible without requiring the testbed. Its synthetic provenance remains separate from the paper's physical experiments and the repository's nine reconstructed model-level proofs. See the [experimental infrastructure guide](experimental-testbed.md) and [formal model guide](formal-models.md) for those evidence sources.
