import argparse
import subprocess
import os
import zipfile
import shutil
from Bio import SeqIO
import re
from decoradores import log_action_decorator

class DescargarProteomasNCBI:
    """Clase para descargar, procesar y gestionar proteomas desde NCBI.

    Attributes:
        output_dir (str): Directorio donde se guardarán los archivos descargados.
        output_dir2 (str): Directorio específico para la descarga de NCBI.
        remove_mitochondrial (bool): Indica si se deben remover las proteínas mitocondriales.
        should_process_fasta (bool): Indica si se deben procesar los archivos FASTA.
        concatenate (bool): Indica si se deben concatenar los archivos FASTA.
    """
    def __init__(self, output_dir, remove_mitochondrial=False, process_fasta=False, concatenate=False):
        """Inicializa la clase con los parámetros dados.

        Args:
            output_dir (str): Ruta del directorio de salida.
            remove_mitochondrial (bool): Opción para remover proteínas mitocondriales.
            process_fasta (bool): Opción para procesar archivos FASTA.
            concatenate (bool): Opción para concatenar archivos FASTA.
        """
        self.output_dir = os.path.abspath(output_dir)
        self.output_dir2 = os.path.join(os.getcwd(), 'NCBI')
        self.remove_mitochondrial = remove_mitochondrial
        self.should_process_fasta = process_fasta  # Renombrado para evitar conflicto
        self.concatenate = concatenate
   
    @log_action_decorator
    def download_genome(self, species_list):
        """Descarga y procesa el genoma de una lista de especies.

        Args:
            species_list (list): Lista de nombres de especies a descargar.
        """
        base_command = "datasets download genome taxon"
        options = "--reference --include protein"

        for species in species_list:
            species_name = species.replace(' ', '_')
            zip_filename = os.path.join(self.output_dir, "ncbi_dataset.zip")
            temp_dir = os.path.join(self.output_dir, "ncbi_dataset")
            extract_dir = os.path.join(self.output_dir, species_name)

            command = f'{base_command} "{species}" {options}'
            print(f"Ejecutando: {command}")
            subprocess.run(command, shell=True, check=True)

            if os.path.exists(zip_filename):
                print(f"Descargado: {zip_filename}")
                with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    print(f"Extraído en: {temp_dir}")

                    if os.path.exists(temp_dir):
                        if os.path.exists(extract_dir):
                            print(f"Error: {extract_dir} ya existe.")
                        else:
                            os.rename(temp_dir, extract_dir)
                            print(f"Carpeta descomprimida renombrada: {extract_dir}")
                    else:
                        print(f"Error: {temp_dir} no encontrado.")
                
                os.remove(zip_filename)
                print(f"Archivo comprimido eliminado: {zip_filename}")

                protein_faa_path = self.find_protein_faa(extract_dir)
                if protein_faa_path:
                    new_protein_faa_path = os.path.join(self.output_dir, f"{species_name}_protein.faa")
                    shutil.move(protein_faa_path, new_protein_faa_path)
                    print(f"Movido y renombrado {protein_faa_path} a {new_protein_faa_path}")
                    
                    if self.remove_mitochondrial:
                        self.remove_mitochondrial_proteins(new_protein_faa_path)
                    
                    if self.should_process_fasta:
                        self.process_fasta(new_protein_faa_path)
                else:
                    print(f"protein.faa no encontrado para {species_name}")
            else:
                print(f"Error: {zip_filename} no encontrado.")
    @log_action_decorator
    def download_genome2(self, species_list):
            """Descarga y procesa el genoma de una lista de especies en un directorio NCBI.

        Args:
            species_list (list): Lista de nombres de especies a descargar.
        """
            base_command = "datasets download genome taxon"
            options = "--reference --include protein"

            for species in species_list:
                species_name = species.replace(' ', '_')
                zip_filename = os.path.join(self.output_dir2, "ncbi_dataset.zip")
                temp_dir = os.path.join(self.output_dir2, "ncbi_dataset")
                extract_dir = os.path.join(self.output_dir2, species_name)
                command = f'{base_command} "{species}" {options}'
                print(f"Executing: {command}")
                subprocess.run(command, shell=True, cwd=self.output_dir2, check=True)

                if os.path.exists(zip_filename):
                    print(f"Downloaded: {zip_filename}")
                    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                        print(f"Extracted to: {temp_dir}")

                        if os.path.exists(temp_dir):
                            if os.path.exists(extract_dir):
                                print(f"Error: {extract_dir} ya existe.")
                            else:
                                os.rename(temp_dir, extract_dir)
                                print(f"Carpeta extraída renombrada: {extract_dir}")
                        else:
                            print(f"Error: {temp_dir} no encontrado.")
                    
                    os.remove(zip_filename)
                    print(f"Archivo comprimido eliminado: {zip_filename}")

                    protein_faa_path = self.find_protein_faa(extract_dir)
                    if protein_faa_path:
                        new_protein_faa_path = os.path.join(self.output_dir, f"{species_name}_protein.faa")
                        shutil.move(protein_faa_path, new_protein_faa_path)
                        print(f"Movido y renombrado {protein_faa_path} a {new_protein_faa_path}")
                        
                        if self.remove_mitochondrial:
                            self.remove_mitochondrial_proteins(new_protein_faa_path)
                        
                        if self.should_process_fasta:
                            self.process_fasta(new_protein_faa_path)
                    else:
                        print(f"protein.faa no encontrado para {species_name}")
                else:
                    print(f"Error: {zip_filename} no encontrado.")

    @log_action_decorator
    def find_protein_faa(self, directory):
        """Busca el archivo protein.faa en la estructura de directorios."""
        """Busca el archivo protein.faa en la estructura de directorios.

        Args:
            directory (str): Ruta del directorio donde buscar.

        Returns:
            str: Ruta completa al archivo protein.faa si se encuentra, de lo contrario None.
        """
        for root, dirs, files in os.walk(directory):
            if "protein.faa" in files:
                return os.path.join(root, "protein.faa")
        return None
    @log_action_decorator
    def remove_mitochondrial_proteins(self, faa_file):
        """Procesa el archivo FASTA para conservar solo la secuencia más larga para cada nombre único.

        Args:
            faa_file (str): Ruta del archivo .faa de entrada.
        """
        """Genera un nuevo archivo sin secuencias mitocondriales."""
        output_file = faa_file.replace('.faa', '_sinmitocondrial.faa')
        with open(faa_file, 'r') as infile, open(output_file, 'w') as outfile:
            write_sequence = True
            for line in infile:
                if line.startswith('>'):
                    if 'mitochondrion' in line.lower():
                        write_sequence = False
                    else:
                        write_sequence = True
                if write_sequence:
                    outfile.write(line)
        print(f"Generación de {output_file} sin secuencias de genoma mitocondrial")
    @log_action_decorator
    def process_fasta(self, faa_file):
        """Procesa el archivo FASTA para conservar solo la secuencia más larga para cada nombre único."""
        pattern = re.compile(r"(?<=\s)([\w\s/-]+?)(?:\sisoforma|\s\[|\s\{|\s\(|\sisoform)")

        output_file_path = faa_file.replace('.faa', '_sin_isoformas.faa')
        
        max_length_dict = {}
        max_id_dict = {}
        max_seq_dict = {}
        
        species_name = os.path.basename(faa_file).replace('_sinmitocondrial.faa', '')
        genus = species_name.split('_')[0]
        species = species_name.split('_')[1] if len(species_name.split('_')) > 1 else ''
        
        suffix = f"{genus[:3].upper()}{species[:2].upper()}"
        
        for record in SeqIO.parse(faa_file, "fasta"):
            seq_id = record.id
            seq = str(record.seq)
            seq_length = len(seq)
            
            match = pattern.search(record.description)
            if match:
                name = match.group(1).strip()
            else:
                continue
            
            if name not in max_length_dict or seq_length > max_length_dict[name]:
                max_length_dict[name] = seq_length
                max_id_dict[name] = seq_id
                max_seq_dict[name] = seq
        
        result = [(name, max_id_dict[name], max_seq_dict[name]) for name in max_id_dict]
        
        with open(output_file_path, 'w') as f:
            for name, seq_id, seq in result:
                f.write(f">{seq_id}_{suffix}\n")
                f.write(f"{seq}\n\n")
        
        formateado_file_path = output_file_path.replace('_sin_isoformas.faa', '_formateado_sin_isoformas.faa')
        with open(output_file_path, 'r') as f:
            lines = f.readlines()
        
        with open(formateado_file_path, 'w') as f:
            previous_line_empty = False
            for line in lines:
                if line.startswith('>'):
                    parts = line[1:].strip().split('_', 1)
                    if len(parts) > 1:
                        new_header = f"{parts[0]}{parts[1]}"
                        f.write(f">{new_header}\n")
                    else:
                        f.write(line)
                    previous_line_empty = False
                elif line.strip() == '':
                    previous_line_empty = True
                else:
                    if previous_line_empty:
                        f.write('\n')
                    f.write(line)
                    previous_line_empty = False
        print(f"Processed {formateado_file_path}")
    @log_action_decorator
    def concatenate_fasta_files(self, concatenated_filename):
        """Concatena múltiples archivos FASTA en uno solo.

        Args:
            output_file_path (str): Ruta del archivo de salida para el archivo concatenado.
        """
        """Concatena todos los archivos _formateado_sin_isoformas.faa en un único archivo."""
        concatenated_file_path = os.path.join(self.output_dir2, f"{concatenated_filename.strip()}.faa")
        log_file_path = os.path.join(self.output_dir2, f"{concatenated_filename.strip()}_resumen.txt")
        
        files_processed = 0
        sequences_total = 0

        with open(concatenated_file_path, 'w') as outfile, open(log_file_path, 'w') as logfile:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith('_formateado_sin_isoformas.faa'):
                        file_path = os.path.join(root, file)
                        print(f"Procesando archivo: {file_path}")
                        
                        with open(file_path, 'r') as infile:
                            content = infile.read()
                            outfile.write(content)
                        
                        num_sequences = content.count('>')
                        sequences_total += num_sequences
                        files_processed += 1
                        
                        logfile.write(f"{file}\t{num_sequences}\n")
        
        if files_processed == 0:
            print("No se encontraron archivos para concatenar.")
        else:
            print(f"Se procesaron {files_processed} archivos con un total de {sequences_total} secuencias.")
            print(f"Todos los archivos _sin_isoformas.faa se han concatenado en {concatenated_file_path}")
            print(f"Archivo de resumen de concatenación generado en {log_file_path}")
