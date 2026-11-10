# Chimney Cottage: the oldest house in the quarter, low enough to touch the eaves, kept warm by a hearth so big that its stack was built outside the gable; the widow who lives there sells kindling from the lean-to.
# A low one-and-a-half-storey cottage with its gable to the street under a steep slate roof with two little dormers, a massive outside chimney breast up the back gable, a boarded wood-shed leaning on the right.
# White lime-wash with the rubble showing through, slate, weathered boards; accent mustard.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "Chimney Cottage", "kind": "cottage", "lot": (5.5, 7.0)}

HX, HW, D, H = -0.45, 4.0, 5.9, 2.7           # x -2.45 .. 1.55


def build(b):
    b.footprint(-2.58, 0.0, 2.55, 6.6, 5.1)
    bd = b.body(HW, D, H, mat="plaster", col="white", x=HX)
    P.plinth(bd, h=0.7, out=0.06)
    for wl in bd.walls:
        P.exposed(wl, "both", n=8)
    P.door(bd.front, 1.25, w=0.9, h=1.95, z=0.17, col="mustard", steps=1, porch="gable", lamp=True)
    P.window(bd.front, 2.95, 1.0, w=0.9, h=1.1, shutters="mustard", box=True)
    P.window(bd.left, 1.6, 1.0, w=0.8, h=1.0)
    P.window(bd.left, 4.2, 1.0, w=0.8, h=1.0)
    P.window(bd.right, 1.0, 1.0, w=0.8, h=1.0, shutters="mustard")
    P.window(bd.back, 0.8, 1.0, w=0.7, h=1.0)
    P.window(bd.back, 3.2, 1.0, w=0.7, h=1.0)
    rise = bd.gable(ridge="y", pitch=50, mat="slate", sag=0.1, eave=0.1, verge=0.3)
    PH.cuttable(bd.front, bd.back)
    P.window(bd.front, HW / 2, H + 0.45, w=0.7, h=0.9, shutters="mustard")
    k = math.tan(rad(50))
    P.dormer(b, HX - HW / 2 + 0.75, 3.1, H + 0.75 * k - 0.15, w=1.0, h=0.8, depth=1.1, face=270, roof="slate", col="white", frame="ivory")
    P.dormer(b, HX + HW / 2 - 0.75, 1.9, H + 0.75 * k - 0.15, w=1.0, h=0.8, depth=1.1, face=90, roof="slate", col="white", frame="ivory")
    PM.stack(b, HX, D + 0.32, 0.0, 7.5, w=0.8, d=0.6, base=(1.7, 0.64, 3.0), mat="masonry", col="warm", pots=2)
    b.box(1.7, 0.64, 3.0, "masonry", col=shade("warm", 0.85), x=HX, y=D + 0.32, z=-3.0, top=False)
    lt = PH.leanto(b, HX + HW / 2, 4.2, 3.0, 0.85, 1.7, rz=90, pitch=28, mat="planks", col="#b89a72", roof="slate", eave=0.15, plinth=0.3)
    P.door(lt.left, 0.42, w=0.6, h=1.5, z=0.05, col="mustard", frame=None)
    PH.battens(lt.front)
    K.firewood(b, HX + HW / 2 + 0.03, 1.9, 0, w=1.2, h=0.9, rz=90)
    P.bench(b, HX + 1.1, -0.5, 0, w=1.1, rz=-4)
    PC.flowers(b, HX - 1.4, -0.3, 0, w=0.9, d=0.4)
    PC.cat(b, HX + 1.1, -0.5, 0.48, rz=10)
