#!/bin/bash
# Rebuild the generated (Meshy) models of the six eastern places from art/places_east/meshy/*.
# Usage: tools/blender/place_east_build.sh [name ...]      (no names = all)
# The hand-modelled plants and dressing come from place_east_flora.py, the layout (east.json) from
# place_east_layout.py.
set -u
cd "$(dirname "$0")/../.."
B=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
PY=${PYTHON:-tools/.venv/bin/python}
M=art/places_east/meshy
O=assets/places/models
L=art/places_east/logs
mkdir -p "$O" "$L"

want() { [ $# -eq 0 ] && return 0; local n=$1; shift; for a in "$@"; do [ "$a" = "$n" ] && return 0; done; return 1; }
run() {
  local n=$1; shift
  "$B" -b -P tools/blender/place_east_process.py -- "$M/$n/$n.glb" "$O/east_$n.glb" "east_$n" "$@" > "$L/proc_$n.log" 2>&1
  grep -E "EXPORTED|Error|Traceback|sheet failed" "$L/proc_$n.log" || echo "$n: no output, see $L/proc_$n.log"
  "$PY" tools/blender/place_east_pack.py "$O/east_$n.glb"
}
job() { local n=$1; if [ ${#ONLY[@]} -eq 0 ] || want "$n" "${ONLY[@]}"; then run "$@" & fi; }
ONLY=("$@")

# ---- 1. The Thousand-Wish Pine
job pine      12.5 14000 1024 wind=pine slabs=columns cell=1.2 foliage=0.6
job cairn     2.8  5000 1024 ntex=512
job bell      1.15 2500  512 cloth=paper clothdim=0.4,0.07 slabs=none solid=none
wait
# ---- 2. The Kettle Pools
job pools     15  11000 1024 fit=length sink=0.35
job emberleaf 8.5 12000 1024 wind=ember slabs=columns cell=1.2 foliage=0.5
job emberstone 0.8 2000  512 glowkey=amber glowcol=1,0.5,0.16,7 slabs=none solid=none
wait
# ---- 3. Starfall
job meteor    4.8  7000 1024 sink=0.5 glow=ice glowcol=0.55,0.85,1,2.5 solid=slabs
job splinter  1.1  2000  512 pre=y70 glow=ice glowcol=0.6,0.9,1,3 slabs=none solid=none
# ---- 4. The Conch Garden
job conch     8.4 10000 1024 fit=length sink=0.2
job clam      3.4  6000 1024 fit=length sink=0.1 ntex=512
job coral     3.6  7000 1024 ntex=512
wait
# ---- 5. Lantern Roots
job mangrove  15  15000 1024 wind=mangrove glow=lantern glowkey=amber glowcol=1,0.62,0.30,5 slabs=columns cell=1.3 foliage=0.6
job skiff     5.0  5000 1024 fit=length align=1 glowkey=amber glowcol=1,0.6,0.3,5 ntex=512
job ferrylight 0.95 2500 512 glowkey=amber glowcol=1,0.72,0.36,4.5 slabs=none solid=none
wait
# ---- 6. The Whalebone Arbour
job whale     30  15000 1024 fit=length align=1 slabs=columns cell=0.85 sink=0.35 solid=bulk bulk=8 baser=1.2
job driftwood 3.8  5500 1024 sink=0.12 ntex=512
job songbone  0.9  2000  512 slabs=none solid=none
wait
