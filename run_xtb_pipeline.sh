#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="/home/Mayday3003/Documents/github_repos/AcetaminophenSynthesis"

find "$BASE_DIR" -mindepth 2 -type f -name "*.sdf" | while read -r sdf; do

    parent_dir=$(dirname "$sdf")
    sdf_name=$(basename "$sdf" .sdf)

    echo "Procesando $sdf"

    mkdir -p "$parent_dir/opt"
    mkdir -p "$parent_dir/ir"
    mkdir -p "$parent_dir/mo"

    xyz_file="$parent_dir/opt/${sdf_name}.xyz"

    python3 << EOF
from ase.io import read, write

atoms = read(r"$sdf")
write(r"$xyz_file", atoms)
EOF

    (
        cd "$parent_dir/opt"
        xtb "${sdf_name}.xyz" --opt > output.out
    )

    cp "$parent_dir/opt/xtbopt.xyz" "$parent_dir/ir/"
    cp "$parent_dir/opt/xtbopt.xyz" "$parent_dir/mo/"

    (
        cd "$parent_dir/ir"
        xtb xtbopt.xyz --hess > hess.out
    )

    (
        cd "$parent_dir/mo"
        xtb xtbopt.xyz --molden > molden.out
    )

    echo "✓ Terminado: $sdf_name"

done