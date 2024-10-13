import argparse
import requests
import gzip
import shutil
import os
from decoradores import log_action_decorator

"""
DB_Builder.py

Gestiona la descarga de proteomas desdeUniProt y NCBI. 
Opcionalmente facilita su procesamiento para Phylomizer.
Éste módulo puede ser importado o ejecutarse como main,
adoptando comportamientos distintos según corresponda. 


Autor: Campos Clara
Consultas y/o sugerencias al mail: clarahabas@gmail.com
Fecha de creación: 2024-08-21
Versión: 1.0

Dependencias:
    - UNIPROT_POO
    - NCBI_POO
"""

class UniProtDownloader:
    def __init__(self, proteome_ids, organism_ids):
        """
        Inicializa el descargador de UniProt.

        :param proteome_ids: Lista de IDs de proteomas a descargar.
        :param organism_ids: Lista de IDs de organismos correspondientes.
        """
        self.proteome_ids = proteome_ids
        self.organism_ids = organism_ids
        self.base_url = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/"
        self.downloaded_files = []
        self.output_dir = os.path.join(os.getcwd(), "UniProt")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @log_action_decorator
    def download_file(self, url, file_path):
        
        """
        Descarga un archivo desde una URL y lo guarda localmente.

        :param url: URL del archivo a descargar.
        :param file_path: Ruta donde se guardará el archivo descargado.
        :return: True si la descarga fue exitosa, False en caso contrario.
        """
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Descargado de UniProt: {file_path}")
            return True
        else:
            print(f"Error al descargar de UniProt: {file_path} - Status code: {response.status_code}")
            return False

    @log_action_decorator
    def decompress_file(self, file_path, output_file_path):
       
        """
        Descomprime un archivo .gz, lo guarda con un nuevo nombre y elimina el archivo comprimido.

        :param file_path: Ruta del archivo comprimido (.gz).
        :param output_file_path: Ruta donde se guardará el archivo descomprimido.
        """
        with gzip.open(file_path, 'rb') as f_in:
            with open(output_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file_path)
        print(f"Descomprimido y eliminado (UniProt): {file_path} -> {output_file_path}")

    @log_action_decorator
    def extract_organism_name_from_fasta(self, file_path):
        
        """
        Extrae el nombre del organismo del encabezado del archivo FASTA.

        :param file_path: Ruta del archivo FASTA.
        :return: Nombre del organismo extraído del encabezado, o None si no se puede extraer.
        """
        with open(file_path, 'r') as fasta_file:
            first_line = fasta_file.readline()
            if first_line.startswith(">"):
                organism_name = first_line.split("|")[2].split("_")[1].split(" ")[0]
                return organism_name
        return None

    @log_action_decorator
    def count_proteins_in_fasta(self, file_path):
        """
        Cuenta el número de proteínas en un archivo FASTA.

        :param file_path: Ruta del archivo FASTA.
        :return: Número de proteínas en el archivo.
        """
        with open(file_path, 'r') as fasta_file:
            count = sum(1 for line in fasta_file if line.startswith(">"))
        return count

    @log_action_decorator
    def concatenate_fastas(self, fasta_files, output_file_name, summary_file_name):
        """Concatenar múltiples archivos FASTA en un único archivo y crear un archivo resumen con los nombres de los archivos concatenados y el número de secuencias de proteínas en cada uno."""
        """
        Concatenar múltiples archivos FASTA en un único archivo y crear un archivo resumen.

        :param fasta_files: Lista de rutas de archivos FASTA a concatenar.
        :param output_file_name: Nombre del archivo de salida donde se guardará la concatenación.
        :param summary_file_name: Nombre del archivo resumen que contendrá la cantidad de proteínas por archivo.
        """
        with open(output_file_name, 'wb') as outfile:
            with open(summary_file_name, 'w') as summary_file:
                summary_file.write("Archivo\tCantidad de proteínas\n")
                for fasta_file in fasta_files:
                    with open(fasta_file, 'rb') as infile:
                        shutil.copyfileobj(infile, outfile)
                    protein_count = self.count_proteins_in_fasta(fasta_file)
                    summary_file.write(f"{fasta_file}\t{protein_count}\n")
        print(f"Archivos FASTA (UniProt) concatenados en: {output_file_name}")
        print(f"Resumen de archivos fasta de UniProt concatenados guardado en: {summary_file_name}")

    @log_action_decorator
    def format_headers_for_phylomizer(self, fasta_file, formatted_fasta_file, headers_file):
        """Formatear los encabezados de un archivo FASTA para Phylomizer y guardar los encabezados originales y modificados en un archivo TXT."""
        """
        Formatea los encabezados de un archivo FASTA para Phylomizer y guarda los encabezados originales y modificados.

        :param fasta_file: Ruta del archivo FASTA original.
        :param formatted_fasta_file: Ruta donde se guardará el archivo FASTA con encabezados formateados.
        :param headers_file: Ruta donde se guardarán los encabezados originales y modificados.
        """

        with open(fasta_file, 'r') as infile, open(formatted_fasta_file, 'w') as outfile, open(headers_file, 'w') as headers_output_file:
            headers_output_file.write("Encabezado Original\tEncabezado Modificado\n")
            for line in infile:
                if line.startswith(">"):
                    original_header = line.strip()
                    parts = original_header.split("|")
                    if len(parts) > 2:
                        new_header = f">{parts[2].split(' ')[0]}"
                        headers_output_file.write(f"{original_header}\t{new_header}\n")  
                        outfile.write(f"{new_header}\n")
                else:
                    outfile.write(line)
        print(f"Encabezados (UniProt) formateados en: {formatted_fasta_file}")
        print(f"Encabezados (UniProt) originales y modificados guardados en: {headers_file}")

    @log_action_decorator
    def process(self, concatenate, output_concat_file_name=None, summary_file_name=None,
                format_headers=False, formatted_fasta_file_name=None, headers_file_name=None):
        """
        Procesa la descarga, descompresión, renombrado y concatenación de archivos FASTA.

        :param concatenate: Indica si se deben concatenar los archivos FASTA.
        :param output_concat_file_name: Nombre del archivo de salida para la concatenación.
        :param summary_file_name: Nombre del archivo resumen que contendrá la cantidad de proteínas por archivo.
        :param format_headers: Indica si se deben formatear los encabezados.
        :param formatted_fasta_file_name: Nombre del archivo para guardar los encabezados formateados.
        :param headers_file_name: Nombre del archivo donde se guardarán los encabezados originales y modificados.
        """
        if len(self.proteome_ids) != len(self.organism_ids):
            print("El número de IDs de proteomas y IDs de organismos de UniProt debe ser igual en los archivos .txt.")
            return

        for proteome_id, organism_id in zip(self.proteome_ids, self.organism_ids):
            url = f"{self.base_url}{proteome_id}/{proteome_id}_{organism_id}.fasta.gz"
            file_name = os.path.join(self.output_dir, f"{proteome_id}_{organism_id}.fasta.gz")
            output_file_name = os.path.join(self.output_dir, f"{proteome_id}_{organism_id}.fasta")

            if self.download_file(url, file_name):
                self.decompress_file(file_name, output_file_name)
                organism_name = self.extract_organism_name_from_fasta(output_file_name)
                if organism_name:
                    final_output_file_name = os.path.join(self.output_dir, f"{proteome_id}_{organism_id}_{organism_name}.fasta")
                    os.rename(output_file_name, final_output_file_name)
                    self.downloaded_files.append(final_output_file_name)
                    print(f"Archivo (UniProt) renombrado: {output_file_name} -> {final_output_file_name}")
                else:
                    print(f"No se pudo extraer el nombre del organismo para el archivo (UniProt): {output_file_name}")

        if concatenate and output_concat_file_name and summary_file_name:
            self.concatenate_fastas(self.downloaded_files, output_concat_file_name, summary_file_name)
            
            if format_headers and formatted_fasta_file_name and headers_file_name:
                self.format_headers_for_phylomizer(output_concat_file_name, formatted_fasta_file_name, headers_file_name)
        else:
            print("No se concatenarán los archivos FASTA de los proteomas descargados de UniProt.")


