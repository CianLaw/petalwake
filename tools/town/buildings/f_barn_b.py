# The Hay House: an open-sided hay barn on eight oak posts; the sweetest-smelling place on the island, and the hens lay in it whatever anyone says.
# Massing: a big round-shouldered thatch hip floating on two rows of posts over a mountain of loose hay, the weather end boarded, a half-loft
#          at the other end with a ladder, a cart backed in underneath.
# Materials: oak posts on stone pads, golden thatch, tarred boards on the weather end, hay everywhere; accent mustard (the cart).
from kit import *
import parts as P
import parts_f as F

META = {"name": "The Hay House", "kind": "barn", "lot": (9.0, 7.0)}

XS = (-3.6, -1.2, 1.2, 3.6)
YF, YB = 1.0, 6.0
PH_ = 4.2                    # height of the plates
CY = (YF + YB) / 2


def build(b):
    # ---- the frame: posts on stone pads, plates, tie beams, braces
    for x in XS:
        for y in (YF, YB):
            b.box(0.5, 0.5, 0.4, "ashlar", col="grey", x=x, y=y, taper=0.8)
            b.box(0.5, 0.5, 3.0, "masonry", col="warm", x=x, y=y, z=-3.0, top=False)
            b.beam((x, y, 0.4), (x, y, PH_), w=0.24, mat="timber", col="darkoak", lod=0)
        b.beam((x, YF - 0.15, PH_ - 0.14), (x, YB + 0.15, PH_ - 0.14), w=0.2, h=0.24, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
        with b.detail(1):
            for (y, sy) in ((YF, 1), (YB, -1)):
                b.beam((x, y, PH_ - 1.1), (x, y + sy * 0.95, PH_ - 0.22), w=0.13, mat="timber", col="darkoak", caps=False)
            if abs(x) < 2.0:
                b.beam((x, CY, PH_), (x, CY, PH_ + 1.5), w=0.14, mat="timber", col="darkoak", caps=False)
    for y in (YF, YB):
        b.beam((XS[0] - 0.2, y, PH_ + 0.06), (XS[-1] + 0.2, y, PH_ + 0.06), w=0.22, h=0.2, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
        with b.detail(1):
            for xa, xb in zip(XS, XS[1:]):
                b.beam((xa, y, PH_ - 0.95), (xa + 0.8, y, PH_ - 0.08), w=0.12, mat="timber", col="darkoak", caps=False)
                b.beam((xb, y, PH_ - 0.95), (xb - 0.8, y, PH_ - 0.08), w=0.12, mat="timber", col="darkoak", caps=False)
    b.footprint(XS[0] - 0.3, YF - 0.3, XS[-1] + 0.3, YB + 0.3, PH_)

    # ---- the thatch
    F.soft_hip(b, XS[-1] - XS[0] + 0.5, YB - YF + 0.5, pitch=47, x=0.0, y=CY, z=PH_ + 0.1, eave=0.42, corner=0.4, shoulder=0.8, under=True)

    # ---- the weather end boarded, a half-loft at the other end
    with b.at(XS[0] - 0.02, YB, 0.25, rz=270):
        b.wall(YB - YF, 3.3, mat="planks", col="#8a7a6a", back="planks", backcol="#7a6c5e", thick=0.06)
    lx0, lx1, lz = XS[2] + 0.05, XS[3] + 0.05, 2.35
    F.deck(b, lx1 - lx0, YB - YF, x=(lx0 + lx1) / 2, y=CY, z=lz, thick=0.08, joists=0.8)
    F.hay(b, (lx0 + lx1) / 2 + 0.2, CY + 0.6, lz, rx=1.0, ry=1.7, h=1.25, lod=1)
    F.ladder_to(b, (lx0 - 0.75, YF + 0.9, 0.0), (lx0 - 0.05, YF + 0.9, lz + 0.7), w=0.45)

    # ---- hay: the mountain in the middle bays, drifts and wisps
    F.hay(b, -1.3, CY + 0.2, 0.0, rx=2.25, ry=2.1, h=3.0, lod=0, seg=9)
    F.hay(b, -2.6, CY - 0.9, 0.0, rx=1.2, ry=1.3, h=1.7, lod=1)
    F.hay(b, 0.5, CY - 1.3, 0.0, rx=1.0, ry=1.0, h=1.1, lod=1)
    F.hay(b, -0.4, YF - 0.25, 0.0, rx=0.7, ry=0.45, h=0.45, lod=2)
    F.hay(b, 0.9, YB + 0.2, 0.0, rx=0.8, ry=0.5, h=0.5, lod=2)
    F.cat(b, -1.1, CY - 0.5, 2.9, rz=200, pose="curl")
    with b.at(-0.2, CY - 1.55, 1.0, rx=-28):
        F.tool(b, 0, 0, 0, kind="fork", h=1.5, lean=0.0)

    # ---- the cart backed in under the loft, tools against a post
    F.cart(b, (lx0 + lx1) / 2, CY + 0.9, 0.0, rz=0, L=2.2, W=1.15, load="hay", paint="mustard")
    F.tool(b, XS[3] - 0.2, YF + 0.25, 0.0, kind="rake", rz=-90, lean=0.08)
    P.barrel(b, XS[3] - 0.45, YB - 0.4, 0.0, r=0.28, h=0.8)
    F.bucket(b, 0.6, YF + 0.2, 0.0)
    F.meadow(b, -4.1, 0.35, 4.1, 0.5, n=6, spread=(0.22, 0.3))
    F.meadow(b, -4.1, 6.5, 4.1, 6.62, n=5, spread=(0.2, 0.26))
