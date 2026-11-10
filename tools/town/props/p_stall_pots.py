# market stall: the potter. A hooped green awning, shelves of jugs and bowls, big jars standing round it
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Pottery stall", "kind": "prop", "group": "square", "clear": 2.2}

GLAZE = ["#c9764a", "#efe2c4", "#4f7fae", "#6f9d6a", "#d9a431", "#b5564a", "#c9764a", "#e9d9b8"]


def build(b):
    s = PP.stall(b, w=2.6, d=1.7, roof="barrel", cols=("stripe_green", "linen"), apron="boards", apron_col="darkoak", rise=0.6)
    top, y0, y1, hw, py = s["top"], s["y0"], s["y1"], s["hw"], s["py"]
    with b.detail(1):
        b.box(2 * hw - 0.1, 0.34, 0.22, "planks", col="greyoak", y=y1 - 0.2, z=top)             # a step shelf at the back of the counter
        PP.board(b, (-hw + 0.0, py - 0.14, 1.42), (hw - 0.0, py - 0.14, 1.42), w=0.26, t=0.04, col="greyoak")     # a high shelf across the back posts
    with b.detail(2):
        kinds = ["jug", "bowl", "vase", "urn", "jug", "bowl", "plate", "vase"]
        for i in range(7):
            x = -hw + 0.2 + (2 * hw - 0.4) * i / 6
            PP.jar(b, x + b.r(-0.03, 0.03), y0 + 0.2 + b.r(-0.04, 0.04), top, s=b.r(0.8, 1.05), kind=kinds[i % len(kinds)], col=GLAZE[i % len(GLAZE)], seg=5)
        for i in range(6):
            x = -hw + 0.26 + (2 * hw - 0.52) * i / 5
            PP.jar(b, x, y1 - 0.2, top + 0.22, s=b.r(0.85, 1.1), kind=kinds[(i + 3) % len(kinds)], col=GLAZE[(i + 2) % len(GLAZE)], seg=5)
        for i in range(5):
            x = -hw + 0.3 + (2 * hw - 0.6) * i / 4
            PP.jar(b, x, py - 0.14, 1.44, s=b.r(0.8, 1.0), kind=("jug", "vase", "bowl")[i % 3], col=GLAZE[(i + 5) % len(GLAZE)], seg=5)
        for j in range(4):                                         # a stack of plates
            PP.jar(b, 0.62, y0 + 0.55, top + 0.022 * j, s=0.9, kind="plate", col=GLAZE[1], seg=6)
        # the big ware stands on the ground
        PP.jar(b, -hw - 0.2, -1.05, 0, s=1.9, kind="amphora", col="#c9764a", seg=8)
        PP.jar(b, -hw + 0.35, -1.25, 0, s=1.5, kind="urn", col="#4f7fae", seg=8)
        PP.jar(b, hw + 0.1, -1.0, 0, s=1.8, kind="urn", col="#c9764a", seg=8)
        PP.jar(b, hw - 0.42, -1.3, 0, s=1.3, kind="jug", col="#efe2c4", seg=8)
        PP.jar(b, hw + 0.25, 0.3, 0, s=2.1, kind="amphora", col="#b5564a", seg=8)
        PP.pot_plant(b, -hw - 0.1, 0.5, 0, r=0.2, h=0.3, flowers=["#e8497a", "#f4f1e4"])
        P.crate(b, 0.2, 0.5, 0, s=0.5, rz=8)
        b.blob(0.2, 0.2, 0.1, mat="thatch", col=PP.STRAW, x=0.2, y=0.5, z=0.5, seg=6, rings=2, rough=0.3, bottom=False)       # packing straw
