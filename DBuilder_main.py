from UniProt_batch_downloader import main_uniprot_import
from NCBI_batch_downloader import main_ncbi_importar
from DBuilder_GUI import App
import argparse
import os
import shutil

"""
DB_Builder.py

Este código gestiona la descarga de proteomas desde
UniProt y NCBI, seguido de su opcional procesamiento para Phylomizer.

Autor: Campos Clara
Consultas y/o sugerencias al mail: clarahabas@gmail.com
Fecha de creación: 2024-08-21
Versión: 1.0

"""

current_dir = os.path.dirname(os.path.abspath(__file__))
ids_path = os.path.join(current_dir, 'organism_proteome_ids.txt')
ids_path_2 = os.path.join(current_dir, 'species_name.txt')

def help_and_info():
    mensaje_ayuda = """ 
    Hola, bienvenida/o. \n Todos los argumentos necesarios para los métodos de los módulos importados son gestionados mediante el manejo directo de entradas pedidas al usuario, por lo que no debes preocuparte. \n
    La ejecución del script principal requiere dos archivos: 
    un archivo nombrado como "organism_proteome_ids.txt" que contenga filas con los pares [organism_id proteome_id] de los proteomas que desees descargar de UniProt.
    un archivo nombrado como “species_name.txt” que contenga una lista con el nombre científico de las especies cuyos proteomas desees descargar de NCBI. \n
    Se ejecuta con el siguiente comando: python3 DBuilder_main.py. Si se agrega el parámetro --GUI al comando se lanza la interfaz gráfica. \n """
    mensaje_bienvenida = "Bienvenida/o"
    print(mensaje_bienvenida)
    while True:
        ayuda = input("¿Desea acceder a la ayuda antes de proceder? (sí/no): ").strip().lower()
        if ayuda in ["sí", "si"]: 
            print(mensaje_ayuda)
            break
        elif ayuda in ["no"]:
            print("Adelante entonces.")
            break
        else:
            print("Opción inválida. Por favor responda 'sí' o 'no'.")


