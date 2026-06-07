#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="/home/Mayday3003/Documents/github_repos/AcetaminophenSynthesis"

command -v xtb >/dev/null || {
    echo "ERROR: xtb no encontrado"
    exit 1
}

command -v python3 >/dev/null || {
    echo "ERROR: python3 no encontrado"
    exit 1
}

find "$BASE_DIR" -type f -name "*.sdf" | while read -r sdf; do

    mol_dir=$(dirname "$sdf")
    mol_name=$(basename "$sdf" .sdf)

    echo
    echo "========================================"
    echo "Procesando: $mol_name"
    echo "========================================"

    ########################################
    # Crear estructura
    ########################################

    mkdir -p "$mol_dir/gas/opt"
    mkdir -p "$mol_dir/gas/ir"
    mkdir -p "$mol_dir/gas/mo"

    mkdir -p "$mol_dir/water/opt"
    mkdir -p "$mol_dir/water/ir"
    mkdir -p "$mol_dir/water/mo"

    ########################################
    # SDF -> XYZ GAS
    ########################################

    GAS_XYZ="$mol_dir/gas/opt/${mol_name}.xyz"

    python3 << EOF
from ase.io import read, write
atoms = read(r"$sdf")
write(r"$GAS_XYZ", atoms)
EOF

    ########################################
    # OPT GAS
    ########################################

    echo "Optimizacion GAS"

    (
        cd "$mol_dir/gas/opt"

        xtb "${mol_name}.xyz" \
            --opt \
            > output.out
    )

    ########################################
    # IR GAS
    ########################################

    cp "$mol_dir/gas/opt/xtbopt.xyz" \
       "$mol_dir/gas/ir/"

    (
        cd "$mol_dir/gas/ir"

        xtb xtbopt.xyz \
            --hess \
            > hess.out
    )

    ########################################
    # MOLDEN GAS
    ########################################

    cp "$mol_dir/gas/opt/xtbopt.xyz" \
       "$mol_dir/gas/mo/"

    (
        cd "$mol_dir/gas/mo"

        xtb xtbopt.xyz \
            --molden \
            > molden.out
    )

    ########################################
    # SDF -> XYZ WATER
    ########################################

    WATER_XYZ="$mol_dir/water/opt/${mol_name}.xyz"

    cp "$GAS_XYZ" "$WATER_XYZ"

    ########################################
    # OPT WATER
    ########################################

    echo "Optimizacion WATER"

    (
        cd "$mol_dir/water/opt"

        xtb "${mol_name}.xyz" \
            --opt \
            --alpb water \
            > output.out
    )

    ########################################
    # IR WATER
    ########################################

    cp "$mol_dir/water/opt/xtbopt.xyz" \
       "$mol_dir/water/ir/"

    (
        cd "$mol_dir/water/ir"

        xtb xtbopt.xyz \
            --hess \
            --alpb water \
            > hess.out
    )

    ########################################
    # MOLDEN WATER
    ########################################

    cp "$mol_dir/water/opt/xtbopt.xyz" \
       "$mol_dir/water/mo/"

    (
        cd "$mol_dir/water/mo"

        xtb xtbopt.xyz \
            --molden \
            --alpb water \
            > molden.out
    )

    echo "Finalizado: $mol_name"

done

echo
echo "TODOS LOS CALCULOS TERMINADOS"