@log_action_decorator
def main_ncbi():
    """Función principal que será llamada si se ejecuta éste script como principal."""
    parser = argparse.ArgumentParser(description="Download, extract, process genomes, remove mitochondrial sequences, process FASTA, and optionally concatenate FASTA files.")
    parser.add_argument('species', nargs='+', help='List of species names to download genomes for.')
    parser.add_argument('-o', '--output_dir', type=str, default=os.getcwd(), help='Directory where genomes will be downloaded and extracted.')

    args = parser.parse_args()
    output_dir = os.path.abspath(args.output_dir)

    remove_mitochondrial = input("Remover proteínas de genoma mitocondrial? (s/n): ").strip().lower() == 's'
    process_fasta_option = input("Procesar archivos FASTA para conservar solo la secuencia más larga? (s/n): ").strip().lower() == 's'
    concatenate_option = input("Concatenar archivos FASTA en un archivo único? (s/n): ").strip().lower() == 's'
    
    downloader = DescargarProteomasNCBI(output_dir, remove_mitochondrial, process_fasta_option, concatenate_option)
    downloader.download_genome(args.species)
    
    if concatenate_option:
        concatenated_filename = input("Nombre del archivo FASTA concatenado: ")
        downloader.concatenate_fasta_files(concatenated_filename)

