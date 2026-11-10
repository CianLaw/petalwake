# Stepgable: built by a master dyer who had seen the merchants' houses up the coast and wanted a crow-stepped gable of his own; his widow lets the rooms now, and the oriel is where the lodger writes.
# A tall narrow terrace house, gable to the street: grey rubble three storeys high under a steep slate roof between crow-stepped gables, a boarded oriel on brackets at the first floor; blank side walls for the neighbours.
# Grey rubble with pale bands, slate, red brick stack; accent teal.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "Stepgable", "kind": "cottage", "lot": (5.5, 7.0), "terrace": True}

W, D, H = 5.2, 5.8, 5.4


def build(b):
    b.footprint(-2.6, 0.0, 2.6, 6.8, 8.8)
    bd = b.body(W, D, H, mat="masonry", col="grey")
    P.plinth(bd, h=0.5, out=0.04, col="dark")
    P.band(bd, 2.75, h=0.16, out=0.04, col="sand")
    P.stones(bd.front, n=6, z0=0.55, z1=2.6)
    P.stones(bd.front, n=4, z0=4.6, z1=5.3)
    P.stones(bd.back, n=12, z0=0.55, z1=5.2)
    P.door(bd.front, 1.15, w=0.95, h=2.1, z=0.34, arch=0.45, col="teal", steps=2, lamp=True)
    P.window(bd.front, 3.75, 1.2, w=1.0, h=1.3, shutters="teal")
    PM.bay(bd.front, W / 2, 3.05, w=2.0, h=1.3, out=0.5, cant=0.28, col="ivory", apron_col="teal", roof="slate")
    P.door(bd.back, 1.2, w=0.9, h=1.95, z=0.1, col="teal", frame="timber")
    P.window(bd.back, 3.7, 1.2, w=1.0, h=1.3)
    P.window(bd.back, 1.3, 3.5, shutters="teal")
    P.window(bd.back, 3.9, 3.5, shutters="teal")
    rise = bd.gable(ridge="y", pitch=52, mat="slate", eave=0.04, verge=0.02, barge=False)
    PH.cuttable(bd.front, bd.back)
    P.window(bd.front, W / 2, H + 0.45, w=0.75, h=1.1, arch=0.3)
    P.window(bd.back, W / 2, H + 0.45, w=0.75, h=1.1, arch=0.3)
    with b.at(-W / 2, -0.03, H):
        PC.crow_steps(b, W, rise, t=0.34, n=5, mat="masonry", col="grey")
    with b.at(W / 2, D + 0.03, H, rz=180):
        PC.crow_steps(b, W, rise, t=0.34, n=5, mat="masonry", col="grey")
    PC.stack(b, 2.1, 3.3, H + 0.2, 3.9, w=0.7, d=0.55, mat="brick", flues=2, style="diagonal")
    P.planter(b, 2.2, -0.35, 0, w=0.8)
    PC.doves(b, [(-1.55, 0.14, H + rise * 0.42), (0.0, 0.14, H + rise + 0.5), (1.2, D - 0.14, H + rise * 0.62)])
    fl = K.yard(b, -2.56, D, 2.56, 6.8, mat="flagstone", h=0.08)
    with b.detail(1):
        b.beam((2.3, 6.6, fl), (2.3, 6.6, 2.8), w=0.1)
    P.laundry(b, (-2.2, D + 0.05, 2.7), (2.3, 6.6, 2.7), n=5)
    P.barrel(b, -2.1, D + 0.5, fl)
