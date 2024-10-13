import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import sys
import threading
from io import StringIO
from PIL import Image, ImageTk

# Importa las funciones del módulo principal
from UniProt_batch_downloader import main_uniprot_import
from NCBI_batch_downloader import main_ncbi_importar

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DB Builder")

        # Etiqueta de bienvenida
        self.label = tk.Label(root, text="Bienvenida/o a DBuilder", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Botón para descargar desde UniProt
        self.uniprot_button = tk.Button(root, text="Descargar y procesar proteomas desde UniProt", font=("Arial", 13), command=self.uniprot_options)
        self.uniprot_button.pack(pady=5)

        # Botón para descargar desde NCBI
        self.ncbi_button = tk.Button(root, text="Descargar y procesar proteomas desde NCBI", font=("Arial", 13), command=self.ncbi_options)
        self.ncbi_button.pack(pady=5)

        # Botón para concatenar PROTEOMAS
        self.concatenar_button = tk.Button(root, text="Concatenar proteomas", font=("Arial", 13), command=self.concatenar_options)
        self.concatenar_button.pack(pady=5)
        
        # Botón de ayuda
        self.help_button = tk.Button(root, text="Ayuda", font=("Arial", 13), command=self.show_help)
        self.help_button.pack(pady=5)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Ventana de salida
        self.output_text = tk.Text(root, height=15, width=60)
        self.output_text.pack(pady=10)

        # Redirigir stdout a la ventana de salida
        self.stdout = sys.stdout
        sys.stdout = self

        # Definir la ruta de la imagen
        image_path = os.path.join(os.path.dirname(__file__), "Pieter_Bruegel_the_Elder_-_The_Tower_of_Babel.png")
        
        # Abrir la imagen con Pillow y redimensionarla
        original_image = Image.open(image_path)
        resized_image = original_image.resize((400, 400), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(resized_image)

        # Crear una etiqueta para mostrar la imagen
        self.image_label = tk.Label(root, image=self.image)
        self.image_label.pack(pady=10)

        # Etiqueta para el nombre de la imagen
        self.image_name_label = tk.Label(root, text="The tower of Babel. Pieter Bruegel", font=("Arial", 12, "italic"))
        self.image_name_label.pack(pady=5)

        # Inicializar lista de archivos a concatenar
        self.files_to_concat = []


    def show_help(self):
        # Crear una nueva ventana para la ayuda
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda")
        
        general_instructions = (
            "Para acceder al tutorial completo de cómo usar DBuilder para reconstruir un filoma con la herramienta Phylomizer dirígete a https://github.com/claceline"
        )
        # Instrucciones para el archivo de UniProt
        uniprot_instructions = (
            "El archivo de IDs para UniProt debe ser una rchivo de texto plano y cumplir con el siguiente formato:\n\n"
            "- Cada fila debe contener dos elementos separados por un espacio:\n"
            "  1. ID del organismo\n"
            "  2. ID del proteoma\n\n"
            "Ambos pueden obtenerse de la página web de UniProt: "
            "https://www.uniprot.org/proteomes?query=*\n\n"
            "Ejemplo de archivo para UniProt:\n"
            "9606 UP000005640\n"
            "3702 UP000006548\n"
        )

        # Instrucciones para el archivo de NCBI
        ncbi_instructions = (
            "El archivo de IDs para NCBI debe ser un archivo de texto plano y cumplir con el siguiente formato:\n\n"
            "- Cada fila debe contener el nombre científico del organismo, separado por un espacio:\n"
            "  1. Nombre del género\n"
            "  2. Epiteto específico\n\n"
            "Ejemplo de archivo para NCBI:\n"
            "Homo sapiens\n"
            "Pan troglodytes\n"
        )

        # Crear etiquetas de texto para mostrar las instrucciones
        uniprot_label = tk.Label(help_window, text="Instrucciones generales", font=("Arial", 14, "bold"))
        uniprot_label.pack(pady=5)
        
        uniprot_text = tk.Label(help_window, text=general_instructions, font=("Arial", 12), justify=tk.LEFT)
        uniprot_text.pack(pady=10)
        
        uniprot_label = tk.Label(help_window, text="Archivo de entrada para descargar de UniProt", font=("Arial", 14, "bold"))
        uniprot_label.pack(pady=5)
        
        uniprot_text = tk.Label(help_window, text=uniprot_instructions, font=("Arial", 12), justify=tk.LEFT)
        uniprot_text.pack(pady=10)

        ncbi_label = tk.Label(help_window, text="Archivo de entrada para descargar de NCBI", font=("Arial", 14, "bold"))
        ncbi_label.pack(pady=5)
        
        ncbi_text = tk.Label(help_window, text=ncbi_instructions, font=("Arial", 12), justify=tk.LEFT)
        ncbi_text.pack(pady=10)


    def write(self, message):
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)

    def flush(self):
        pass

    def uniprot_options(self):
        # Primero se abre el diálogo para seleccionar el archivo de IDs
        self.uniprot_ids_path = filedialog.askopenfilename(title="Selecciona el archivo de IDs de UniProt", filetypes=[("Text files", "*.txt")])
        
        # Si no se selecciona un archivo, no se muestra la ventana de opciones
        if not self.uniprot_ids_path:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
            return

        # Si se selecciona un archivo, se abre la ventana de opciones
        uniprot_window = tk.Toplevel(self.root)
        uniprot_window.title("Opciones de UniProt")

        tk.Label(uniprot_window, text="Opciones para UniProt").pack(pady=5)

        self.concat_uniprot_var = tk.BooleanVar()
        tk.Checkbutton(uniprot_window, text="Concatenar archivos FASTA", variable=self.concat_uniprot_var).pack(anchor=tk.W)

        self.formatted_uniprot_var = tk.BooleanVar()
        tk.Checkbutton(uniprot_window, text="Formatear archivos para Phylomizer", variable=self.formatted_uniprot_var).pack(anchor=tk.W)

        # Aquí paso un argumento para cerrar la ventana cuando se ejecute el botón
        tk.Button(uniprot_window, text="Ejecutar", command=lambda: self.execute_uniprot(uniprot_window)).pack(pady=10)

    def execute_uniprot(self, window):
        # Verificar si la carpeta UniProt ya existe
        uniprot_dir = "UniProt"
        
        if os.path.exists(uniprot_dir):
            # Preguntar si el usuario desea sobreescribir la carpeta
            overwrite = messagebox.askyesno("Carpeta existente", f"La carpeta '{uniprot_dir}' ya existe. ¿Deseas sobreescribirla?")
            
            if not overwrite:
                # Si el usuario no desea sobreescribir, se cancela la operación y se vuelve al menú principal
                messagebox.showinfo("Operación cancelada", "El proceso de UniProt fue cancelado.")
                window.destroy()  # Cerrar la ventana de opciones y volver al menú principal
                return
            else:
                # Si el usuario elige sobreescribir, borrar todo el contenido de la carpeta
                shutil.rmtree(uniprot_dir)
                os.makedirs(uniprot_dir)  # Recrear la carpeta vacía
        
        else:
            # Si la carpeta no existe, crearla
            os.makedirs(uniprot_dir)

        # Si el usuario acepta sobreescribir o la carpeta no existe, continuar con el proceso
        if not self.uniprot_ids_path:
            messagebox.showerror("Error", "No se seleccionó ningún archivo de IDs para UniProt.")
            return

        with open(self.uniprot_ids_path, 'r') as file:
            lines = file.readlines()

        organism_ids = [line.split()[0] for line in lines]
        proteome_ids = [line.split()[1] for line in lines]

        concat = "sí" if self.concat_uniprot_var.get() else "no"
        formatted = "sí" if self.formatted_uniprot_var.get() else "no"

        # Reiniciar la barra de progreso y establecer el máximo
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100

        # Ejecutar en un hilo separado
        threading.Thread(target=self.run_uniprot_process, args=(proteome_ids, organism_ids, concat, formatted)).start()

        # Cerrar la ventana de opciones
        window.destroy()




    def run_uniprot_process(self, proteome_ids, organism_ids, concat, formatted):
        try:
            self.progress_bar.step(20)
            main_uniprot_import(proteome_ids, organism_ids, concat, formatted, "concatenated_uniprot", "formatted_uniprot")
            self.progress_bar.step(80)

            messagebox.showinfo("Éxito", "Procesamiento de UniProt completado.")
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error: {e}")
        finally:
            self.progress_bar['value'] = 100

    def ncbi_options(self):
        # Selección de archivo para NCBI primero
        self.ncbi_ids_path = filedialog.askopenfilename(title="Selecciona el archivo con los nombres de especies para NCBI", filetypes=[("Text files", "*.txt")])
        
        # Si no se selecciona un archivo, no se muestra la ventana de opciones
        if not self.ncbi_ids_path:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
            return

        # Si se selecciona un archivo, se abre la ventana de opciones
        ncbi_window = tk.Toplevel(self.root)
        ncbi_window.title("Opciones de NCBI")

        tk.Label(ncbi_window, text="Opciones para NCBI").pack(pady=5)

        self.remove_mitochondrial_var = tk.BooleanVar()
        tk.Checkbutton(ncbi_window, text="Remover proteínas mitocondriales", variable=self.remove_mitochondrial_var).pack(anchor=tk.W)

        self.process_fasta_var = tk.BooleanVar()
        tk.Checkbutton(ncbi_window, text="Conservar solo la secuencia más larga", variable=self.process_fasta_var).pack(anchor=tk.W)

        self.concat_ncbi_var = tk.BooleanVar()
        tk.Checkbutton(ncbi_window, text="Concatenar archivos FASTA", variable=self.concat_ncbi_var).pack(anchor=tk.W)

        tk.Button(ncbi_window, text="Ejecutar", command=lambda: self.execute_ncbi(ncbi_window)).pack(pady=10)

    def execute_ncbi(self, ncbi_window):
        # Verificar si la carpeta NCBI ya existe
        ncbi_dir = "NCBI"
        
        if os.path.exists(ncbi_dir):
            # Preguntar si el usuario desea sobreescribir la carpeta
            overwrite = messagebox.askyesno("Carpeta existente", f"La carpeta '{ncbi_dir}' ya existe. ¿Deseas sobreescribirla?")
            
            if not overwrite:
                # Si el usuario no desea sobreescribir, se cancela la operación y se vuelve al menú principal
                messagebox.showinfo("Operación cancelada", "El proceso de NCBI fue cancelado.")
                ncbi_window.destroy()  # Cerrar la ventana de opciones y volver al menú principal
                return
            else:
                # Si el usuario elige sobreescribir, borrar todo el contenido de la carpeta
                shutil.rmtree(ncbi_dir)
                os.makedirs(ncbi_dir)  # Recrear la carpeta vacía
        else:
            # Si la carpeta no existe, crearla
            os.makedirs(ncbi_dir)

        # Continuar con el procesamiento si la carpeta está lista
        if not self.ncbi_ids_path:
            messagebox.showerror("Error", "No se seleccionó ningún archivo de species_names.")
            return

        with open(self.ncbi_ids_path, 'r') as file:
            lines = file.readlines()

        species_names = [line.strip() for line in lines]

        remove_mitochondrial = self.remove_mitochondrial_var.get()
        process_fasta = self.process_fasta_var.get()
        concatenate = self.concat_ncbi_var.get()

        # Reiniciar la barra de progreso y establecer el máximo
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100

        # Ejecutar en un hilo separado
        threading.Thread(target=self.run_ncbi_process, args=(self.ncbi_ids_path, remove_mitochondrial, process_fasta, concatenate)).start()

        # Cerrar la ventana de opciones después de ejecutar
        ncbi_window.destroy()



    def run_ncbi_process(self, ncbi_ids_path, remove_mitochondrial, process_fasta, concatenate):
        try:
            self.progress_bar.step(20)
            main_ncbi_importar(ncbi_ids_path, remove_mitochondrial, process_fasta, concatenate, "concatenated_NCBI")
            self.progress_bar.step(80)

            messagebox.showinfo("Éxito", "Procesamiento de NCBI completado.")
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error: {e}")
        finally:
            self.progress_bar['value'] = 100

    def execute_concatenation(self):
        if not self.files_to_concat:
            messagebox.showwarning("Advertencia", "No se han seleccionado archivos para concatenar.")
            return

        output_file = f"{self.concat_output_name.get()}.fasta"
        count_file = f"{self.concat_output_name.get()}_resumen_concat.txt"
        
        try:
            with open(output_file, 'w') as outfile, open(count_file, 'w') as countfile:
                for fasta_file in self.files_to_concat:
                    with open(fasta_file, 'r') as infile:
                        # Contar proteínas en el archivo actual
                        protein_count = sum(1 for line in infile if line.startswith('>'))
                        infile.seek(0)  # Reiniciar el archivo para la lectura de concatenación
                        outfile.write(infile.read())  # Concatenar el contenido del archivo

                        # Escribir el nombre del archivo y el conteo en el archivo de conteo
                        countfile.write(f"{fasta_file}: {protein_count} proteínas\n")
            
            messagebox.showinfo("Éxito", f"Archivos concatenados en: {output_file}\nConteo guardado en: {count_file}")
            self.files_to_concat.clear()
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error: {e}")


    def concatenar_options(self):
        concat_window = tk.Toplevel(self.root)
        concat_window.title("Concatenar archivos FASTA")

        self.concat_output_name = tk.StringVar()

        tk.Label(concat_window, text="Nombre para el archivo concatenado:").pack(pady=5)
        output_name_entry = tk.Entry(concat_window, textvariable=self.concat_output_name)
        output_name_entry.pack(pady=5)

        tk.Button(concat_window, text="Seleccionar archivos FASTA", command=self.select_fasta_files).pack(pady=5)
        tk.Button(concat_window, text="Concatenar archivos", command=self.execute_concatenation).pack(pady=10)

        # Mostrar archivos seleccionados
        self.selected_files_label = tk.Label(concat_window, text="", justify=tk.LEFT)
        self.selected_files_label.pack(pady=5)

    def select_fasta_files(self):
        files = filedialog.askopenfilenames(title="Seleccionar archivos FASTA", filetypes=[("Todos los archivos", "*.*")])
        if files:
            self.files_to_concat.extend(files)
            # Mostrar los archivos seleccionados
            self.selected_files_label.config(text="\n".join(self.files_to_concat))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
