# The corner grocer: the house was cut away at the corner so that carts could turn, and the door has stood in the cut ever since, under the room above on its stone post.
# Corner house, streets to the front and the left: a chamfered rubble shop storey with the door in the chamfer, two square plastered storeys sailing over it on a column, a hipped roof with a dormer to each street.
# White lime-wash over warm rubble, terracotta tiles; accent green.
from kit import *
import parts as P
import parts_l as L
import parts_m as PM

META = {"name": "The Corner Grocer", "kind": "shop", "lot": (7.5, 8.0), "terrace": True, "fronts": ["front", "left"]}


def build(b):
    acc = "green"
    x0, x1, D = -3.25, 3.45, 7.7           # the side street runs down the left
    W, cx = x1 - x0, (x0 + x1) / 2
    H0, H = 3.2, 5.4
    top = H0 + H
    ch = 1.5
    # --- the shop storey, its corner cut off
    chw, fw, rw, bw, lw = L.outline_walls(b, [(x0, ch), (x0 + ch, 0.0), (x1, 0.0), (x1, D), (x0, D)], H0, mat="masonry", col="warm")
    P.plinth(L.Walls(b, [chw, fw, rw, bw, lw], front=fw), h=0.3)
    P.door(chw, chw.w / 2, w=1.05, h=2.15, z=0.17, col=acc, frame="stone", steps=1)
    P.window(chw, chw.w / 2, 2.45, w=1.05, h=0.36, bars=(2, 0), sill=False, lintel=None)
    P.lantern(chw, chw.w - 0.28, 2.25)
    L.shopfront(fw, 0.3, 3.5, h=2.7, z=0.3, col=acc, lights=4, riser=0.45)
    P.awning(fw, 1.9, 2.6, w=3.3, out=1.05, drop=0.5, cols=("stripe_green", "linen"))
    P.door(fw, 4.38, w=0.9, h=2.05, z=0.17, col=acc, frame="stone", steps=1)
    L.shopfront(lw, 3.45, lw.w - 0.3, h=2.7, z=0.3, col=acc, lights=3, riser=0.45)
    P.window(lw, 1.5, 1.15, w=0.9, h=1.3, shutters=acc)
    L.column(b, x0 + 0.34, 0.34, 0, r=0.2, h=H0)
    # --- two plastered storeys, square over the cut corner
    up = b.body(W, D, H, mat="plaster", col="white", x=cx, z=H0, floor="planks")
    P.band(up, -0.14, h=0.22, out=0.07)
    P.quoins(up, corners="f", col="warm")
    for u, bx in ((1.2, True), (3.35, False), (5.5, True)):
        P.window(up.front, u, 0.9, w=0.85, h=1.3, shutters=acc, box=bx)
        P.window(up.front, u, 3.6, w=0.8, h=1.1, shutters=acc)
    for u, bx in ((1.4, False), (3.85, True), (6.3, False)):
        P.window(up.left, u, 0.9, w=0.85, h=1.3, shutters=acc, box=bx)
        P.window(up.left, u, 3.6, w=0.8, h=1.1, shutters=acc)
    P.window(up.right, 4.6, 3.65, w=0.6, h=0.9); P.window(up.back, 2.2, 3.65, w=0.6, h=0.9); P.window(up.back, 5.0, 3.65, w=0.6, h=0.9)
    P.exposed(up.right, "corners", n=8); P.exposed(up.back, "corners", n=6)
    L.sign(up.front, 0.22, 0.85, emblem="apple", col="red", board="ivory", round_board=True)
    # --- the roof: hipped, deep eaves to the streets
    R, ridge = L.hip_roof(b, W, D, pitch=42, x=cx, y=D / 2, z=top, eave=(0.4, 0.12, 0.12, 0.38), col="#f3ddd0")
    tp = math.tan(rad(42))
    P.dormer(b, cx - 0.2, 1.3, top + 1.3 * tp - 0.1, w=1.0, h=0.9, depth=1.45, face=0, kind="hip", col="white", frame="ivory")
    P.dormer(b, x0 + 1.3, 4.3, top + 1.3 * tp - 0.1, w=1.0, h=0.9, depth=1.45, face=270, kind="hip", col="white", frame="ivory")
    P.chimney(b, x1 - 0.42, 2.7, top + 0.05, 3.5, w=0.66, d=0.9, mat="brick", pots=2)
    P.chimney(b, cx + 1.0, D - 0.42, top + 0.05, 3.3, w=0.9, d=0.66, mat="brick", pots=2)
    PM.weathercock(b, ridge[0][0], ridge[0][1], ridge[0][2] + 0.05, h=1.4, shape="cock")
    # --- the pavement: a trestle of fruit under the awning, crates, sacks
    L.stall(b, x0 + ch + 1.75, -0.72, w=2.2, d=0.6, goods=("#d9432f", "#e8a23a", "#7fb04a", "#f0d24a"))
    PM.produce(b, x0 + ch + 3.35, -0.5, 0.0, rz=10, cols=["#8a4fa0", "#6f9a3e"])
    P.sack(b, x0 + ch + 0.25, -0.35, 0, r=0.28); P.sack(b, x0 + ch + 0.6, -0.5, 0, r=0.24)
    P.barrel(b, x1 - 0.35, -0.4, r=0.27, h=0.7)
    L.flowerpot(b, x0 - 0.2, 4.6, 0, r=0.14, flower="#e8497a"); L.flowerpot(b, x0 - 0.2, 1.9, 0, r=0.14, flower="#f5c842")
    L.cat(b, x0 + ch + 2.9, -0.45, 0.0, rz=-15, col="#d98a3d")