@log_action_decorator
def parse_arguments_uniprot():
    """
    Analiza los argumentos de la línea de comandos para la descarga de UniProt.

    :return: Objeto que contiene los argumentos analizados.
    """
    parser = argparse.ArgumentParser(description='Descargar y descomprimir archivos FASTA de proteomas desde UniProt.')
    parser.add_argument('--proteome_ids', nargs='+', required=True, help='Lista de IDs de proteomas.')
    parser.add_argument('--organism_ids', nargs='+', required=True, help='Lista de IDs de organismos.')
    return parser.parse_args()


@log_action_decorator
def main_uniprot_import(proteome_ids, organism_ids, concatenate_option_uniprot, formatted_option_uniprot, output_concat_file_name_uniprot, output_formatted_file_name_uniprot):
    """
    Función principal que será llamada desde DBuilder_main.py 
    
    """
    downloader = UniProtDownloader(proteome_ids, organism_ids)

    if concatenate_option_uniprot in ["sí", "si"]:
        output_concat_file_name = os.path.join(downloader.output_dir, output_concat_file_name_uniprot.strip() + "_UniProt.fasta")
        summary_file_name = os.path.join(downloader.output_dir, "resumen_concatenacion_UniProt.txt")

        if formatted_option_uniprot in ["sí", "si"]:
            formatted_fasta_file_name = os.path.join(downloader.output_dir, output_formatted_file_name_uniprot.strip() + "_UNIPROT.fasta")
            headers_file_name = os.path.join(downloader.output_dir, "headers_originales_modificados_UniProt.txt")
        else:
            formatted_fasta_file_name = None
            headers_file_name = None

        downloader.process(
            concatenate=True,
            output_concat_file_name=output_concat_file_name,
            summary_file_name=summary_file_name,
            format_headers=formatted_option_uniprot in ["sí", "si"],
            formatted_fasta_file_name=formatted_fasta_file_name,
            headers_file_name=headers_file_name
        )
    else:
        downloader.process(concatenate=False)


