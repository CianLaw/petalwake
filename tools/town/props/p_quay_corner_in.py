# quay corner (inner): the paved square where two quay runs meet round a basin; the water touches only its (-x, -y) corner
from kit import *
import parts as P
import parts_p as PP

D = PP.QUAY_D
META = {"name": "Quay corner (inner)", "kind": "prop", "group": "harbour", "clear": 2.6, "wobble": 0.0, "size": D, "deck": 0.0, "bottom": -PP.DEEP,
        "notes": "3.6 m square of paving; a quay run along x (face toward -y) ends on its -x side, another (face toward -x) on its -y side"}


def build(b):
    h = D / 2
    with b.detail(0):
        PP.quay_deck(b, -h, h, back=0.7)
        b.quad((h, -h, PP.PAVE - 0.7), (h, h, PP.PAVE - 0.7), (h, h, PP.PAVE), (h, -h, PP.PAVE), "ashlar", col=shade("sand", 0.9))
        for (za, zb, m, k) in PP.QUAY_BANDS:          # the sliver between the two battered faces where they meet
            oa, ob = PP.quay_out(za), PP.quay_out(zb)
            b.face([(-h, -h - oa, za), (-h - oa, -h, za), (-h - ob, -h, zb), (-h, -h - ob, zb)], "ashlar", col=PP.quay_tone(zb - 0.01))
    with b.detail(1):
        b.stone(0.7, 0.7, 0.34, mat="ashlar", col="stone", x=-h + 0.3, y=-h + 0.3, z=PP.PAVE + 0.045 - 0.34, jitter=0.05, ch=0.16)
    with b.detail(2):
        P.barrel(b, 0.9, 0.9, PP.PAVE)
        P.crate(b, 0.2, 1.1, PP.PAVE, s=0.55, rz=14)
        PP.coil(b, 0.9, -0.2, PP.PAVE, r=0.28, turns=2)
