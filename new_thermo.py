import numpy as np
import argparse
import re

# ==========================================
# CAMBIO 1: Constantes más precisas y explícitas.
# Se reemplazó el factor de conversión "0.0002909" por la constante física 
# estándar (hc/k_B) para la conversión de frecuencias vibracionales. Esto hace 
# que el código sea universal y transparente.
# ==========================================
R_kcal = 0.0019872       # kcal/(mol·K)
kcal_to_eV = 0.0433641   
hartree_to_eV = 27.2114  
hc_over_kB = 1.4388      # cm·K (h·c / k_B)


def extract_frequencies(file_path):
    freqs = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 3:
                # CAMBIO 2: Captura de excepción específica.
                # Se cambió el "except:" desnudo por "except ValueError:". 
                # El original silenciaba cualquier error (como un fallo de memoria), 
                # lo cual es una mala práctica en Python.
                try:
                    val = float(parts[2])
                    if val > 0:
                        freqs.append(val)
                except ValueError:
                    continue
    return freqs


def extract_scf_energy(out_file_path):
    with open(out_file_path, 'r') as f:
        text = f.read()
    
    # CAMBIO 3: Expresión regular mejorada.
    # Se añadió soporte para capturar "total E" además de "TOTAL ENERGY", 
    # ya que distintas versiones de xtb varían en cómo imprimen este valor.
    match = re.search(r'TOTAL ENERGY\s+([-]?\d+\.\d+)', text)
    if not match:
        match = re.search(r'total E\s+([-]?\d+\.\d+)', text, re.IGNORECASE)
        
    if match:
        return float(match.group(1))
    else:
        # CAMBIO 4: Salida controlada.
        # El original usaba un exit() vacío. Ahora informa exactamente por qué se detuvo.
        exit("Error: No se encontró la energía SCF en el archivo de salida.")


# CAMBIO 5: Eliminación de 'num_atoms'.
# Se borró el parámetro 'num_atoms' de la función. El script original lo pedía 
# y lo pasaba (num_atoms=10), pero jamás lo usaba en ninguna ecuación.
def thermodynamics(frequencies_cm1, T, is_linear_molecule=False):
    
    # CAMBIO 6: Vectorización con NumPy.
    # El original usaba list comprehensions (bucles for dentro de listas) para las
    # sumatorias. Las operaciones vectorizadas de NumPy son más rápidas y legibles.
    theta_v = np.array(frequencies_cm1) * hc_over_kB
    x = theta_v / T

    # ==========================================
    # CAMBIO 7: Aislamiento total de la ZPE (El error principal).
    # El script original sumaba la ZPE a la Entalpía (H_total_eV), luego se la 
    # sumaba al Gibbs (G_total_eV_with_ZPE), y finalmente en el bloque 'main' la
    # volvía a sumar. Aquí la ZPE se calcula sola y se retorna limpia.
    # ==========================================
    ZPE_kcal = np.sum(0.5 * theta_v * R_kcal)
    ZPE_eV = ZPE_kcal * kcal_to_eV

    # CAMBIO 8: Estabilidad matemática en Entropía Vibracional.
    # Se añadió "+ 1e-12" dentro del np.log(). Si la frecuencia es enorme o la T muy baja, 
    # el logaritmo en el código original podía evaluarse como log(0), quebrando el script.
    U_vib_thermal = R_kcal * np.sum(theta_v / (np.exp(x) - 1))
    S_vib = R_kcal * np.sum(x / (np.exp(x) - 1) - np.log(1 - np.exp(-x) + 1e-12))

    # ==========================================
    # CAMBIO 9: Corrección Termodinámica de la Entalpía (H = U + PV).
    # El original usaba H_trans = (3/2)RT. Eso es incorrecto, esa es la Energía Interna (U).
    # Para calcular la Entalpía de un gas ideal, se debe calcular la Energía Interna
    # total primero (U_vib + U_trans + U_rot) y sumarle R*T al final.
    # ==========================================
    S_trans = (5 / 2) * R_kcal
    U_trans = (3 / 2) * R_kcal * T

    # ==========================================
    # CAMBIO 10: Grados de libertad rotacional reales.
    # El original asignaba (3/2)R y (3/2)RT a moléculas lineales. Una molécula lineal
    # solo rota en 2 ejes significativos, por lo que su aporte es R y R*T.
    # ==========================================
    if is_linear_molecule:
        U_rot = R_kcal * T
        S_rot = R_kcal 
    else:
        U_rot = (3 / 2) * R_kcal * T
        S_rot = (3 / 2) * R_kcal

    S_total = S_vib + S_trans + S_rot
    
    # Aplicación de la fórmula correcta de Entalpía térmica: H = U_tot + RT
    H_thermal_kcal = U_vib_thermal + U_trans + U_rot + R_kcal * T
    H_thermal_eV = H_thermal_kcal * kcal_to_eV

    return ZPE_eV, H_thermal_eV, S_total


def parse_args():
    parser = argparse.ArgumentParser(description="Termodinámica xtb Simplificada")
    parser.add_argument("--temps", nargs="+", type=float, required=True)
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--out", type=str, required=True)
    # CAMBIO 11: Flag dinámico para moléculas lineales.
    # El original forzaba "is_linear_molecule=True" en la línea de código. 
    # Ahora el usuario lo indica desde la terminal si es necesario.
    parser.add_argument("--linear", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    frequencies = extract_frequencies(args.file)
    if not frequencies:
        exit("Error: No se encontraron frecuencias válidas mayores a cero.")

    scf_energy_eV = extract_scf_energy(args.out) * hartree_to_eV

    with open("thermodynamics_output.txt", "w") as f:
        f.write(f"Propiedades Termodinámicas\n")
        f.write(f"Archivo de Frecuencias: {args.file}\n")
        f.write(f"Energía SCF (Base): {scf_energy_eV:.5f} eV\n\n")

        for T in args.temps:
            # Recibimos valores térmicos puros y la ZPE totalmente separada
            ZPE_eV, H_thermal_eV, S_total_kcal_mol_K = thermodynamics(frequencies, T, args.linear)

            # CAMBIO 12: Ecuaciones Finales de Gibbs sin redundancias.
            # En el original, el cálculo de Gibbs_final incluía términos enredados 
            # desde la función. Aquí la lógica es de un solo paso:
            # H_total = SCF + Calor Térmico + Energía Punto Cero
            # G_total = H_total - TS
            H_total_eV = scf_energy_eV + H_thermal_eV + ZPE_eV
            G_total_eV = H_total_eV - T * (S_total_kcal_mol_K * kcal_to_eV)

            # Escritura de resultados consolidados
            f.write(f"--- {T:.1f} K ---\n")
            f.write(f"Energía Punto Cero (ZPE):  {ZPE_eV:.5f} eV\n")
            f.write(f"Entalpía Total (H_tot):    {H_total_eV:.5f} eV\n")
            f.write(f"Entropía Total (S_tot):    {S_total_kcal_mol_K:.5f} kcal/(mol·K)\n")
            f.write(f"Energía de Gibbs (G_tot):  {G_total_eV:.5f} eV\n\n")

            print(f"{T:.1f} K → ZPE: {ZPE_eV:.5f} eV | H_tot: {H_total_eV:.5f} eV | " \
                  f"S_tot: {S_total_kcal_mol_K:.5f} kcal/(mol·K) | " \
                  f"G_tot: {G_total_eV:.5f} eV")

    print("\nResultados guardados exitosamente en 'thermodynamics_output.txt'")