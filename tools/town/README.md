# The town kit

Every building in Petalwake's towns is modelled in Blender by a short Python script written with
this kit. `kit.py` is the vocabulary of shapes (walls with real openings, round and many-sided
towers, stepped-course roofs, beams, stones, lathe-turned forms); `parts.py` is the dressing
(windows, doors, galleries, railings, chimneys, dormers, signs, laundry, flags...). Read both files:
the docstrings are the reference, and `parts.py` doubles as a set of examples for making new parts.
`buildings/_t1.py` and `buildings/_t2.py` are complete worked examples that use every part.

## Making a building

One file per building: `tools/town/buildings/<id>.py` (props: `tools/town/props/<id>.py`).

```python
from kit import *
import parts as P

META = {"name": "The Gull's Rest", "kind": "inn", "lot": (9.0, 10.0)}   # lot = frontage x depth it needs, metres

def build(b):
    ...
```

Build, look, fix, repeat:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b -P tools/town/make.py -- <id> [<id> ...] --render
```

That prints one `BUILT <id>: ... tris ...` line per building (or a traceback), and writes two
views side by side to `art/town/preview/<id>.jpg` (left: front and left side, sunlit; right: back
and right side). Look at the picture with the Read tool every time. Add `--blend` on the last run
to save `art/town/blend/<id>.blend`.

## The frame

- Metres. `x` to the right, `y` away from the street, `z` up. **The front faces -y. The front wall
  stands on y = 0 and the building is centred on x = 0**, so it occupies x in ±frontage/2 and y in
  0..depth. The ground is z = 0 and flat; the assembler seats the building on the terrain, and the
  hidden foundation that `P.plinth` / `P.round_base` add (3 m deep) covers a slope. Give every
  building one of those under each volume that touches the ground.
- Steps, benches, barrels, awnings and signs may reach up to 1.3 m in front of the wall (y < 0).
  Nothing else may leave the lot.
- `with b.at(x, y, z, rz=...)` moves the frame; parts are written in their own local frame.
- Positions on a wall: metres from its left end on a flat `Wall` (as seen from outside), compass
  degrees on a round `Ring` (0 = front, 90 = right, 180 = back). Heights are above the wall's base.

## Detail levels and budgets

Each face has a level: 0 = structure, always drawn; 1 = dropped beyond a few hundred metres;
2 = dropped beyond about 120 m. The parts set sensible levels themselves; wrap your own fine work
in `with b.detail(2):`. The far level must still be a complete building (walls, roofs, window
panes), which is what you get if structure comes from `b.body`, `b.round`, `b.polygon` and the
roof calls.

Budgets per building (the `BUILT` line prints them): **at most 14,000 triangles in all, at most
7,000 at mid level and 3,500 at far level**; typical houses should land at 5,000 to 9,000. A
landmark may use up to 25,000. Small props: 100 to 2,500.

## Landing places

About a quarter of the buildings have a place where the rider can land her broom: the briefs say
which. A landing place is a **clear, level floor high up**: a gallery round a tower under the
eaves, a railed lighthouse-style walkway round a lantern, a flat roof terrace inside a parapet, an
open belfry floor, a roof deck, a mill's stage. Requirements:

- at least 0.75 m radius of clear floor around the spot (she stands there holding a 2 m broom);
- open to the air on the approach side: a gap in the railing or no railing there, nothing
  overhead that she would have to duck under for at least 2.5 m above the floor along the approach;
- 9 m or more above the ground for towers (roof decks on houses may be lower);
- mark it with `b.pad(x, y, z, radius, face=<compass degrees she looks, outward over the view>,
  name="...")` in the frame where the floor is, and paint it with `P.landing_mark(b, radius)`.
- make the way she would get down believable: a door onto the gallery, a hatch, a ladder.

## Style

A storybook coastal village: hand-built, a little crooked, loved for centuries. Think of chunky
stone towers given a second life as homes and hostels, timber verandas hung on old masonry,
lime-washed houses with bright shutters, washing lines and flower boxes.

- **Shapes first.** Vary the silhouette: no plain boxes. Step storeys in or out, add a lean-to, a
  stair turret, a bay, an oriel on brackets, a taller chimney, a dormer, an off-centre door. Towers
  taper and their roofs flare at the eaves. Nothing is quite symmetrical.
- **Materials.** Warm rubble stone (`masonry`), pale dressed stone (`ashlar`) for trim and grander
  walls, lime plaster in soft washes (`cream`, `white`, `butter`, `ochre`, `rose`, `peach`, `sage`,
  `sky`, `lilac`, `sand`), dark oak timber. Roofs: terracotta `tiles` on most houses, `slate` on
  towers and spires, `thatch` and `shingle` now and then. Stone below, plaster or timber above.
- **One accent colour per building** for doors, shutters and frames, from the paints (`green`,
  `teal`, `blue`, `navy`, `red`, `mustard`, `plum`, `pink`, `mint`, `orange`, `brown`, `ivory`).
- **Life.** Every building gets two or three small stories: a shop sign, laundry, a bench and a
  barrel by the door, ivy up a corner, a cat-sized dormer, a weathervane, smoke from the chimney
  (`P.chimney` adds it), stones showing through fallen plaster (`P.exposed`), a flag.
- **Every wall a passer-by can see has openings.** A street door on the front. Windows sit at
  sensible storey heights but need not line up.
- Everything must be original: no text, no logos, nothing taken from an existing film, game or book.

## More parts, and things to know

`parts_c.py` (written for the upper town) is a second library of proven parts that anyone may
import and use (`import parts_c as PC`; read its docstrings, do not edit it): true tapered square
and many-sided towers (`tbody`, `poly_tower`), roofless shells with ragged tops (`shell`),
corbels, battlements with gaps, stone walks and deck arcs for galleries, `rail_arc`, a vaulted
passage (`vault`), arch stones, buttresses, crow-stepped gables, tall chimney stacks, garden
walls, gate piers, wooden gates and walled yards, round windows for gables (`oculus`: the kit
cannot cut an opening in a gable), a well, a pergola, an outside stair, domes and ribs, vanes,
banners, doves, a cat, urns, flower clumps, climbers, pots, a lamp post, a roof hatch.

`parts_m.py` (written for the market square) may be used the same way (`import parts_m as PM`):
shop fronts, bay and oriel windows, mullioned and round windows, real openings cut in gables
(`gable_holes`), see-through arcades (two walls back to back), jetties, big chimneys, signs, a
hoist, bunting, stalls.

`parts_h.py` (written for the harbour) likewise (`import parts_h as PH`): shaped walls that can
still be cut (`gwall`: gables, lean-to ends, crow steps), `leanto`, a dark lining behind an open
doorway, loading doors, hatches, louvres, a hoist with loads, boarding battens, and quay clutter
(nets, floats, rope coils, pots, bollards, anchors, oars, buoys, fish racks, baskets, a clinker
`hull`, a gull).

`parts_l.py` (lanes), `parts_k.py` (craft row), `parts_p.py` (street furniture, quays, boats,
trees), `parts_v.py` (the cliff village: battered walls of any outline, roped thatch, turf roofs,
drystone) and `parts_f.py` (farms: thatch, mill sails, barn doors, hay, carts) are libraries of
the same kind; each lists what it holds at its top.

- Every opening's edges cut right across its wall, so many openings of different sizes and
  heights multiply the far-level triangles: line windows up in rows and columns, or plant a
  shutter on the wall (`PH.shutter`) instead of cutting where it will not be missed.
- A hipped roof (`loop_roof`) has no underside: over an open hall, board it yourself.
- `P.timber_frame` draws posts and rails straight across openings: place them by hand around one.
- Keep 10 cm clear of the lot's sides and back (the wobble moves things a few centimetres), and
  keep shutters off walls that stand on the lot's edge.
- Model everything yourself: do not start helpers or sub-agents of your own.
- On a round tower give the stone foot the wall (`P.round_base(b, r, ring=wall)`) so that the
  doorway is left clear; `P.plinth(body)` leaves doorways clear by itself.
- `b.polygon(..., taper<1)` leans flat faces that cross at the corners: for a tapered tower use
  `PC.tbody` or `PC.poly_tower`.
- A lean-to roof (`b.gable_roof(..., half=True)`) has its high edge on the line y and falls
  toward -y; `PC.shed_roof` wraps it.
- For painted railings and woodwork prefer `mat="planks"` with a paint colour.
- Stairs and railings are mid-level detail (they are not drawn far away).

## Where things stand: the layout

`layout.py` seats everything. Buildings get a lot of their own (`S.put`, or `S.line_up` along one
side of a street) and the ground is levelled under them. Props do not change the ground:
`S.prop(id, x, z, yaw, y=None, clear=...)` stands one, `S.along` lays pieces end to end along a
line (a quay edge, a field wall), `S.walled` builds a walled enclosure, `S.rows` an orchard and
`S.scatter` sprinkles a patch. `clear="lots"` keeps a prop off buildings, `"yard"` also off other
props, `"all"` also off streets and squares. Harbour pieces carry on 7.5 m below their deck, so
give them an explicit `y` (the quay's paving is at 4.46 m, the moles' at 2.95 m). Boats and buoys
are modelled with their water line at z = 0 and `"float": True` in their META: the game floats
them on the swell. A `kind="grass"` plaza is a mown green or a farmyard: the meadow stops at its
edge. `art/town/plan_<town>.png` is drawn on every run: look at it.

## Rules of the workshop

- Do not edit `kit.py`, `parts.py`, `make.py` or another modeller's files. If you need a new part,
  write it in your own module `tools/town/parts_<yourprefix>.py` with the kit primitives and import
  it. If you find a bug in the kit, work around it and say so in your report.
- Module names are the building ids and must be unique: use your prefix.
- Iterate on every building at least twice after looking at its picture. Check both views: is the
  silhouette interesting, do the roofs meet the walls, is anything floating, buried, inside-out
  (dark faces) or poking through? Is the landing place really clear?
