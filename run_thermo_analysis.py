import os
import shutil
import subprocess
import pandas as pd
import re

def main():
    # Directorio raíz del repositorio
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    thermo_script = os.path.join(repo_dir, "new_thermo.py")
    
    if not os.path.exists(thermo_script):
        print("Error: new_thermo.py no se encuentra en el directorio raíz.")
        return

    # Carpetas que no son moléculas
    ignore_dirs = {".git", "images", "__pycache__"}
    
    data_records = []
    
    print("Iniciando análisis termodinámico...")
    
    # Recorrer todas las carpetas del repositorio
    for molecule_dir in os.listdir(repo_dir):
        if molecule_dir in ignore_dirs or not os.path.isdir(os.path.join(repo_dir, molecule_dir)):
            continue
            
        mol_path = os.path.join(repo_dir, molecule_dir)
        
        # Buscar en entornos water y gas
        for env in ["water", "gas"]:
            env_path = os.path.join(mol_path, env)
            if os.path.isdir(env_path):
                opt_out = os.path.join(env_path, "opt", "output.out")
                ir_vib = os.path.join(env_path, "ir", "vibspectrum")
                
                # Verificar que los archivos necesarios existan
                if os.path.exists(opt_out) and os.path.exists(ir_vib):
                    print(f"Procesando: {molecule_dir} ({env})")
                    
                    thermo_dir = os.path.join(env_path, "thermo")
                    os.makedirs(thermo_dir, exist_ok=True)
                    
                    # Copiar archivos a la carpeta thermo
                    copied_opt = os.path.join(thermo_dir, "output.out")
                    copied_ir = os.path.join(thermo_dir, "vibspectrum")
                    shutil.copy(opt_out, copied_opt)
                    shutil.copy(ir_vib, copied_ir)
                    
                    # Ejecutar new_thermo.py a las 3 temperaturas
                    # 298.15 K (ambiente), 353.15 K (80 C), 373.15 K (100 C)
                    cmd = [
                        "python", thermo_script, 
                        "--temps", "298.15", "353.15", "373.15", 
                        "--file", "vibspectrum", 
                        "--out", "output.out"
                    ]
                    
                    # Ejecutar el comando haciendo que el directorio de trabajo sea la carpeta thermo
                    # De esta forma "thermodynamics_output.txt" se guarda directamente allí.
                    result = subprocess.run(cmd, cwd=thermo_dir, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"  Error ejecutando new_thermo en {thermo_dir}:\n{result.stderr}")
                        continue
                        
                    # Extraer datos del archivo de salida
                    out_txt_path = os.path.join(thermo_dir, "thermodynamics_output.txt")
                    if os.path.exists(out_txt_path):
                        with open(out_txt_path, "r") as f:
                            content = f.read()
                            
                        # El script new_thermo imprime las temperaturas con 1 decimal (ej. 298.1 K)
                        for temp in ["298.1", "353.1", "373.1"]: 
                            zpe_match = re.search(rf"--- {temp} K ---\nEnergía Punto Cero \(ZPE\):\s+([-\d.]+) eV", content)
                            h_match = re.search(rf"--- {temp} K ---\n.*?\nEntalpía Total \(H_tot\):\s+([-\d.]+) eV", content, re.DOTALL)
                            s_match = re.search(rf"--- {temp} K ---\n.*?\nEntropía Total \(S_tot\):\s+([-\d.]+) kcal/\(mol·K\)", content, re.DOTALL)
                            g_match = re.search(rf"--- {temp} K ---\n.*?\nEnergía de Gibbs \(G_tot\):\s+([-\d.]+) eV", content, re.DOTALL)
                            
                            if zpe_match and h_match and s_match and g_match:
                                data_records.append({
                                    "Molécula": molecule_dir,
                                    "Entorno": env,
                                    "Temperatura (K)": float(temp),
                                    "ZPE (eV)": float(zpe_match.group(1)),
                                    "H_tot (eV)": float(h_match.group(1)),
                                    "S_tot (kcal/mol·K)": float(s_match.group(1)),
                                    "G_tot (eV)": float(g_match.group(1))
                                })
                            else:
                                print(f"  Advertencia: No se pudieron extraer datos para {temp} K")
                    else:
                        print(f"  Advertencia: No se generó thermodynamics_output.txt")

    # Crear el DataFrame y guardarlo a CSV
    if data_records:
        df = pd.DataFrame(data_records)
        csv_path = os.path.join(repo_dir, "resumen_termodinamico.csv")
        df.to_csv(csv_path, index=False)
        print(f"\n¡Éxito! Resumen termodinámico guardado en:\n{csv_path}\n")
        print("Vista previa de los resultados:")
        print(df.to_string(index=False))
    else:
        print("\nNo se extrajeron datos para generar el CSV.")

if __name__ == "__main__":
    main()
