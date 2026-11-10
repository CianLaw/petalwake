"""Petalwake town kit: the lead's odds and ends (pieces written after the district libraries)."""
import math

from kit import mix, shade
import parts_p as PP

MOLE_TW = 8.0           # as props/p_mole.py: the width of a mole's top
MOLE_SLOPE = 0.72       # ...and how far its rubble runs out per metre down


def _arc(r, z, a0=0.0, a1=180.0, n=10, dy=0.0):
    """Points round an arc about the z axis: angle 0 is toward -y, 90 toward +x, 180 toward +y."""
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        out.append((r * math.sin(a), dy - r * math.cos(a), z))
    return out


def mole_head(b, wall=None, seg=10):
    """The rounded end of a mole: joins a run of p_mole on its -x side and bulges toward +x; its top is level
    with theirs and its rubble goes as deep.
    wall = None (a bare head with a kerb all round: stand a light on it), 'right' (the run's sea wall, on -y,
    carried round the tip) or 'left' (the same for a wall on +y)."""
    hw, Z = MOLE_TW / 2, PP.PAVE
    rng = b.rng
    ro, ri, h = hw - 0.44, hw - 1.06, 1.1
    wa0, wa1 = (0.0, 126.0) if wall == "right" else (54.0, 180.0)
    with b.detail(0):
        for (za, zb, m, k) in PP.QUAY_BANDS:                      # the rubble cone, weedier toward the water
            ra, rb = hw + (Z - za) * MOLE_SLOPE, hw + (Z - zb) * MOLE_SLOPE
            b.revolve([(ra, za), (rb, zb)], "masonry", col=shade(mix("grey", "#9aa888", m), k), seg=seg, a0=0.0, a1=180.0, smooth=False)
        b.face(_arc(hw, Z, n=seg), "masonry", col="grey")         # the top, and the flagged walk ending in a round
        b.face(_arc(2.5, Z + 0.03, n=seg, dy=-0.2 if wall == "left" else 0.2), "flagstone", col="sand")
        if wall:
            b.revolve([(ro, Z), (ro, Z + h), (ri, Z + h), (ri, Z)], "masonry", col="grey", seg=7, a0=wa0, a1=wa1, smooth=False)
            ae = math.radians(wa1 if wall == "right" else wa0)     # its free end
            u = (math.sin(ae), -math.cos(ae))
            q = [(ri * u[0], ri * u[1], Z), (ro * u[0], ro * u[1], Z), (ro * u[0], ro * u[1], Z + h), (ri * u[0], ri * u[1], Z + h)]
            b.face(q if wall == "left" else [q[0], q[3], q[2], q[1]], "masonry", col=shade("grey", 0.85))
    with b.detail(1):
        if wall:                                                   # capping stones
            b.revolve([(ro + 0.06, Z + h - 0.01), (ro + 0.06, Z + h + 0.13), (ri - 0.06, Z + h + 0.13), (ri - 0.06, Z + h - 0.01)],
                      "ashlar", col="stone", seg=7, a0=wa0, a1=wa1, smooth=False)
            ab = math.radians(150.0 if wall == "right" else 30.0)
            PP.bollard_stone(b, (hw - 1.15) * math.sin(ab), -(hw - 1.15) * math.cos(ab), Z, h=0.7, r=0.19)
        k0, k1 = {None: (3.0, 177.0), "right": (129.0, 177.0), "left": (3.0, 51.0)}[wall]
        r = hw - 0.32                                              # a kerb where there is no wall
        a = k0
        while a < k1 - 5.0:
            w = min(rng.uniform(0.85, 1.25), math.radians(k1 - a) * r)
            da = math.degrees(w / r)
            am = math.radians(a + da / 2)
            with b.at(r * math.sin(am), -r * math.cos(am), 0.0, rz=math.degrees(am)):
                b.stone(w - 0.03, 0.6, 0.3, mat="ashlar", col="stone", z=Z - 0.22, jitter=0.06, ch=0.18)
            a += da
    for lod, n, s0, s1 in ((1, 8, 0.2, 2.4), (2, 12, 0.6, 5.2)):   # armour stones tumbled down the slope
        with b.detail(lod):
            for i in range(n):
                w = rng.uniform(0.8, 1.6)
                d, hh = w * rng.uniform(0.6, 0.9), w * rng.uniform(0.45, 0.7)
                a = math.radians(180.0 * (i + rng.uniform(0.15, 0.85)) / n)
                s = rng.uniform(s0, s1)
                rr = hw + s * MOLE_SLOPE + 0.1
                with b.at(rr * math.sin(a), -rr * math.cos(a), Z - s - hh * 0.45, rz=rng.uniform(0, 90), rx=rng.uniform(-12, 20)):
                    b.stone(w, d, hh, mat="masonry", col=shade("grey", 0.95 if s < 2.6 else 0.8), jitter=0.22, ch=0.3)
    with b.detail(2):
        for ad in (20.0, 75.0, 110.0, 160.0):
            a = math.radians(ad)
            PP.tuft(b, (hw - 0.9) * math.sin(a), -(hw - 0.9) * math.cos(a), Z, r=0.1, h=0.17, n=4)
        if wall:
            ab = math.radians(150.0 if wall == "right" else 30.0)
            PP.rope_turns(b, (hw - 1.15) * math.sin(ab), -(hw - 1.15) * math.cos(ab), Z + 0.28, r=0.185, turns=2)
