# Acetaminophen Synthesis by Computational Chemistry

This repository documents a computational study of acetaminophen, also known as paracetamol. It follows the reaction between 4-aminophenol and acetic anhydride and combines geometry optimization, vibrational analysis, frontier-orbital inspection, and thermodynamic post-processing.

The project is written to be readable by a broad audience while still preserving the structure of a real computational chemistry workflow.

## At a Glance

- Focus: acetaminophen formation from simple organic reactants.
- Methods: xTB geometry optimization, ALPB solvation, vibrational analysis, HOMO/LUMO inspection, and thermodynamic calculations.
- Environments: gas phase and water.
- Outputs: optimized structures, vibrational spectra, orbital input files, and temperature-dependent thermodynamic tables.

## Why This Project Matters

Acetaminophen is one of the best-known pain relievers in modern medicine. This project shows how its formation can be studied computationally and how the surrounding environment changes the behavior of the molecules involved.

In practice, the repository helps answer questions such as:

- How does the reaction proceed from reactants to product?
- What changes when the same system is studied in water instead of in vacuum?
- Which molecular features help explain the reactivity of the starting materials?
- How can thermodynamic quantities be summarized across several temperatures?

## Main Results

- Optimized structures for the main species involved in the mechanism.
- Vibrational data that support infrared interpretation and thermodynamic corrections.
- Molecular orbital files for visualizing HOMO and LUMO behavior.
- A consolidated thermodynamic summary in `mecanismos_reaccion/resumen_termodinamico.csv`.
- A full written report in `Informe_completo.md`.

## Repository Structure

The repository is organized by chemical species, solvent environment, and calculation type.

```text
AcetaminophenSynthesis/
├── Informe_completo.md
├── README.md
├── scripts_termo/
│   ├── new_thermo.py
│   └── script_thermo_xtb_complete_all.py
├── acetaminofen/
├── acido_acetico/
├── aminofenol/
├── anhídrido_acético/
├── molecula_intermedia/
└── mecanismos_reaccion/
```

Each molecule folder follows the same pattern:

```text
[molecule]/
├── gas/
│   ├── opt/
│   ├── ir/
│   ├── mo/
│   └── thermo/
└── water/
        ├── opt/
        ├── ir/
        ├── mo/
        └── thermo/
```

### Folder Guide

- `opt/` stores geometry optimization results.
- `ir/` stores vibrational data and infrared-related outputs.
- `mo/` stores files used to inspect molecular orbitals.
- `thermo/` stores the inputs and outputs used for thermodynamic processing.

## Molecules Included

The project includes the main species involved in the mechanism:

- 4-aminophenol, the starting nucleophile.
- Acetic anhydride, the acylating agent.
- An intermediate species formed along the reaction path.
- Acetic acid, the byproduct.
- Acetaminophen, the final product.

## Workflow Overview

1. Molecular structures are optimized with xTB.
2. The same systems are studied in gas phase and in water using the ALPB solvation model.
3. Vibrational spectra are used to interpret the systems and support thermodynamic corrections.
4. Molecular orbital files are generated for HOMO/LUMO inspection.
5. A thermodynamic script combines vibrational contributions with SCF energies across temperatures.

## How To Use The Repository

### Read the report

Open `Informe_completo.md` for the full explanation of the chemistry, methodology, and results.

### Compare thermodynamics

Open `mecanismos_reaccion/resumen_termodinamico.csv` to compare ZPE, enthalpy, entropy, and Gibbs free energy across molecules, solvents, and temperatures.

### Visualize geometries

Open any `[molecule]/water/opt/xtbopt.xyz` file in Avogadro, VMD, or another molecular viewer to inspect optimized geometries.

### Inspect orbitals

Open any `[molecule]/water/mo/molden.input` file in a quantum chemistry visualization tool to inspect frontier orbitals.

### Review vibrational data

Inspect `[molecule]/water/ir/vibspectrum` for the simulated infrared information.

## Thermodynamic Scripts

The `scripts_termo/` folder contains the Python scripts used to process xTB outputs.

- `new_thermo.py` is the corrected and vectorized version used in the project pipeline.
- `script_thermo_xtb_complete_all.py` is the earlier baseline version kept for reference.

### Example usage

```bash
python scripts_termo/new_thermo.py \
    --temps 298.1 353.1 373.1 \
    --file path/to/vibspectrum \
    --out path/to/xtb_output.out
```

Add `--linear` if the system is linear.

## Notes

- The detailed report is written in Spanish, while this README gives an English overview for general readers.

## Author

Mariana Lopera Correa