if __name__ == "__main__":
    main_ncbi()

@log_action_decorator
def main_ncbi_importar(ncbi_ids_path=None, remove_mitochondrial=False, process_fasta_option=False, concatenate_option=False, concatenated_filename=None):
    """Función principal que será llamada cuando el script sea importado por el módulo DBuilder.py"""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directorio donde se encuentra el script
    output_dir = os.path.join(script_dir, "NCBI")  # Directorio de salida NCBI en el mismo directorio

    # Crear el directorio de salida sin verificar si ya existe
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directorio {output_dir} creado o ya existente.")

    # Si no se proporciona ncbi_ids_path, usar species_name.txt en el directorio del script
    if ncbi_ids_path is None:
        ncbi_ids_path = os.path.join(script_dir, "species_name.txt")
    
    # Verificar si el archivo de entrada existe
    if not os.path.isfile(ncbi_ids_path):
        print(f"Error: El archivo {ncbi_ids_path} no existe.")
        return

    with open(ncbi_ids_path, 'r') as file:
        species_list = [line.strip() for line in file if line.strip()]

    if not species_list:
        print("Error: No se encontraron nombres de especies en el archivo.")
        return

    downloader = DescargarProteomasNCBI(output_dir, remove_mitochondrial, process_fasta_option, concatenate_option)
    downloader.download_genome2(species_list)

    if process_fasta_option:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('_protein.faa'):
                    file_path = os.path.join(root, file)
                    downloader.process_fasta(file_path)

    if concatenate_option:
        downloader.concatenate_fasta_files(concatenated_filename)

