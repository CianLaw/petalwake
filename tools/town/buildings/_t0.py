# first smoke test of the kit: a round tower, a house, their roofs
META = {"name": "Kit test", "kind": "test"}
def build(b):
    t = b.round(3.2, 12.0, r1=2.8, mat="masonry", col="warm", x=-4.5, y=4)
    t.opening(0, 0.0, 1.1, 2.1, arch=0.5, pane="planks", pane_col="green")
    t.opening(40, 5.0, 0.7, 1.3, arch=0.35)
    t.opening(200, 7.5, 0.7, 1.3)
    b.cone_roof(2.8, 5.2, mat="slate", x=-4.5, y=4, z=12.0, seg=20)
    bd = b.body(7.0, 6.0, 5.2, mat="plaster", col="cream", x=2.5)
    bd.front.opening(1.4, 0.0, 1.0, 2.05, pane="planks", pane_col="green")
    bd.front.opening(4.6, 1.1, 0.9, 1.3)
    bd.front.opening(4.6, 3.4, 0.9, 1.3, arch=0.3)
    bd.right.opening(3.0, 3.2, 0.8, 1.2)
    bd.gable(ridge="x", pitch=46, mat="tiles", sag=0.12)
    b.stone(0.6, 0.4, 0.35, x=7, y=-1)
    b.beam((6.2, -0.4, 0), (6.2, -0.4, 2.4), w=0.16)
    b.blob(0.8, x=-1, y=-1.2, z=0.6, col="#9fd07a")