@log_action_decorator
def main_uniprot():
    """
    Función que será llamada cuando se ejecute éste script como principal. 
    
    """
    args = parse_arguments_uniprot()
    proteome_ids = args.proteome_ids
    organism_ids = args.organism_ids

    downloader = UniProtDownloader(proteome_ids, organism_ids)
    
    concatenate = input("¿Desea concatenar todos los archivos FASTA descargados de UniProt en un único archivo? (sí/no): ").strip().lower()
    if concatenate in ["sí", "si"]:
        output_concat_file_name = os.path.join(downloader.output_dir, input("Ingrese el nombre para el archivo FASTA de proteomas descargados de UniProt concatenados (sin extensión): ").strip() + ".faa")
        summary_file_name = os.path.join(downloader.output_dir, "resumen_concatenacion.txt")
    else:
        output_concat_file_name = None
        summary_file_name = None

    format_headers = input("¿Desea formatear los encabezados de los FASTA de UniProt descargados para Phylomizer? (sí/no): ").strip().lower()
    if format_headers in ["sí", "si"] and output_concat_file_name:
        formatted_fasta_file_name = os.path.join(downloader.output_dir, input("Ingrese el nombre para el archivo FASTA con encabezados formateados (sin extensión): ").strip() + ".faa")
        headers_file_name = os.path.join(downloader.output_dir, "headers_originales_modificados.txt")
    else:
        formatted_fasta_file_name = None
        headers_file_name = None

    downloader.process(
        concatenate=concatenate in ["sí", "si"],
        output_concat_file_name=output_concat_file_name,
        summary_file_name=summary_file_name,
        format_headers=format_headers in ["sí", "si"],
        formatted_fasta_file_name=formatted_fasta_file_name,
        headers_file_name=headers_file_name
    )

if __name__ == "__main__":
    main_uniprot()