class ManejoArchivos:
    def __init__(self, base_dir):
        """Inicializa la clase con un directorio base.

        :param base_dir: Ruta base donde se manejarán los archivos.
        """
        self.base_dir = base_dir

    def create_output_dir(self, dir_name):
        """Crea un directorio de salida en la ruta base especificada.

        :param dir_name: Nombre del directorio que se creará.
        :return: Ruta del directorio creado.
        """
        output_dir = os.path.join(self.base_dir, dir_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directorio creado: {output_dir}")
        else:
            print(f"El directorio {output_dir} ya existe.")
        return output_dir

    def move_files(self, source_dir, dest_dir, file_extension):
        """Mueve archivos con una extensión dada desde el directorio de origen al de destino.

        :param source_dir: Directorio de origen donde están los archivos.
        :param dest_dir: Directorio de destino donde se moverán los archivos.
        :param file_extension: Extensión de los archivos a mover (ej. '.faa').
        """
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            print(f"Directorio creado: {dest_dir}")

        for filename in os.listdir(source_dir):
            if filename.endswith(file_extension):
                src_file = os.path.join(source_dir, filename)
                dest_file = os.path.join(dest_dir, filename)
                shutil.move(src_file, dest_file)
                print(f"Movido: {src_file} a {dest_file}")

def read_ids_from_file(file_path):
    """
    Lee un archivo .txt que contiene organism_id y proteome_id, y retorna dos listas con los IDs correspondientes.
    El archivo debe llamarse "organism_proteome_ids.txt". Cada fila es un par [organism_id proteome_id] separados por espacio.

    :param file_path: Ruta al archivo .txt que contiene los IDs.
    :return: Dos listas, una con los organism_ids y otra con los proteome_ids.
    """
    organism_ids = []
    proteome_ids = []

    with open(file_path, 'r') as file:
        for line in file:
            if not line.strip():
                continue  # Ignora líneas vacías
            line = ' '.join(line.split())  # Elimina espacios múltiples
            if '\t' in line:
                parts = line.split('\t')  # Divide por tabuladores
            else:
                parts = line.split()  # Divide por espacios

            if len(parts) == 2:
                organism_id, proteome_id = parts
                organism_ids.append(organism_id.strip())  # Agrega el ID del organismo
                proteome_ids.append(proteome_id.strip())  # Agrega el ID del proteoma
            else:
                print(f"Advertencia: Línea ignorada por formato incorrecto: {line}")

    return organism_ids, proteome_ids

def main():
    """Función principal que ejecuta el proceso de descarga y manejo de archivos de proteomas."""
    parser = argparse.ArgumentParser(description="Script principal para descargar y procesar proteomas.")
    parser.add_argument("--GUI", action="store_true", help="Lanzar la interfaz gráfica.")
    
    
    args = parser.parse_args()

    # Si se pasa el argumento --GUI, ejecuta la interfaz gráfica
    if args.GUI:
        import tkinter as tk  
        root = tk.Tk()
        app = App(root)  
        root.mainloop()  
        return  
    # Inicializar manejo de archivos
    manejo = ManejoArchivos(current_dir)

    # Leer los IDs desde archivos de texto
    organism_ids, proteome_ids = read_ids_from_file(ids_path)

    # Variables inicializadas en caso de que el usuario elija no descargar desde UniProt o NCBI
    concatenate_option_uniprot = None
    formatted_option_uniprot = None
    output_concat_file_name_uniprot = "concatenated_uniprot"
    output_formatted_file_name_uniprot = "formatted_uniprot"
    
    remove_mitochondrial = None
    process_fasta_option = None
    concatenate_option = None
    concatenated_filename = None
    
    help_and_info()
    
    # Solicitar inputs al usuario
    while True:
        elegir_uniprot = input("¿Deseas descargar y procesar proteomas desde UniProt? (sí/no): ").lower()
        if elegir_uniprot in ["sí", "si", "no"]:
            break
        else:
            print("Opción no válida. Por favor, responde 'sí' o 'no'.")

    if elegir_uniprot in ["sí", "si"]:
        concatenate_option_uniprot = input("¿Desea concatenar todos los archivos FASTA descargados de UniProt en un único archivo? (sí/no): ").strip().lower()
        if concatenate_option_uniprot in ["sí", "si"]:
            output_concat_file_name_uniprot = input("Ingrese el nombre para el archivo FASTA concatenado de UniProt (sin extensión): ").strip()
            if not output_concat_file_name_uniprot:
                output_concat_file_name_uniprot = "concatenated_uniprot"

        formatted_option_uniprot = input("¿Desea formatear los encabezados de las proteínas de UniProt para Phylomizer? (sí/no): ").strip().lower()
        if formatted_option_uniprot in ["sí", "si"]:
            output_formatted_file_name_uniprot = input("Ingrese el nombre para el archivo FASTA de proteomas concatenados formateado para Phylomizer (sin extensión): ").strip()
            if not output_formatted_file_name_uniprot: 
                output_formatted_file_name_uniprot = "formatted_uniprot"

    while True:
        elegir_ncbi = input("¿Deseas descargar y procesar proteomas desde NCBI? (sí/no): ").lower().strip()
        if elegir_ncbi in ["sí", "si", "no"]:
            break
        else:
            print("Opción no válida. Por favor, responde 'sí' o 'no'.")

    if elegir_ncbi in ["sí", "si"]:
        remove_mitochondrial = input("¿Remover proteínas de genoma mitocondrial de los proteomas descargados de NCBI? (sí/no): ").strip().lower() in ["sí", "si"]
        process_fasta_option = input("¿Procesar archivos FASTA de proteomas descargados de NCBI para conservar solo la secuencia más larga? (sí/no): ").strip().lower() in ["sí", "si"]
        concatenate_option = input("¿Concatenar en un único archivo FASTA todos los proteomas de NCBI descargados y procesados? (sí/no): ").strip().lower() in ["sí", "si"]

        if concatenate_option:
            concatenated_filename = input("Ingrese el nombre para el archivo FASTA concatenado de NCBI: ").strip()
            if not concatenated_filename:
                concatenated_filename = "concatenated_NCBI"

        else:
            print("probando")
            concatenated_filename = "concatenated_NCBI"  # Valor por defecto si no se selecciona concatenar


    # Ejecutar descarga y procesamiento de UniProt
    if elegir_uniprot in ["sí", "si"]:
        if len(proteome_ids) != len(organism_ids):
            raise ValueError("El número de IDs de proteomas y de organismos para descargar de UniProt debe ser igual.")
        main_uniprot_import(proteome_ids, organism_ids, concatenate_option_uniprot, formatted_option_uniprot, output_concat_file_name_uniprot, output_formatted_file_name_uniprot)
    else:
        print("No se descargarán proteomas de UniProt.")

    # Ejecutar descarga y procesamiento de NCBI
    if elegir_ncbi in ["sí", "si"]:
       main_ncbi_importar(ncbi_ids_path=ids_path_2, remove_mitochondrial=remove_mitochondrial, process_fasta_option=process_fasta_option, concatenate_option=concatenate_option, concatenated_filename=concatenated_filename)

    else:
        if elegir_uniprot == "no":
            print("No se descargarán proteomas de NCBI. No hay nada más que hacer. Saliendo del programa.")
    print(f"Valor de elegir_ncbi: {elegir_ncbi}")

if __name__ == "__main__":
    main()
