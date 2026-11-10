# The Boat Bothy: the after half of the old herring drifter Fulmar, turned keel-up on the cliff top, tarred every
# autumn and roped down like everything else here; a tinker mends pots in it in summer. Half a clinker hull for
# walls and roof, a boarded end with the door in it, stones banked along its sides. Tar black, a mustard strake.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_f as PF

META = {"name": "The Boat Bothy", "kind": "house", "lot": (4.0, 5.0), "wobble": 0.03}

LH, S0, WID, DEP, NS, STR = 4.45, 0.44, 3.1, 2.3, 8, 5


def build(b):
    b.footprint(-1.9, 0.0, 1.9, 4.9, DEP)
    L = LH / (1 - S0)
    Y0 = 0.14
    tar = V.TAR
    # ------------------------------------------------------------------ the hull, keel up, bow to the back
    with b.at(0.0, Y0, DEP):
        with b.at(ry=180):
            with b.at(0, -L * S0, 0):
                V.hull(b, L=L, width=WID, depth=DEP, n=NS, strakes=STR, s0=S0, s1=1.0, col=tar, inside=False, rail="mustard", cap0=False, lod=0, sheer=0.0)
    S = [S0 + (1 - S0) * i / NS for i in range(NS + 1)]
    secs = [V._hull_section(s, WID, DEP, STR, 0.0) for s in S]
    ys = [Y0 + L * (s - S0) for s in S]
    # its hidden foundation, and the stones banked against it
    loop = [(-secs[0][-1][0], ys[0])] + [(secs[i][-1][0], ys[i]) for i in range(NS + 1)] + [(-secs[i][-1][0], ys[i]) for i in range(NS - 1, 0, -1)]
    V.skin(b, [[(p[0], p[1], -3.0) for p in loop], [(p[0], p[1], 0.02) for p in loop]], "masonry", col=shade("dark", 0.8), lod=0, smooth=False)
    rng = b.rng
    for i in range(NS):
        for sgn in (-1, 1):
            for t in (0.25, 0.75):
                hb = lerp(secs[i][-1][0], secs[i + 1][-1][0], t)
                if hb < 0.25:
                    continue
                b.stone(rng.uniform(0.34, 0.5), rng.uniform(0.26, 0.36), rng.uniform(0.25, 0.48), mat="masonry", col=shade("grey", rng.uniform(0.85, 1.1)),
                        lod=1 if t < 0.5 else 2, x=sgn * (hb + 0.06), y=lerp(ys[i], ys[i + 1], t), z=0.0, ch=0.28, jitter=0.2)
    # ropes over her with stones on the ends
    for i in (2, 4, 6):
        for sgn in (-1, 1):
            pts = [(sgn * p[0] * 1.012, ys[i], (DEP - p[1]) * 1.012 + 0.02) for p in secs[i]]
            with b.detail(2):
                for a, c in zip(pts, pts[1:]):
                    V.beam(b, a, c, w=0.05, h=0.04, mat="cloth", col=V.ROPE, caps=False)
    # ------------------------------------------------------------------ the boarded end and its door
    arch = [(WID / 2 + sgn * p[0] * 0.985, (DEP - p[1]) * 0.985) for p in secs[0] for sgn in (-1, 1)]
    with b.at(-WID / 2, Y0 - 0.02, 0):
        wl = V.BWall(b, WID, DEP, "planks", tar, depth=0.14, outline=V.convex(arch))
    V.door(wl, WID / 2 - 0.2, w=0.8, h=1.65, col="mustard", lintel="timber", jambs=False)
    V.window(wl, WID / 2 + 0.95, 0.85, w=0.42, h=0.45, lintel=None, sill=False, frame="mustard", bars=(1, 0))
    PH.floats(wl, WID / 2 - 1.1, 1.5, n=4)
    PF.stovepipe(b, 0.75, Y0 + 1.3, DEP - 0.55, h=1.15)
    # ------------------------------------------------------------------ the tinker's bits
    PH.pots(b, -1.1, -0.5, 0, rz=8, n=2)
    V.oars(b, 0.98, 0.04, 0.0, h=1.95, lean=0.28, blade="mustard")
    V.bucket(b, 0.75, -0.45, 0)
    PH.gull(b, 0.0, Y0 + 0.5, DEP + 0.1, rz=200)
