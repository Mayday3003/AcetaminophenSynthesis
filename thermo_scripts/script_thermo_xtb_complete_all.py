import numpy as np
import argparse
import re

# Constants
R = 0.0019872  # kcal/(mol·K)  (gas constant in kcal/mol·K)
kcal_to_eV = 0.0433641  # conversion: 1 kcal/mol = 0.0433641 eV
hartree_to_eV = 27.2114  # conversion: 1 Hartree = 27.2114 eV

def extract_frequencies(file_path):
    freqs = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    val = float(parts[2])
                    if val > 0:
                        freqs.append(val)
                except:
                    continue
    return freqs

def extract_scf_energy(out_file_path):
    with open(out_file_path, 'r') as f:
        text = f.read()
    # Look for a line containing "TOTAL ENERGY" or similar
    match = re.search(r'TOTAL ENERGY\s+([-]?\d+\.\d+)', text)
    if match:
        return float(match.group(1))
    else:
        print("Could not find SCF energy in the output file.")
        exit()

def thermodynamics(frequencies_cm1, T, num_atoms, is_linear_molecule=True):
    # Convert vibrational frequencies from cm^-1 to kcal/mol
    frequencies_kcal = np.array(frequencies_cm1) * 0.0002909

    # Zero Point Energy (ZPE)
    ZPE_kcal = 0.5 * np.sum(frequencies_kcal)
    ZPE_eV = ZPE_kcal * kcal_to_eV

    # Vibrational entropy (S_vib, in kcal/(mol·K))
    S_vib = R * np.sum([
        (freq / (R * T)) / (np.exp(freq / (R * T)) - 1) - np.log(1 - np.exp(-freq / (R * T)))
        for freq in frequencies_kcal
    ])

    # Vibrational enthalpy (H_vib, in kcal/mol)
    H_vib = np.sum([
        freq / (np.exp(freq / (R * T)) - 1)
        for freq in frequencies_kcal
    ])

    # Translational contribution
    S_trans = R * (5 / 2)      # in kcal/(mol·K)
    H_trans = (3 / 2) * R * T  # in kcal/mol

    # Rotational contribution
    if is_linear_molecule:
        S_rot = R * (3 / 2)      # in kcal/(mol·K)
        H_rot = (3 / 2) * R * T  # in kcal/mol
    else:
        S_rot = R * (3)          # in kcal/(mol·K)
        H_rot = (3 / 2) * R * T  # in kcal/mol

    # Total entropy in kcal/(mol·K) and enthalpy in kcal/mol
    S_total = S_vib + S_trans + S_rot
    H_total_kcal = H_vib + H_trans + H_rot

    # Add Zero Point Energy to enthalpy and convert to eV
    H_total_eV = (H_total_kcal * kcal_to_eV) + ZPE_eV

    # Gibbs Free Energy without ZPE added later (in eV)
    G_total_eV = H_total_eV - T * (S_total * kcal_to_eV)

    # In this formulation, we want the final free energy to include the ZPE
    G_total_eV_with_ZPE = G_total_eV + ZPE_eV

    return ZPE_eV, H_total_eV, S_total, G_total_eV_with_ZPE

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute thermodynamic data from vibrational frequencies + SCF energy from xtb.out"
    )
    parser.add_argument("--temps", nargs="+", type=float, required=True, help="List of temperatures (in K)")
    parser.add_argument("--file", type=str, required=True, help="Path to vibspectrum file")
    parser.add_argument("--out", type=str, required=True, help="Path to xtb output file (to extract SCF energy)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    temperatures = args.temps
    vibspectrum_file = args.file
    out_file = args.out

    # Extract data
    frequencies = extract_frequencies(vibspectrum_file)
    if not frequencies:
        print("No valid frequencies found.")
        exit()

    scf_energy_hartree = extract_scf_energy(out_file)
    scf_energy_eV = scf_energy_hartree * hartree_to_eV

    with open("thermodynamics_output.txt", "w") as f:
        f.write(f"Thermodynamic properties (vibrational + ZPE + SCF) from {vibspectrum_file}\n")
        f.write(f"SCF Energy extracted from {out_file}: {scf_energy_hartree:.8f} Hartree = {scf_energy_eV:.5f} eV\n\n")

        for T in temperatures:
            # Here, num_atoms is provided in case you need it later;
            # Adjust 'is_linear_molecule' to False if your molecule is nonlinear.
            ZPE_eV, H_total_eV, S_total, G_total_eV_with_ZPE = thermodynamics(frequencies, T, num_atoms=10, is_linear_molecule=True)

            # Add SCF energy to the total enthalpy
            H_total_eV_with_SCF = scf_energy_eV + H_total_eV
            # Final Gibbs free energy with SCF and including ZPE explicitly
            G_total_eV_with_SCF_and_ZPE = H_total_eV_with_SCF - T * (S_total * kcal_to_eV) + ZPE_eV

            # Write out values. S_total is in kcal/(mol·K); we also show it in eV/K by multiplying by kcal_to_eV.
            f.write(f"--- {T:.1f} K ---\n")
            f.write(f"Zero-point energy (ZPE): {ZPE_eV:.5f} eV\n")
            f.write(f"Enthalpy (H total): {H_total_eV_with_SCF:.5f} eV\n")
            f.write(f"Entropy (S total): {S_total:.5f} kcal/(mol·K) or {S_total * kcal_to_eV:.5f} eV/K\n")
            f.write(f"Gibbs Free Energy (G total, with ZPE): {G_total_eV_with_SCF_and_ZPE:.5f} eV\n\n")

            print(f"{T:.1f} K → ZPE: {ZPE_eV:.5f} eV | H: {H_total_eV_with_SCF:.5f} eV | " \
                  f"S: {S_total:.5f} kcal/(mol·K) or {S_total * kcal_to_eV:.5f} eV/K | " \
                  f"G: {G_total_eV_with_SCF_and_ZPE:.5f} eV")

    print("\nAll results saved to 'thermodynamics_output.txt'")


