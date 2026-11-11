#!/bin/bash
set -e
source /opt/openfoam13/etc/bashrc
for case in /tmp/fan_jump_nx4_forward /tmp/fan_jump_nx4_reverse
do
 cd "$case"
 blockMesh > log.blockMesh 2>&1
 foamRun > log.foamRun 2>&1
done
