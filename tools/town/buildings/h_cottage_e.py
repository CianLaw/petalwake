# Driftwood Cottage: the widow Nance keeps a whale's jawbones for a garden arch and hangs the whole street's washing in exchange for mackerel.
# A long low cream cottage under a silvered shingle roof that slides down at the back almost to the ground, a dormer, a broad
# stone stack on the gable; nets and washing in the yard, the jawbone arch by the bench. Cream plaster, shingle, stone; accent pink.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Driftwood Cottage", "kind": "cottage", "lot": (6.0, 7.0), "lean": (-0.002, -0.002)}


def build(b):
    bd = b.body(5.4, 3.8, 2.5, mat="plaster", col="cream")                   # x +-2.7, y 0 .. 3.8
    H.cuttable(bd.left, bd.right)
    P.door(bd.front, 3.3, w=0.9, h=1.9, col="pink", frame="timber", z=0.17, steps=1, lamp=True)
    P.window(bd.front, 1.25, 1.0, w=1.05, h=1.05, bars=(2, 1), shutters="pink", box=True, lintel="timber")
    P.window(bd.front, 4.7, 1.05, w=0.6, h=0.85, shutters="pink", lintel="timber")
    P.window(bd.left, 1.9, 1.0, w=0.8, h=1.0, shutters="pink", lintel="timber")
    P.window(bd.left, 1.9, 2.95, w=0.55, h=0.65, lintel=None)
    P.window(bd.right, 0.9, 1.05, w=0.6, h=0.85, lintel="timber")
    P.plinth(bd, h=0.45)
    P.exposed(bd.front, "both", n=12)
    P.exposed(bd.left, "corners", n=8)
    bd.gable(ridge="x", pitch=45, mat="shingle", eave=0.3, verge=0.3, sag=0.14)
    cs = H.leanto(b, 0.0, 3.8, 5.4, 1.6, 0.9, rz=180, pitch=45, mat="plaster", col="cream", roof="shingle", eave=0.25, verge=0.3, plinth=0.4)
    P.window(cs.front, 1.3, 0.3, w=0.6, h=0.42, lintel=None, sill=False)
    P.window(cs.front, 4.0, 0.3, w=0.6, h=0.42, lintel=None, sill=False)
    P.door(cs.right, 0.45, w=0.7, h=1.5, col="pink", frame=None, z=0.05)
    P.dormer(b, -1.2, 0.8, 3.1, w=1.0, h=0.72, depth=1.05, face=0, roof="shingle", col="cream", pitch=34)
    H.stack(b, 2.6, 1.9, 0.0, 6.4, w=0.7, d=1.5, top=0.5, mat="masonry", col="warm", bands=1, pots=2)
    # ------------------------------------------------------------------ the jawbone arch, the bench, the front garden
    with b.at(-1.75, -0.9, 0):
        with b.detail(1):
            for sx in (-1, 1):
                pts = [(sx * 0.7, 0, -0.1), (sx * 0.66, 0, 1.0), (sx * 0.5, 0, 1.9), (sx * 0.22, 0, 2.5), (0.0, 0, 2.75)]
                for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
                    b.tube(p0, p1, r=0.11 - 0.02 * i, r1=0.09 - 0.02 * i, mat="paint", col="!#ece4d0", n=6)
    P.bench(b, -1.6, -0.3, w=1.4)
    PC.cat(b, -1.25, -0.3, 0.48, rz=30, col="!#8a8f96")
    PC.flowers(b, 1.75, -0.4, w=1.2, d=0.5, n=7)
    PC.flowers(b, -2.55, -0.45, w=0.5, d=0.5, n=3)
    P.barrel(b, 0.0, -0.35, r=0.27, h=0.75)
    # ------------------------------------------------------------------ the yard: nets and the street's washing
    with b.detail(1):
        for (x, y) in ((-2.6, 5.7), (2.6, 5.9), (-0.2, 6.55)):
            b.beam((x, y, 0), (x, y, 2.3), w=0.08, mat="timber", col="greyoak")
    P.laundry(b, (-2.6, 5.7, 2.25), (2.6, 5.9, 2.25), n=7, sag=0.3)
    H.net_drape(b, (-0.2, 6.55, 2.1), (2.6, 5.9, 2.2), drop=1.5, sag=0.12, col=H.NET_BROWN)
    H.pots(b, -2.1, 6.1, rz=20, n=3)
    PC.flowers(b, -0.9, 5.9, w=1.4, d=0.5, n=6, cols=["#f5c842", "#f4f1e4", "#e85d3a"])
    H.gull(b, 2.6, 1.9, 7.2, rz=260)
