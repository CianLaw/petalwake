# quay stairs, 8 m: a quay segment with a flight of steep harbour steps let into its face, going down under the water
from kit import *
import parts as P
import parts_p as PP

L = 8.0
D = PP.QUAY_D
META = {"name": "Quay stairs 8 m", "kind": "prop", "group": "harbour", "clear": 4.4, "length": L, "axis": "x", "wobble": 0.0,
        "deck": 0.0, "depth": D, "face_y": -D / 2, "bottom": -PP.DEEP,
        "notes": "replaces one quay segment; the steps go down toward -x from the deck to 5.2 m below it (26 risers of 0.2 m)"}


def build(b):
    yf, W = -D / 2, 1.3
    yr = yf + W
    n, rise, going, x_top = 26, 0.2, 0.26, 3.3
    x_low = x_top - n * going
    Z = PP.PAVE
    with b.detail(0):
        PP.quay_face(b, -L / 2, x_low, cell=1.0)
        PP.quay_face(b, x_top, L / 2, cell=1.0)
        for k in range(n):
            xb = x_top - k * going
            xa = xb - going
            zk = Z - (k + 1) * rise
            c = PP.quay_tone(zk + 0.05, col="stone")
            o0, o1 = PP.quay_out(zk), PP.quay_out(zk + rise)
            PP.quay_face(b, xa, xb, top=zk, cell=1.0)
            b.quad((xa, yf - o0, zk), (xb, yf - o0, zk), (xb, yr, zk), (xa, yr, zk), "ashlar", col=c)
            b.quad((xb, yr, zk), (xb, yf - o0, zk), (xb, yf - o1, zk + rise), (xb, yr, zk + rise), "ashlar", col=shade(c, 0.86))
            b.quad((xa, yr, zk), (xb, yr, zk), (xb, yr, Z), (xa, yr, Z), "ashlar", col=PP.quay_tone((zk + Z) / 2))
        zb = Z - n * rise
        b.quad((x_low, yf - PP.quay_out(zb), zb), (x_low, yr, zb), (x_low, yr, Z), (x_low, yf, Z), "ashlar", col=PP.quay_tone(-2.0))
        PP.quay_deck(b, -L / 2, L / 2, y0=yr)
        PP.quay_deck(b, -L / 2, x_low, y0=yf, y1=yr, back=0, cell=1.0)
        PP.quay_deck(b, x_top, L / 2, y0=yf, y1=yr, back=0, cell=1.0)
    with b.detail(1):
        PP.quay_coping(b, -L / 2, x_low)
        PP.quay_coping(b, x_top, L / 2)
        PP.quay_coping(b, x_low, x_top, yf=yr + 0.05, depth=0.42, thick=0.3, wmin=0.7, wmax=1.1)
        P.railing(b, [(x_low + 0.12, yr + 0.21, Z + 0.04), (x_top - 1.0, yr + 0.21, Z + 0.04)], h=0.95, style="iron", posts_at=1.5, gap=0.42)
        PP.bollard_stone(b, x_top + 0.36, yf + 0.7, Z, h=0.66, r=0.17)
    with b.detail(2):
        PP.quay_stones(b, x_top, L / 2, n=2, size=(0.3, 0.5))
        with b.at(x_low, yf + 0.55, -1.3, rz=-90):
            PP.mooring_ring(b, r=0.14, rr=0.02)
        with b.at(-1.2, yr, -1.2):
            PP.mooring_ring(b, r=0.14, rr=0.02)
        PP.rope_turns(b, x_top + 0.36, yf + 0.7, Z + 0.26, r=0.165, turns=2)
        for x in (-2.6, 0.9, 3.2):
            PP.tuft(b, x, D / 2 - b.r(0.15, 0.5), Z, r=0.09, h=0.14, n=4)
