# a garden pergola hung with wisteria: timber posts on stone feet, a bench in its shade
from kit import *
import parts as P
import parts_p as PP
import parts_c as PC

W, D, H = 3.4, 2.2, 2.35
META = {"name": "Pergola with a vine", "kind": "prop", "group": "green", "clear": 2.5, "size": (W + 0.6, D + 0.6), "wobble": 0.02}
LILAC = ["#b08ae6", "#c9a8f0", "#9f7fd9"]


def build(b):
    PC.pergola(b, W, D, h=H, nx=3, col="darkoak", vines=True, bloom=LILAC)
    with b.detail(1):
        for x in (-W / 2, 0.0, W / 2):
            for y in (-D / 2, D / 2):
                b.stone(0.3, 0.3, 0.24, mat="ashlar", col="sand", x=x, y=y, z=-0.04, jitter=0.06, ch=0.2)
        PC.climber(b, (-W / 2, D / 2, H + 0.25), (W / 2, D / 2, H + 0.3), n=7, r=0.3, bloom=LILAC)
        PC.climber(b, (-W / 2 + 0.3, -D / 2, H + 0.25), (W / 2, -D / 2, H + 0.28), n=6, r=0.26, bloom=LILAC)
    with b.detail(2):
        rng = b.rng
        for _ in range(16):                                   # the hanging flowers
            x, y = rng.uniform(-W / 2, W / 2), rng.choice((-D / 2, 0.0, D / 2)) + rng.uniform(-0.2, 0.2)
            hh = rng.uniform(0.16, 0.3)
            b.blob(0.065, 0.065, hh, mat="paint", col=rng.choice(LILAC), x=x, y=y, z=H + 0.02 - hh, seg=5, rings=3, rough=0.12, wind=0.55)
        P.bench(b, 0.2, 0.55, 0, w=1.5, rz=0)
        PP.pot_plant(b, -W / 2 + 0.35, -D / 2 + 0.3, 0, r=0.17, h=0.26, flowers=["#f4f1e4", "#f5c842"])
        for (x, y) in ((W / 2 + 0.2, 0.4), (-W / 2 - 0.2, -0.5), (0.6, -D / 2 - 0.25)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.24)
