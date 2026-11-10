# the flower seller's barrow: two big wheels, stepped shelves of pots and buckets in bloom, a striped parasol
from kit import *
import parts as P
import parts_p as PP
import parts_m as PM

META = {"name": "Flower cart", "kind": "prop", "group": "square", "clear": 1.7, "wobble": 0.015}

BODY = "!#8fcfae"


def posy(b, x, y, z, r=0.11, h=0.17, cols=None, n=4, tall=0.0, pot="#c9764a"):
    with b.at(x, y, z):
        b.revolve([(r * 0.7, 0.0), (r, h), (r * 0.8, h)], "paint", col=pot, seg=6)
        b.blob(r * 1.35, r * 1.35, r * 1.2 + tall, mat="ivy", col=shade(PP.LEAF, b.r(0.9, 1.1)), z=h + r * 0.5 + tall * 0.5, seg=5, rings=3, rough=0.3, wind=0.3, bottom=False)
        PP.blooms(b, 0, 0, h + r * 1.3 + tall, r * 1.2, n=n, cols=cols, size=0.05, lift=0.06)


def build(b):
    zb = 0.74
    with b.detail(1):
        PP.board(b, (-0.78, 0, zb - 0.025), (0.78, 0, zb - 0.025), w=0.84, t=0.05, col=BODY)
        for sy in (-1, 1):
            PP.board(b, (-0.78, sy * 0.42, zb + 0.08), (0.78, sy * 0.42, zb + 0.08), w=0.2, t=0.03, col=BODY, up=(0, 1, 0))
        for sx in (-1, 1):
            PP.board(b, (sx * 0.78, -0.42, zb + 0.08), (sx * 0.78, 0.42, zb + 0.08), w=0.2, t=0.03, col=BODY, up=(1, 0, 0))
        PP.board(b, (-0.72, 0.0, zb + 0.2), (0.72, 0.0, zb + 0.2), w=0.28, t=0.03, col="ivory")              # middle shelf
        PP.board(b, (-0.72, 0.27, zb + 0.4), (0.72, 0.27, zb + 0.4), w=0.26, t=0.03, col="ivory")            # top shelf
        PP.board(b, (-0.72, 0.4, zb + 0.3), (0.72, 0.4, zb + 0.3), w=0.56, t=0.025, col=BODY, up=(0, 1, 0))  # back board
        b.beam((0, -0.56, 0.44), (0, 0.56, 0.44), w=0.07, mat="timber")
        for sy in (-1, 1):
            with b.at(0, sy * 0.54, 0.44):
                PP.wheel(b, r=0.44, w=0.06, spokes=8, col="!#f2ead8")
            b.beam((0, sy * 0.36, 0.46), (0, sy * 0.36, zb - 0.05), w=0.06, mat="timber")
            b.beam((0.7, sy * 0.3, zb - 0.06), (1.5, sy * 0.33, zb + 0.12), w=0.05, mat="planks", col="darkoak")     # handles
            b.beam((0.72, sy * 0.3, zb - 0.05), (0.8, sy * 0.33, 0.0), w=0.05, mat="planks", col="darkoak")          # legs
        PM.parasol(b, -0.55, 0.3, zb, r=1.05, h=1.75, cols=("#f2a0bd", "linen"), n=8)
    with b.detail(2):
        sets = [["#e8497a", "#f2a0bd"], ["#f5c842", "#f4f1e4"], ["#b08ae6", "#e3d8ee"], ["#e85d3a", "#f5c842"], ["#ffffff", "#f2a0bd"], ["#f07fa8", "#b08ae6"]]
        for i in range(4):
            posy(b, -0.54 + 0.36 * i, -0.26, zb, cols=sets[i % 6])
        for i in range(4):
            posy(b, -0.5 + 0.34 * i, 0.0, zb + 0.215, cols=sets[(i + 2) % 6], r=0.1)
        for i in range(3):
            posy(b, -0.1 + 0.34 * i, 0.27, zb + 0.415, cols=sets[(i + 4) % 6], r=0.1, tall=0.12, pot="#7f8a90")
        posy(b, -0.95, -0.75, 0, r=0.16, h=0.26, cols=sets[0], n=6, tall=0.15, pot="#c9a57a")
        posy(b, -0.5, -0.9, 0, r=0.14, h=0.22, cols=sets[1], n=5, pot="#c9a57a")
        PP.bucket(b, 1.0, -0.8, 0, r=0.13, h=0.24, water=True)
