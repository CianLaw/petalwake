# The bonded warehouse: tea, brandy and bolts of silk sit behind its green shutters until the duty is paid; the hoist never stops.
# A tall brick store, gable to the quay, crow-stepped front and back with stone copings; one column of loading doors climbs the face
# to a hooded hoist, small shuttered lights either side, iron ties at every floor. Red brick, pale stone bands, tiles; accent green.
from kit import *
import parts as P
import parts_h as H

META = {"name": "The Bonded Warehouse", "kind": "warehouse", "lot": (10.0, 11.0)}

W, D, HT = 8.8, 9.8, 8.1
RISE = (W / 2) * math.tan(rad(52))
STEP_RISE, NSTEP, TOPW, T = RISE + 0.55, 7, 1.2, 0.4
BRICK = "#f2e2d6"


def copings(wl, tops):
    """Stone slabs on every step of a crow-stepped gable, and a block on its top."""
    b = wl.b

    def deco():
        with b.detail(1):
            for (u0, z0), (u1, z1) in zip(tops, tops[1:]):
                if u1 - u0 > 0.05 and abs(z1 - z0) < 1e-6 and z0 > 0.01:
                    b.box(u1 - u0 + 0.12, T + 0.14, 0.1, "ashlar", col="stone", x=(u0 + u1) / 2, y=T / 2, z=z0, bottom=True)
            b.box(0.5, T + 0.05, 0.5, "ashlar", col="stone", x=wl.w / 2, y=T / 2, z=tops[len(tops) // 2][1] + 0.1, taper=0.7)

    wl.add(deco)


def ties(wl, us, zz):
    """Iron wall ties: small crosses at a floor line."""
    b = wl.b

    def deco():
        with b.detail(2):
            for u in us:
                for sgn in (-1, 1):
                    b.beam((u - 0.16, -0.02, zz - 0.16 * sgn), (u + 0.16, -0.02, zz + 0.16 * sgn), w=0.03, h=0.05, mat="metal", col="iron", up=(0, 1, 0), caps=False)

    wl.add(deco)


def build(b):
    bd = b.body(W, D, HT, mat="brick", col=BRICK)
    # the crow-stepped gables stand on the end walls as walls of their own (so each keeps its own few cuts)
    tops = [(u, z - HT) for u, z in H.steps_outline(W, HT, STEP_RISE, NSTEP, top_w=TOPW)]
    with b.at(-W / 2, 0.0, HT):
        gf = H.gwall(b, W, 0.0, tops=tops, mat="brick", col=BRICK, back="brick", thick=T, back_from=0.0)
    with b.at(W / 2, D, HT, rz=180):
        gb = H.gwall(b, W, 0.0, tops=tops, mat="brick", col=BRICK, back="brick", thick=T, back_from=0.0)
    copings(gf, tops)
    copings(gb, tops)
    # ------------------------------------------------------------------ the front: the column of loading doors
    C0 = W / 2
    cols_u = (1.15, 2.45, 6.35, 7.65)
    P.door(bd.front, C0, w=2.2, h=2.75, arch=0.7, col="green", frame="stone", double=True, z=0.06, lamp=True)
    H.loading_door(bd.front, C0, 3.25, w=1.5, h=1.8, col="green")
    H.loading_door(bd.front, C0, 5.85, w=1.5, h=1.8, col="green")
    for u in cols_u:
        P.window(bd.front, u, 1.55, w=0.7, h=0.75, bars=(2, 0), lintel="stone", frame="black")
        H.hatch(bd.front, u, 3.7, w=0.7, h=0.95, col="green")
        H.hatch(bd.front, u, 6.3, w=0.7, h=0.95, col="green")
    H.loading_door(gf, C0, 0.4, w=1.5, h=1.6, col="green")
    H.loading_door(gf, C0, 2.8, w=1.0, h=1.3, col="green", bar=False)
    for u in (2.75, 6.05):
        H.hatch(gf, u, 0.65, w=0.7, h=0.95, col="green")
    H.hoist(b, 0.0, 0.0, 12.75, out=1.1, load="barrel", drop=5.6, hood="tiles")
    ties(bd.front, (0.55, 3.2, 5.6, 8.25), 5.5)
    ties(gf, (0.9, 3.2, 5.6, 7.9), 0.1)
    # ------------------------------------------------------------------ the long sides: one more loading column, planted shutters
    P.door(bd.right, 5.0, w=1.5, h=2.4, col="green", frame="stone", double=True, z=0.06)
    H.loading_door(bd.right, 5.0, 3.25, w=1.5, h=1.8, col="green")
    H.loading_door(bd.right, 5.0, 5.85, w=1.5, h=1.8, col="green")
    H.hoist(b, W / 2, 5.0, 7.85, out=0.34, rz=90, load=None, drop=0.0, brace=False, back=0.4)
    P.door(bd.right, 1.2, w=0.9, h=2.0, col="green", frame="stone", z=0.1, lamp=True)
    for u in (3.0, 7.2, 8.7):
        P.window(bd.right, u, 1.55, w=0.7, h=0.75, bars=(2, 0), lintel="stone", frame="black")
    for u in (1.2, 4.9, 8.6):
        P.window(bd.left, u, 1.55, w=0.7, h=0.75, bars=(2, 0), lintel="stone", frame="black")
    for z in (3.7, 6.3):
        for u in (1.2, 3.0, 7.2, 8.7):
            H.shutter(bd.right, u, z, col="green")
        for u in (1.2, 3.05, 4.9, 6.75, 8.6):
            H.shutter(bd.left, u, z, col="green")
    ties(bd.right, (0.6, 2.1, 3.9, 6.2, 7.95, 9.3), 5.5)
    ties(bd.left, (0.6, 2.1, 3.95, 5.8, 7.7, 9.3), 5.5)
    # ------------------------------------------------------------------ the back gable
    P.door(bd.back, 2.2, w=1.0, h=2.0, col="green", frame="stone", z=0.1)
    P.window(bd.back, 6.6, 1.55, w=0.7, h=0.75, bars=(2, 0), lintel="stone", frame="black")
    for z in (3.7, 6.3):
        for u in (1.6, 4.4, 7.2):
            H.shutter(bd.back, u, z, col="green")
    H.loading_door(gb, C0, 0.4, w=1.2, h=1.5, col="green", bar=False)
    H.louvre(gb, C0, 2.9, w=0.8, h=1.0)
    P.plinth(bd, h=0.8, out=0.1, mat="masonry", col="grey")
    P.quoins(bd, z0=0.8, z1=HT, col="stone")
    P.band(bd, 3.02, h=0.16, out=0.06)
    P.band(bd, 5.62, h=0.16, out=0.06)
    P.band(bd, HT - 0.1, h=0.2, out=0.1)
    # ------------------------------------------------------------------ the roof between the gables
    b.gable_roof(W, D - 2 * T, pitch=52, mat="tiles", x=0, y=D / 2, z=HT, ridge="y", eave=0.3, verge=0.0, barge=False)
    for (x, y) in ((-2.3, 3.2), (2.3, 6.6)):      # two little roof vents
        zr = HT + (W / 2 - abs(x)) * math.tan(rad(52))
        with b.at(x, y, zr - 0.1):
            with b.detail(1):
                b.box(0.6, 0.6, 0.55, "planks", col="greyoak")
                b.box(0.8, 0.8, 0.08, "metal", col="lead", z=0.55, bottom=True)
    run = (W - TOPW) / 2
    H.gull(b, -(W / 2 - run * 4.5 / NSTEP), 0.2, HT + STEP_RISE * 5 / NSTEP + 0.12, rz=30)
    H.gull(b, 0.3, 0.2, HT + STEP_RISE + 0.62, rz=320)
    # ------------------------------------------------------------------ on the quay
    P.barrel(b, -3.6, -0.6, r=0.34, h=0.9)
    P.barrel(b, -2.85, -0.75, r=0.34, h=0.9)
    P.barrel(b, -3.25, -0.65, z=0.9, r=0.3, h=0.8, col="#b99870")
    P.crate(b, -1.9, -0.6, s=0.75, rz=6)
    P.crate(b, -1.85, -0.62, z=0.75, s=0.55, rz=-18)
    P.sack(b, 2.0, -0.55, r=0.34)
    P.sack(b, 2.55, -0.75, r=0.3, col="#cdbb92")
    P.sack(b, 2.2, -0.6, z=0.42, r=0.28)
    H.bollard(b, 4.3, -1.0)
    H.bollard(b, -4.5, -1.0)
