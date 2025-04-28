import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.messagebox as messagebox
import datetime
import hashlib
import json
import shutil
import os
from PIL import Image, ImageTk
import tkinter.simpledialog as simpledialog
import win32print
import win32ui
import csv
from tkinter import filedialog, messagebox
from tkcalendar import Calendar
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors,units
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image as PImage  
import io
from fpdf import FPDF
from reportlab.lib.colors import HexColor 



inventario = {}
usuarios = {"admin": hashlib.sha256("admin".encode()).hexdigest()}  # Usuario administrador predeterminado
clave_admin = hashlib.sha256("NEVA".encode()).hexdigest()
salidas_departamentos = []
entradas_departamentos=[]
salidas_espera=[]

#funciones de inicio de sesion




def guardar_datos():
    """Guarda los datos en un archivo JSON."""
    datos = {
        "inventario": {
            producto: {
                **datos,
                "fecha_entrada": datos["fecha_entrada"].isoformat() if isinstance(datos["fecha_entrada"], datetime.date) else None if datos["fecha_entrada"] is None or datos["fecha_entrada"] == "null" else str(datos["fecha_entrada"]),
                "fecha_salida": datos["fecha_salida"].isoformat() if isinstance(datos["fecha_salida"], datetime.date) else None if datos["fecha_salida"] is None or datos["fecha_salida"] == "null" else str(datos["fecha_salida"])
            }
            for producto, datos in inventario.items()
        },
        "usuarios": usuarios,
        "salidas_departamentos": salidas_departamentos
    }
    try:
        with open("inventario.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
        messagebox.showinfo("Guardado", "Datos guardados correctamente.")
    except IOError as e:
        messagebox.showerror("Error", f"Error de entrada/salida: {e}")
    except TypeError as e:
        messagebox.showerror("Error", f"Error de tipo de datos: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")

def cargar_datos():
    """Carga los datos desde un archivo JSON."""
    global inventario, usuarios, salidas_departamentos
    try:
        with open("inventario.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            inventario = {}
            for producto, datos_producto in datos["inventario"].items():
                fecha_entrada = datos_producto.get("fecha_entrada")
                fecha_salida = datos_producto.get("fecha_salida")

                # Manejar los valores "null"
                if fecha_entrada == "null" or fecha_entrada is None:
                    fecha_entrada = None
                else:
                    try:
                        fecha_entrada = datetime.date.fromisoformat(fecha_entrada)
                    except ValueError:
                        fecha_entrada = fecha_entrada # Mantener la cadena original si no es un formato ISO válido

                if fecha_salida == "null" or fecha_salida is None:
                    fecha_salida = None
                else:
                    try:
                        fecha_salida = datetime.date.fromisoformat(fecha_salida)
                    except ValueError:
                        fecha_salida = fecha_salida # Mantener la cadena original si no es un formato ISO válido

                inventario[producto] = {
                    **datos_producto,
                    "fecha_entrada": fecha_entrada,
                    "fecha_salida": fecha_salida
                }
            usuarios = datos.get("usuarios", [])
            salidas_departamentos = datos.get("salidas_departamentos", [])
    except FileNotFoundError:
        messagebox.showinfo("Cargar Datos", "No se encontró el archivo inventario.json. Se creará uno nuevo.")
        inventario = {}
        usuarios = []
        salidas_departamentos = []
    except json.JSONDecodeError:
        messagebox.showerror("Error", "No se pudieron cargar los datos: El archivo JSON está corrupto.")
        inventario = {}
        usuarios = []
        salidas_departamentos = []
    except ValueError as e:
        messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
        inventario = {}
        usuarios = []
        salidas_departamentos = []
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado al cargar los datos: {e}")



def iniciar_sesion():
    """Permite al usuario iniciar sesión."""
    global ventana_login  # Declarar como global para poder cerrarla

    def iniciar():
        nombre_usuario = entry_nombre.get()
        contrasena = entry_contrasena.get()
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        es_admin = var_admin.get()  # Obtener el valor de la casilla de verificación

        if nombre_usuario in usuarios and usuarios[nombre_usuario] == contrasena_hash:
            if es_admin:
                ventana_clave = tk.Toplevel(ventana_login)
                ventana_clave.title("Clave de Administrador")
                ventana_clave.configure(bg="#263238") # Fondo oscuro

                # --- Estilos ttk Personalizados ---
                style_clave = ttk.Style(ventana_clave)
                style_clave.theme_use('clam')
                style_clave.configure("TLabel", foreground="#eceff1", background="#263238", font=("Arial", 14))
                style_clave.configure("TEntry", fieldbackground="#f0f0f0", foreground="black", font=("Arial", 14))
                style_clave.configure("TButton", foreground="#eceff1", background="#37474F", font=("Arial", 14, "bold"))
                style_clave.configure("TCheckbutton", foreground="#eceff1", background="#263238", font=("Arial", 14))

                ttk.Label(ventana_clave, text="Clave:", background="#263238", foreground="#eceff1", font=("Arial", 14)).pack(pady=5)
                entry_clave = ttk.Entry(ventana_clave, show="*", font=("Arial", 14), width=20)
                entry_clave.pack(pady=5)

                def verificar_clave():
                    clave_ingresada = hashlib.sha256(entry_clave.get().encode()).hexdigest()
                    if clave_ingresada == clave_admin:
                        messagebox.showinfo("Acceso Permitido", "Acceso de administrador concedido.")
                        mostrar_menu()
                        ventana_clave.destroy()
                        ventana_login.destroy()
                    else:
                        messagebox.showerror("Acceso Denegado", "Clave incorrecta.")

                ttk.Button(ventana_clave, text="Verificar", command=verificar_clave, style="TButton").pack(pady=10)
            else:
                messagebox.showinfo("Acceso Denegado", "No tienes privilegios de administrador.")
                ventana_login.destroy()
        else:
            messagebox.showerror("Error", "Nombre de usuario o contraseña incorrectos.")

    ventana_login = tk.Tk()
    ventana_login.title("Login")
    ventana_login.configure(bg="#263238")  # Fondo oscuro

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_login)
    style.theme_use('clam')
    style.configure("TLabel", foreground="#eceff1", background="#263238", font=("Arial", 14))
    style.configure("TEntry", fieldbackground="#f0f0f0", foreground="black", font=("Arial", 14))
    style.configure("TButton", foreground="#eceff1", background="#37474F", font=("Arial", 14, "bold"))
    style.configure("TCheckbutton", foreground="#eceff1", background="#263238", font=("Arial", 14))

    # Marco principal para el contenido
    frame_contenido = tk.Frame(ventana_login, bg="#263238")
    frame_contenido.pack(padx=20, pady=20, fill="both", expand=True)

    # Marco para el logo (a la izquierda)
    frame_logo = tk.Frame(frame_contenido, bg="#263238")
    frame_logo.pack(side="left", padx=20, pady=20, fill="both", expand=True)  # Hacer que el marco se expanda

    # Cargar el logo y redimensionarlo
    try:
        imagen_logo = Image.open("C:/Users/monster/Desktop/src/server/routes/imagenes/logo.png")
        imagen_logo = imagen_logo.resize((300, 300))
        logo = ImageTk.PhotoImage(imagen_logo)
        label_logo = tk.Label(frame_logo, image=logo, bg="#263238")
        label_logo.image = logo
        label_logo.pack(fill="both", expand=True)  # Hacer que el logo se expanda
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el archivo del logo.")

    # Marco para los campos de entrada (a la derecha)
    frame_campos = tk.Frame(frame_contenido, bg="#263238")
    frame_campos.pack(side="right", padx=20, pady=20, fill="both", expand=True)  # Hacer que el marco se expanda

    # Configurar la cuadrícula para que se expanda
    frame_campos.grid_columnconfigure(1, weight=1)  # Hacer que la columna 1 se expanda
    frame_campos.grid_rowconfigure(0, weight=1)  # Hacer que las filas se expandan
    frame_campos.grid_rowconfigure(1, weight=1)
    frame_campos.grid_rowconfigure(2, weight=1)
    frame_campos.grid_rowconfigure(3, weight=1)  # Agregar fila para la casilla de verificación

    # Centrar los campos de entrada
    ttk.Label(frame_campos, text="Usuario:", background="#263238", foreground="#eceff1").grid(row=0, column=0, pady=5, sticky="e")
    entry_nombre = ttk.Entry(frame_campos, width=30)  # Aumentar el ancho del campo de entrada
    entry_nombre.grid(row=0, column=1, pady=5, sticky="ew")  # sticky="ew" para expandir horizontalmente

    ttk.Label(frame_campos, text="Contraseña:", background="#263238", foreground="#eceff1").grid(row=1, column=0, pady=5, sticky="e")
    entry_contrasena = ttk.Entry(frame_campos, show="*", width=30)  # Aumentar el ancho del campo de entrada
    entry_contrasena.grid(row=1, column=1, pady=5, sticky="ew")  # sticky="ew" para expandir horizontalmente

    var_admin = tk.IntVar()  # Variable para la casilla de verificación
    check_admin = ttk.Checkbutton(frame_campos, text="Administrador", variable=var_admin)
    check_admin.grid(row=2, column=0, columnspan=2, pady=5, sticky="w") # sticky="w" para alinear a la izquierda

    ttk.Button(frame_campos, text="Iniciar Sesión", command=iniciar, style="TButton").grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")  # sticky="ew" para expandir horizontalmente

    ventana_login.mainloop()
                            #Hasta aqui funciones de inicio de sesion




def abrir_calendario(ventana_padre, entry_fecha):
    """Abre una ventana con un calendario y actualiza el campo de fecha."""
    def seleccionar_fecha():
        fecha = cal.get_date()
        entry_fecha.delete(0, tk.END)
        entry_fecha.insert(0, fecha)
        ventana_calendario.destroy()

    ventana_calendario = tk.Toplevel(ventana_padre)
    ventana_calendario.title("Seleccionar Fecha")
    cal = Calendar(ventana_calendario, selectmode="day", date_pattern="yyyy-mm-dd")
    cal.pack(padx=10, pady=10)
    ttk.Button(ventana_calendario, text="Seleccionar", command=seleccionar_fecha).pack(pady=5)
















    
    
                                            #funciones principales:
       
def agregar_producto():
    """Agrega un producto al inventario con fecha de entrada manual."""
    
    def agregar():
        producto = entry_producto.get()
        categoria = combo_categoria.get()  # Obtener la categoría seleccionada del Combobox
        destino_entrada = entry_destino_entrada.get()
        entrada = int(entry_entrada.get())
        unidad_medida = combo_unidad_medida.get() #Obtener Unidad de Medida del combo box
        fecha_str = entry_fecha_entrada.get()
        fecha_entrada = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
        fecha_salida = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()

        salida = 0
        inventario[producto] = {
            "categoria": categoria,
            "destino_entrada": destino_entrada,
            "entrada": entrada,
            "salida": salida,
            "stock": entrada - salida,
            "unidad_medida": unidad_medida,
            "fecha_entrada": fecha_entrada,
            "fecha_salida": "None",
            "destino_salida": ""
        }
        messagebox.showinfo("Producto Agregado", f"Producto '{producto}' agregado al inventario. Fecha de entrada: {fecha_entrada}")
        ventana_agregar.destroy()

        # Registrar la entrada en el historial
        entradas_departamentos.append({
            "producto": producto,
            "cantidad": entrada,
            "fecha": fecha_entrada,
            "destino": destino_entrada
        })
        
    

    ventana_agregar = tk.Toplevel(ventana)
    ventana_agregar.title("Agregar Producto")
    ventana_agregar.configure(bg="#000080")

    # Obtener las categorías existentes del inventario
    categorias = list(set(producto["categoria"] for producto in inventario.values()))
    categorias.append("Añadir nueva")  # Agregar la opción "Añadir nueva"

    #Obtener Unidades de medida existentes
    unidades_medida = list(set(producto["unidad_medida"] for producto in inventario.values()))
    unidades_medida.append("Añadir nueva")


    def abrir_calendario():
        """Abre un calendario para seleccionar la fecha."""
        def seleccionar_fecha():
            fecha_seleccionada = cal.get_date()
            entry_fecha_entrada.delete(0, tk.END)
            entry_fecha_entrada.insert(0, fecha_seleccionada)
            ventana_calendario.destroy()

        ventana_calendario = tk.Toplevel(ventana_agregar)
        ventana_calendario.title("Seleccionar Fecha")
        cal = Calendar(ventana_calendario, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10)
        tk.Button(ventana_calendario, text="Seleccionar", command=seleccionar_fecha).pack(pady=5)

    

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_agregar)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",  # Etiquetas blancas y gruesas con fondo azul
                    foreground="#ffffff",
                    background="#000080",
                    font=("Segoe UI", 10, "bold"))

    style.configure("CustomEntry.TEntry",  # Campos de entrada blancos con texto negro grueso
                    foreground="#000000",
                    background="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10, "bold"))

    style.configure("TCombobox",  # Combobox blanco con texto negro grueso
                    foreground="#000000",
                    background="#ffffff",
                    fieldbackground="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10, "bold"))

    style.configure("CustomButton.TButton",  # Estilo para los botones (manteniendo el color)
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"),
                    padding=8,
                    relief="raised",
                    anchor="center")
    style.map("CustomButton.TButton",
              background=[('active', '#c1c1c1')],
              foreground=[('active', '#000000')])

    # --- Etiquetas y Campos de Entrada ---
    ttk.Label(ventana_agregar, text="Nombre del producto:", style="CustomLabel.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    entry_producto = ttk.Entry(ventana_agregar, style="CustomEntry.TEntry")
    entry_producto.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    ttk.Label(ventana_agregar, text="Categoría del producto:", style="CustomLabel.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=10)
    combo_categoria = ttk.Combobox(ventana_agregar, values=list(set(producto["categoria"] for producto in inventario.values())) + ["Añadir nueva"], style="TCombobox")
    combo_categoria.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    ttk.Label(ventana_agregar, text="Destino de entrada:", style="CustomLabel.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=10)
    entry_destino_entrada = ttk.Entry(ventana_agregar, style="CustomEntry.TEntry")
    entry_destino_entrada.insert(0, "Almacén principal")
    entry_destino_entrada.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    ttk.Label(ventana_agregar, text="Cantidad de entrada:", style="CustomLabel.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=10)
    entry_entrada = ttk.Entry(ventana_agregar, style="CustomEntry.TEntry")
    entry_entrada.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

    ttk.Label(ventana_agregar, text="Unidad de medida:", style="CustomLabel.TLabel").grid(row=4, column=0, sticky="w", padx=10, pady=10)
    combo_unidad_medida = ttk.Combobox(ventana_agregar, values=list(set(producto["unidad_medida"] for producto in inventario.values())) + ["Añadir nueva"], style="TCombobox")
    combo_unidad_medida.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

    ttk.Label(ventana_agregar, text="Fecha de entrada (YYYY-MM-DD):", style="CustomLabel.TLabel").grid(row=5, column=0, sticky="w", padx=10, pady=10)
    entry_fecha_entrada = ttk.Entry(ventana_agregar, style="CustomEntry.TEntry")
    entry_fecha_entrada.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

    ttk.Button(ventana_agregar, text="Calendario", command=abrir_calendario, style="CustomButton.TButton").grid(row=5, column=2, padx=10, pady=10)
    ttk.Button(ventana_agregar, text="Agregar", command=agregar, style="CustomButton.TButton").grid(row=6, column=0, columnspan=3, pady=15, padx=10, sticky="ew")

    # --- Configurar la expansión de la columna ---
    ventana_agregar.grid_columnconfigure(1, weight=1)

def realizar_salida():
    """Realiza una salida en espera de productos del inventario."""
    
    def salida_espera():
        """Agrega una salida a la lista de espera."""
        departamento = departamento_var.get()
        producto = combo_producto.get()
        cantidad = int(entry_cantidad.get())

        salidas_espera.append({
            "producto": producto,
            "cantidad": cantidad,
            "departamento": departamento
        })

        messagebox.showinfo("Salida en Espera", f"{cantidad} unidades de '{producto}' solicitadas para {departamento}. Agregado a la lista de espera.")
        ventana_salida_espera.destroy()

    ventana_salida_espera = tk.Toplevel(ventana)
    ventana_salida_espera.title("Salida en Espera")
    ventana_salida_espera.configure(bg="#000080")

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_salida_espera)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#000080",
                    font=("Segoe UI", 10, "bold"))

    style.configure("TCombobox",
                    foreground="#000000",
                    background="#ffffff",
                    fieldbackground="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10))

    style.configure("CustomEntry.TEntry",
                    foreground="#000000",
                    background="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10))

    style.configure("CustomButton.TButton",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"),
                    padding=8,
                    relief="raised",
                    anchor="center")
    style.map("CustomButton.TButton",
              background=[('active', '#c1c1c1')],
              foreground=[('active', '#000000')])

    # Obtener la lista de productos del inventario
    productos = sorted(list(inventario.keys()))

    ttk.Label(ventana_salida_espera, text="Nombre del producto:", style="CustomLabel.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    combo_producto = ttk.Combobox(ventana_salida_espera, values=productos, style="TCombobox")
    combo_producto.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    # Función para filtrar la lista de productos a medida que el usuario escribe
    def filtrar_productos(event):
        valor_escrito = combo_producto.get().lower()
        productos_filtrados = [
            producto
            for producto in productos
            if any(palabra.startswith(valor_escrito) for palabra in producto.lower().split())
        ]
        combo_producto["values"] = productos_filtrados

    # Enlazar el evento de escritura al Combobox
    combo_producto.bind("<KeyRelease>", filtrar_productos)

    ttk.Label(ventana_salida_espera, text="Cantidad de salida:", style="CustomLabel.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=10)
    entry_cantidad = ttk.Entry(ventana_salida_espera, style="CustomEntry.TEntry")
    entry_cantidad.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    # Menú desplegable para seleccionar el departamento
    ttk.Label(ventana_salida_espera, text="Departamento:", style="CustomLabel.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=10)
    departamentos = ["OTIC", "Oficina de Gestion Administrativa", "Oficina Contabilidad","Oficina Compras","Oficina de Bienes","Direccion de Servicios Generales y Transporte","Oficina de Seguimiento y Proyectos Estructurales","Direccion General de Planificacion Estrategica","Planoteca","Biblioteca","Direccion General de Seguimiento de Proyectos","Gestion Participativa Parque la isla","Oficina de Atencion ciudadana","Oficina de gestion Humana","Presidencia","Secretaria General","Consultoria Juridica","Oficina de Planificacion y Presupuesto","Auditoria","Direccion de informacion y Comunicacion","Direccion General de Formacion"]  # Reemplaza con tus departamentos
    departamentos.sort()
    departamento_var = tk.StringVar(ventana_salida_espera)
    departamento_var.set(departamentos[0])  # Valor predeterminado
    ttk.Combobox(ventana_salida_espera, textvariable=departamento_var, values=departamentos, style="TCombobox").grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    ttk.Button(ventana_salida_espera, text="Agregar a Salida en Espera", command=salida_espera, style="CustomButton.TButton").grid(row=3, column=0, columnspan=2, pady=15, padx=10, sticky="ew")

    ventana_salida_espera.grid_columnconfigure(1, weight=1)


   


def mostrar_inventario():
    """Muestra el inventario con menú desplegable de categorías y búsqueda por abreviatura, y totales."""
   
    ventana_inventario = tk.Toplevel(ventana)
    ventana_inventario.title("Inventario")
    ventana_inventario.geometry("1200x600")
    ventana_inventario.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_inventario)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#A9A9A9",
                    font=("Segoe UI", 10, "bold"))

    style.configure("TCombobox",
                    foreground="#000000",
                    background="#ffffff",
                    fieldbackground="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10))

    style.configure("CustomEntry.TEntry",
                    foreground="#000000",
                    background="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10))

    style.configure("CustomButton.TButton",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"),
                    padding=8,
                    relief="raised",
                    anchor="center")
    style.map("CustomButton.TButton",
              background=[('active', '#c1c1c1')],
              foreground=[('active', '#000000')])

    style.configure("Grid.Treeview",
                    foreground="#000000",
                    background="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview",
              background=[('selected', '#bddfff')],
              foreground=[('selected', '#000000')])

    # Frame para los menús desplegables, totales y búsqueda
    frame_menu = tk.Frame(ventana_inventario, bg="#A9A9A9")
    frame_menu.pack(pady=10, padx=10, fill=tk.X)

    # Frame para la búsqueda por abreviatura
    frame_busqueda = tk.Frame(frame_menu, bg="#A9A9A9")
    frame_busqueda.pack(side=tk.LEFT, padx=10)

    ttk.Label(frame_busqueda, text="Buscar:", style="CustomLabel.TLabel").pack(side=tk.LEFT)
    entry_busqueda = ttk.Entry(frame_busqueda, style="CustomEntry.TEntry")
    entry_busqueda.pack(side=tk.LEFT)

    # Función para buscar productos por abreviatura
    def buscar_por_abreviatura(event=None):  # Agregamos el argumento event
        termino_busqueda = entry_busqueda.get().lower()
        mostrar_tabla(categoria_seleccionada_mostrar.get(), termino_busqueda)

    entry_busqueda.bind("<KeyRelease>", buscar_por_abreviatura)  # Enlazamos el evento KeyRelease

    # Menú desplegable de categorías para mostrar
    categorias_mostrar = ["Todas"] + sorted(set(datos["categoria"] for datos in inventario.values()))
    categoria_seleccionada_mostrar = tk.StringVar(frame_menu)
    categoria_seleccionada_mostrar.set(categorias_mostrar[0])

    menu_categorias_mostrar = ttk.Combobox(frame_menu, textvariable=categoria_seleccionada_mostrar, values=categorias_mostrar, style="TCombobox")
    menu_categorias_mostrar.pack(side=tk.LEFT, padx=10)

    # Función para mostrar el inventario según la categoría seleccionada
    def mostrar_por_categoria():
        categoria = categoria_seleccionada_mostrar.get()
        mostrar_tabla(categoria)

    boton_mostrar = ttk.Button(frame_menu, text="Mostrar", command=mostrar_por_categoria, style="CustomButton.TButton")
    boton_mostrar.pack(side=tk.LEFT, padx=10)

    # Frame para la tabla de inventario
    frame_tabla = tk.Frame(ventana_inventario, bg="#A9A9A9")
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Treeview (tabla)
    tabla_productos = ttk.Treeview(frame_tabla, columns=("Categoría", "Producto", "Destino Entrada", "Destino Salida", "Entrada", "Salida", "Stock", "Unidad Medida", "Fecha Entrada", "Fecha Salida"), show="headings", style="Grid.Treeview")
    tabla_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Definir encabezados de columna
    tabla_productos.heading("Categoría", text="Categoría", anchor=tk.W)
    tabla_productos.heading("Producto", text="Producto", anchor=tk.W)
    tabla_productos.heading("Destino Entrada", text="Destino Entrada", anchor=tk.W)
    tabla_productos.heading("Destino Salida", text="Destino Salida", anchor=tk.W)
    tabla_productos.heading("Entrada", text="Entrada", anchor=tk.E)
    tabla_productos.heading("Salida", text="Salida", anchor=tk.E)
    tabla_productos.heading("Stock", text="Stock", anchor=tk.E)
    tabla_productos.heading("Unidad Medida", text="Unidad Medida", anchor=tk.W)
    tabla_productos.heading("Fecha Entrada", text="Fecha Entrada", anchor=tk.W)
    tabla_productos.heading("Fecha Salida", text="Fecha Salida", anchor=tk.W)

    # Configurar ancho de columnas
    tabla_productos.column("Categoría", width=120)
    tabla_productos.column("Producto", width=150)
    tabla_productos.column("Destino Entrada", width=150)
    tabla_productos.column("Destino Salida", width=150)
    tabla_productos.column("Entrada", width=80)
    tabla_productos.column("Salida", width=80)
    tabla_productos.column("Stock", width=80)
    tabla_productos.column("Unidad Medida", width=120)
    tabla_productos.column("Fecha Entrada", width=100)
    tabla_productos.column("Fecha Salida", width=100)

    # Agregar barra de desplazamiento vertical
    barra_desplazamiento = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_productos.yview)
    tabla_productos.configure(yscrollcommand=barra_desplazamiento.set)
    barra_desplazamiento.pack(side=tk.RIGHT, fill=tk.Y)

    # Frame para los totales
    frame_totales = tk.Frame(ventana_inventario, bg="#A9A9A9")
    frame_totales.pack(pady=10, padx=10, fill=tk.X)

    label_totales = ttk.Label(frame_totales, text="", style="CustomLabel.TLabel")
    label_totales.pack()

    # Función para mostrar la tabla con los datos filtrados
    def mostrar_tabla(categoria="Todas", termino_busqueda=""):
        tabla_productos.delete(*tabla_productos.get_children())
        productos_filtrados = obtener_productos_filtrados(categoria, termino_busqueda)
        for producto, datos in productos_filtrados:
            destino_salida = datos["destino_salida"]
            numero_requisicion = datos.get("numero_requisicion", "")  # Leer de la clave numero_requisicion

            if numero_requisicion:
                destino_salida += f" (Req. {numero_requisicion})"  # Agregar el número de requisición al destino de salida

            tabla_productos.insert("", tk.END, values=(
                datos["categoria"],
                producto,
                datos["destino_entrada"],
                destino_salida,  # Mostrar el destino de salida con el número de requisición
                datos["entrada"],
                datos["salida"],
                datos["stock"],
                datos["unidad_medida"],
                datos["fecha_entrada"],
                datos["fecha_salida"]
            ))
        mostrar_totales(categoria)

    # Función para obtener los productos filtrados por categoría y término de búsqueda
    def obtener_productos_filtrados(categoria, termino_busqueda):
        resultados = []
        for producto, datos in inventario.items():
            incluir = True
            if categoria != "Todas" and datos["categoria"] != categoria:
                incluir = False
            if termino_busqueda and not producto.lower().startswith(termino_busqueda):
                incluir = False
            if incluir:
                resultados.append((producto, datos))
        return sorted(resultados, key=lambda x: (x[1]["categoria"], x[0]))

    # Función para mostrar los totales
    def mostrar_totales(categoria):
        if categoria == "Todas":
            total_productos = len(inventario)
            total_categorias = len(set(datos["categoria"] for datos in inventario.values()))
            label_totales.config(text=f"Total de productos: {total_productos}, Total de categorías: {total_categorias}", style="CustomLabel.TLabel")
        else:
            productos_categoria = [datos for datos in inventario.values() if datos["categoria"] == categoria]
            total_productos = len(productos_categoria)
            label_totales.config(text=f"Total de productos en {categoria}: {total_productos}", style="CustomLabel.TLabel")

    # Mostrar todos los productos al inicio
    mostrar_tabla()

    def realizar_entrada_contextual(producto):
        """Realiza una entrada de productos desde el menú contextual con botón de calendario."""
        def confirmar_entrada():
            cantidad = entry_cantidad.get()
            fecha = entry_fecha.get()
            if not cantidad.isdigit():
                messagebox.showerror("Error", "La cantidad debe ser un número.")
                return
            cantidad = int(cantidad)

            if producto in inventario:
                inventario[producto]["stock"] += cantidad
                inventario[producto]["entrada"] += cantidad
                inventario[producto]["fecha_entrada"] = fecha
                entradas_departamentos.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "fecha": fecha,
                    "destino": inventario[producto]["destino_entrada"]
                })
                mostrar_tabla(categoria_seleccionada_mostrar.get())
                messagebox.showinfo("Entrada Realizada", f"{cantidad} unidades de {producto} entraron al inventario.")
                ventana_entrada.destroy()
            else:
                messagebox.showerror("Error", "El producto no existe en el inventario.")

        ventana_entrada = tk.Toplevel(ventana_inventario)
        ventana_entrada.title(f"Realizar Entrada - {producto}")
        ventana_entrada.configure(bg="#A9A9A9")

        ttk.Label(ventana_entrada, text="Cantidad:", style="CustomLabel.TLabel").grid(row=0, column=0, padx=10, pady=10)
        entry_cantidad = ttk.Entry(ventana_entrada, style="CustomEntry.TEntry")
        entry_cantidad.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(ventana_entrada, text="Fecha:", style="CustomLabel.TLabel").grid(row=1, column=0, padx=10, pady=10)
        entry_fecha = ttk.Entry(ventana_entrada, style="CustomEntry.TEntry")
        entry_fecha.grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(ventana_entrada, text="Calendario", command=lambda: abrir_calendario(ventana_entrada, entry_fecha), style="CustomButton.TButton").grid(row=1, column=2, padx=10, pady=10)

        ttk.Button(ventana_entrada, text="Confirmar Entrada", command=confirmar_entrada, style="CustomButton.TButton").grid(row=2, column=0, columnspan=3, pady=15, padx=10, sticky="ew")
        ventana_entrada.grid_columnconfigure(1, weight=1)

    def realizar_salida_contextual(producto):
        """Realiza una salida de productos desde el menú contextual con botón de calendario."""

        def confirmar_salida():
            departamento = departamento_var.get()
            cantidad = entry_cantidad.get()
            fecha = entry_fecha.get()
            numero_requisicion = entry_numero_requisicion.get()

            if not cantidad.isdigit():
                messagebox.showerror("Error", "Cantidad inválida. Ingrese un número entero.")
                return
            cantidad = int(cantidad)

            if not departamento or not fecha or not numero_requisicion:
                messagebox.showerror("Error", "Por favor, complete todos los campos.")
                return

            if producto in inventario and inventario[producto]["stock"] >= cantidad:
                inventario[producto]["stock"] -= cantidad
                inventario[producto]["salida"] += cantidad
                inventario[producto]["fecha_salida"] = fecha
                inventario[producto]["destino_salida"] = departamento
                inventario[producto]["numero_requisicion"] = numero_requisicion
                salidas_departamentos.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "fecha": fecha,
                    "destino": departamento,
                    "requisicion": numero_requisicion
                })
                mostrar_tabla(categoria_seleccionada_mostrar.get())
                messagebox.showinfo("Salida Realizada", f"{cantidad} unidades de {producto} salieron para {departamento}.")
                ventana_salida.destroy()
            else:
                messagebox.showerror("Error", "No hay suficiente stock para realizar la salida.")

        ventana_salida = tk.Toplevel(ventana_inventario)
        ventana_salida.title(f"Realizar Salida - {producto}")
        ventana_salida.configure(bg="#A9A9A9")

        ttk.Label(ventana_salida, text="Departamento:", style="CustomLabel.TLabel").grid(row=0, column=0, padx=10, pady=10)
        departamentos = ["OTIC", "Oficina de Gestion Administrativa", "Oficina Contabilidad","Oficina Compras","Oficina de Bienes","Direccion de Servicios Generales y Transporte","Oficina de Seguimiento y Proyectos Estructurales","Direccion General de Planificacion Estrategica","Planoteca","Biblioteca","Direccion General de Seguimiento de Proyectos","Gestion Participativa Parque la isla","Oficina de Atencion ciudadana","Oficina de gestion Humana","Presidencia","Secretaria General","Consultoria Juridica","Oficina de Planificacion y Presupuesto","Auditoria","Direccion de informacion y Comunicacion","Direccion General de Formacion"]  # Reemplaza con tus departamentos
        departamentos.sort()
        departamento_var = tk.StringVar(ventana_salida)
        departamento_var.set(departamentos[0] if departamentos else "")
        combo_departamento = ttk.Combobox(ventana_salida, textvariable=departamento_var, values=departamentos, style="TCombobox")
        combo_departamento.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(ventana_salida, text="Cantidad:", style="CustomLabel.TLabel").grid(row=1, column=0, padx=10, pady=10)
        entry_cantidad = ttk.Entry(ventana_salida, style="CustomEntry.TEntry")
        entry_cantidad.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(ventana_salida, text="Fecha:", style="CustomLabel.TLabel").grid(row=2, column=0, padx=10, pady=10)
        entry_fecha = ttk.Entry(ventana_salida, style="CustomEntry.TEntry")
        entry_fecha.grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(ventana_salida, text="Calendario", command=lambda: abrir_calendario(ventana_salida, entry_fecha), style="CustomButton.TButton").grid(row=2, column=2, padx=10, pady=10)

        ttk.Label(ventana_salida, text="Número de Requisición:", style="CustomLabel.TLabel").grid(row=3, column=0, padx=10, pady=10)
        entry_numero_requisicion = ttk.Entry(ventana_salida, style="CustomEntry.TEntry")
        entry_numero_requisicion.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        ttk.Button(ventana_salida, text="Confirmar Salida", command=confirmar_salida, style="CustomButton.TButton").grid(row=4, column=0, columnspan=3, pady=15, padx=10, sticky="ew")
        ventana_salida.grid_columnconfigure(1, weight=1)

    def eliminar_producto_contextual(producto):
        """Elimina un producto del inventario desde el menú contextual."""
        if messagebox.askyesno("Eliminar Producto", f"¿Seguro que desea eliminar {producto} del inventario?"):
            if producto in inventario:
                del inventario[producto]
                mostrar_tabla(categoria_seleccionada_mostrar.get())
                messagebox.showinfo("Producto Eliminado", f"Producto '{producto}' eliminado del inventario.")
            else:
                messagebox.showerror("Error", "El producto no existe en el inventario.")

    # Función para manejar el clic derecho en un producto
    def menu_contextual(event):
        item = tabla_productos.identify_row(event.y)
        if item:
            producto_nombre = tabla_productos.item(item, "values")[1]  # Obtener el nombre del producto
            menu = tk.Menu(ventana_inventario, tearoff=0)
            menu.add_command(label="Realizar Entrada", command=lambda: realizar_entrada_contextual(producto_nombre))
            menu.add_command(label="Realizar Salida", command=lambda: realizar_salida_contextual(producto_nombre))
            menu.add_command(label="Eliminar Producto", command=lambda: eliminar_producto_contextual(producto_nombre))
            menu.post(event.x_root, event.y_root)

    # Enlazar el evento de clic derecho al Treeview
    tabla_productos.bind("<Button-3>", menu_contextual)

    ventana_inventario.grid_columnconfigure(0, weight=1)
    ventana_inventario.grid_rowconfigure(1, weight=1)



def calcular_consumo_departamento():
    """Calcula el consumo diario, semanal y mensual por departamento y en general."""

    consumo_diario = calcular_consumo_periodo(datetime.timedelta(days=1))
    consumo_semanal = calcular_consumo_periodo(datetime.timedelta(weeks=1))
    consumo_mensual = calcular_consumo_periodo(datetime.timedelta(days=30))

    mostrar_consumo_periodos(consumo_diario, consumo_semanal, consumo_mensual)

def mostrar_consumo_periodos(consumo_diario, consumo_semanal, consumo_mensual):
    """Muestra el consumo para los tres períodos en una tabla."""
    ventana_consumo = tk.Toplevel(ventana)  # Usar la variable global 'ventana'
    ventana_consumo.title("Consumo por Período")
    ventana_consumo.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_consumo)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#A9A9A9",
                    font=("Segoe UI", 10, "bold"))

    style.configure("Grid.Treeview",
                    foreground="#000000",
                    background="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview",
              background=[('selected', '#bddfff')],
              foreground=[('selected', '#000000')])

    # Treeview (tabla) para mostrar el consumo
    tabla_consumo = ttk.Treeview(ventana_consumo, columns=("Departamento", "Producto", "Diario", "Semanal", "Mensual", "Unidad Medida", "Porcentaje"), show="headings", style="Grid.Treeview")
    tabla_consumo.pack(fill=tk.BOTH, expand=True)

    # Definir encabezados de columna
    tabla_consumo.heading("Departamento", text="Departamento", anchor=tk.W)
    tabla_consumo.heading("Producto", text="Producto", anchor=tk.W)
    tabla_consumo.heading("Diario", text="Diario", anchor=tk.W)
    tabla_consumo.heading("Semanal", text="Semanal", anchor=tk.W)
    tabla_consumo.heading("Mensual", text="Mensual", anchor=tk.W)
    tabla_consumo.heading("Unidad Medida", text="Unidad Medida", anchor=tk.W)
    tabla_consumo.heading("Porcentaje", text="Porcentaje", anchor=tk.W)

    # Configurar ancho de columnas
    tabla_consumo.column("Departamento", width=150)
    tabla_consumo.column("Producto", width=150)
    tabla_consumo.column("Diario", width=80)
    tabla_consumo.column("Semanal", width=80)
    tabla_consumo.column("Mensual", width=80)
    tabla_consumo.column("Unidad Medida", width=100)
    tabla_consumo.column("Porcentaje", width=100)

    # Insertar datos en la tabla
    departamentos = set()
    productos = set()
    for consumo in [consumo_diario, consumo_semanal, consumo_mensual]:
        departamentos.update(consumo[0].keys())
        for productos_departamento in consumo[0].values():
            productos.update(productos_departamento.keys())

    for departamento in departamentos:
        for producto in productos:
            diario = consumo_diario[0].get(departamento, {}).get(producto, 0)
            semanal = consumo_semanal[0].get(departamento, {}).get(producto, 0)
            mensual = consumo_mensual[0].get(departamento, {}).get(producto, 0)
            unidad_medida = inventario[producto]["unidad_medida"]

            # Calcular el consumo total para el producto
            consumo_total = diario + semanal + mensual

            # Calcular el porcentaje de consumo
            porcentaje = (consumo_total / sum([consumo_diario[1], consumo_semanal[1], consumo_mensual[1]])) * 100 if sum([consumo_diario[1], consumo_semanal[1], consumo_mensual[1]]) > 0 else 0

            tabla_consumo.insert("", tk.END, values=(departamento, producto, diario, semanal, mensual, unidad_medida, f"{porcentaje:.2f}%"))


def calcular_consumo_periodo(periodo):
    """Calcula el consumo para un período específico."""
    consumo_departamentos = {}
    total_consumo = 0
    fecha_actual = datetime.date.today()
    fecha_inicio = fecha_actual - periodo

    for salida in salidas_departamentos:  # Iterar sobre la lista de salidas
        fecha_salida = salida["fecha"]

        # Convertir a datetime.date si es una cadena
        if isinstance(fecha_salida, str):
            try:
                fecha_salida = datetime.date.fromisoformat(fecha_salida)
            except ValueError:
                # Manejar fechas inválidas (puedes omitir o registrar el error)
                print(f"Fecha inválida: {salida['fecha']}")
                continue  # Saltar a la siguiente salida

        if fecha_inicio <= fecha_salida <= fecha_actual:
            departamento = salida["destino"]
            producto = salida["producto"]
            cantidad = salida["cantidad"]

            try:
                cantidad = int(cantidad)
            except ValueError:
                print(f"Cantidad inválida: {cantidad} para el producto {producto} en el departamento {departamento}")
                continue  # Saltar a la siguiente salida


            if departamento not in consumo_departamentos:
                consumo_departamentos[departamento] = {}

            if producto not in consumo_departamentos[departamento]:
                consumo_departamentos[departamento][producto] = 0

            consumo_departamentos[departamento][producto] += cantidad
            total_consumo += cantidad

    return consumo_departamentos, total_consumo

def mostrar_consumo_periodo(periodo_nombre, consumo_periodo):
    """Muestra el consumo para un período específico en una tabla."""
    consumo_departamentos, total_consumo = consumo_periodo

    ventana_consumo = tk.Toplevel(ventana)  # Usar la variable global 'ventana'
    ventana_consumo.title(f"Consumo {periodo_nombre}")
    ventana_consumo.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_consumo)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#A9A9A9",
                    font=("Segoe UI", 10, "bold"))

    style.configure("Grid.Treeview",
                    foreground="#000000",
                    background="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview",
              background=[('selected', '#bddfff')],
              foreground=[('selected', '#000000')])

    # Treeview (tabla) para mostrar el consumo
    tabla_consumo = ttk.Treeview(ventana_consumo, columns=("Departamento", "Producto", "Consumo", "Unidad Medida", "Porcentaje"), show="headings", style="Grid.Treeview")
    tabla_consumo.pack(fill=tk.BOTH, expand=True)

    # Definir encabezados de columna
    tabla_consumo.heading("Departamento", text="Departamento", anchor=tk.W)
    tabla_consumo.heading("Producto", text="Producto", anchor=tk.W)
    tabla_consumo.heading("Consumo", text="Consumo", anchor=tk.W)
    tabla_consumo.heading("Unidad Medida", text="Unidad Medida", anchor=tk.W)
    tabla_consumo.heading("Porcentaje", text="Porcentaje", anchor=tk.W)

    # Configurar ancho de columnas
    tabla_consumo.column("Departamento", width=150)
    tabla_consumo.column("Producto", width=150)
    tabla_consumo.column("Consumo", width=80)
    tabla_consumo.column("Unidad Medida", width=100)
    tabla_consumo.column("Porcentaje", width=100)

    # Insertar datos en la tabla
    for departamento, productos in consumo_departamentos.items():
        for producto, cantidad in productos.items():
            unidad_medida = inventario[producto]["unidad_medida"]
            porcentaje = (cantidad / total_consumo) * 100 if total_consumo > 0 else 0
            tabla_consumo.insert("", tk.END, values=(departamento, producto, cantidad, unidad_medida, f"{porcentaje:.2f}%"))

    

    




                            #Hasta aqui funciones principales.


















                                    #Funciones de reportes:

def generar_reporte_bajo_stock():
    """Genera un reporte de productos con bajo stock en una tabla."""
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title("Reporte de Bajo Stock")
    ventana_reporte.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_reporte)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#A9A9A9",
                    font=("Segoe UI", 10, "bold"))

    style.configure("Grid.Treeview",
                    foreground="#000000",
                    background="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview",
              background=[('selected', '#bddfff')],
              foreground=[('selected', '#000000')])

    umbral_stock_minimo = 1  # Puedes ajustar este valor
    productos_bajo_stock = []
    for producto, datos in inventario.items():
        if datos["stock"] < umbral_stock_minimo:
            productos_bajo_stock.append((producto, datos))

    if productos_bajo_stock:
        # Treeview (tabla) para mostrar el reporte de bajo stock
        tabla_bajo_stock = ttk.Treeview(ventana_reporte, columns=("Producto", "Stock Actual", "Unidad Medida"), show="headings", style="Grid.Treeview")
        tabla_bajo_stock.pack(fill=tk.BOTH, expand=True)

        # Definir encabezados de columna
        tabla_bajo_stock.heading("Producto", text="Producto", anchor=tk.W)
        tabla_bajo_stock.heading("Stock Actual", text="Stock Actual", anchor=tk.W)
        tabla_bajo_stock.heading("Unidad Medida", text="Unidad Medida", anchor=tk.W)

        # Configurar ancho de columnas
        tabla_bajo_stock.column("Producto", width=150)
        tabla_bajo_stock.column("Stock Actual", width=100)
        tabla_bajo_stock.column("Unidad Medida", width=100)

        # Insertar datos en la tabla
        for producto, datos in productos_bajo_stock:
            tabla_bajo_stock.insert("", tk.END, values=(producto, datos["stock"], datos["unidad_medida"]))

        # Agregar barra de desplazamiento vertical
        scrollbar_y = ttk.Scrollbar(ventana_reporte, orient="vertical", command=tabla_bajo_stock.yview)
        scrollbar_y.pack(side="right", fill="y")
        tabla_bajo_stock.configure(yscrollcommand=scrollbar_y.set)
    else:
        messagebox.showinfo("Reporte de Bajo Stock", "No hay productos con bajo stock.")
        





def generar_reporte_entradas():
    """Genera un reporte del historial de entradas."""
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title("Reporte de Entradas")
    ventana_reporte.geometry("800x500")
    ventana_reporte.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_reporte)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#A9A9A9",
                    font=("Segoe UI", 10, "bold"))

    style.configure("CustomEntry.TEntry",
                    foreground="#000000",
                    background="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10))

    style.configure("Grid.Treeview",
                    foreground="#000000",
                    background="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview",
              background=[('selected', '#bddfff')],
              foreground=[('selected', '#000000')])

    # Treeview (tabla) para mostrar las entradas
    tabla_entradas = ttk.Treeview(ventana_reporte, columns=("Producto", "Cantidad", "Fecha", "Destino"), show="headings", style="Grid.Treeview")
    tabla_entradas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Definir encabezados de columna
    tabla_entradas.heading("Producto", text="Producto", anchor=tk.W)
    tabla_entradas.heading("Cantidad", text="Cantidad", anchor=tk.W)
    tabla_entradas.heading("Fecha", text="Fecha", anchor=tk.W)
    tabla_entradas.heading("Destino", text="Destino", anchor=tk.W)

    # Configurar ancho de columnas
    tabla_entradas.column("Producto", width=150)
    tabla_entradas.column("Cantidad", width=80)
    tabla_entradas.column("Fecha", width=100)
    tabla_entradas.column("Destino", width=150)

    # Barras de desplazamiento
    scrollbar_vertical = ttk.Scrollbar(ventana_reporte, orient="vertical", command=tabla_entradas.yview)
    scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
    tabla_entradas.configure(yscrollcommand=scrollbar_vertical.set)

    # Insertar datos iniciales en la tabla
    for entrada in entradas_departamentos:
        fecha_str = entrada["fecha"].strftime("%Y-%m-%d") if isinstance(entrada["fecha"], datetime.date) else str(entrada["fecha"])
        tabla_entradas.insert("", tk.END, values=(
            entrada["producto"],
            entrada["cantidad"],
            fecha_str,
            entrada["destino"]
        ))

    def eliminar_entrada():
        seleccion = tabla_entradas.selection()
        if seleccion:
            item_id = seleccion[0]  # Obtener el ID del elemento seleccionado
            index = tabla_entradas.index(item_id)  # Obtener el índice del elemento en la tabla

            if 0 <= index < len(entradas_departamentos):  # Verificar si el índice es válido
                del entradas_departamentos[index]
                tabla_entradas.delete(item_id)
            else:
                messagebox.showerror("Error", "Índice de elemento no válido.")

    def editar_entrada():
        seleccion = tabla_entradas.selection()
        if seleccion:
            item_id = seleccion[0]  # Obtener el ID del elemento seleccionado
            index = tabla_entradas.index(item_id)  # Obtener el índice del elemento en la tabla

            if 0 <= index < len(entradas_departamentos):  # Verificar si el índice es válido
                entrada = entradas_departamentos[index]

                # Crear ventana de edición
                ventana_edicion = tk.Toplevel(ventana_reporte)
                ventana_edicion.title("Editar Entrada")
                ventana_edicion.configure(bg="#A9A9A9")

                # Crear etiquetas y campos de entrada para cada columna
                tk.Label(ventana_edicion, text="Producto:", fg="#ffffff", bg="#A9A9A9").grid(row=0, column=0, padx=5, pady=5)
                entry_producto = tk.Entry(ventana_edicion)
                entry_producto.grid(row=0, column=1, padx=5, pady=5)
                entry_producto.insert(0, entrada["producto"])

                tk.Label(ventana_edicion, text="Cantidad:", fg="#ffffff", bg="#A9A9A9").grid(row=1, column=0, padx=5, pady=5)
                entry_cantidad = tk.Entry(ventana_edicion)
                entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
                entry_cantidad.insert(0, entrada["cantidad"])

                tk.Label(ventana_edicion, text="Fecha:", fg="#ffffff", bg="#A9A9A9").grid(row=2, column=0, padx=5, pady=5)
                entry_fecha = tk.Entry(ventana_edicion)
                entry_fecha.grid(row=2, column=1, padx=5, pady=5)
                entry_fecha.insert(0, entrada["fecha"])

                tk.Label(ventana_edicion, text="Destino:", fg="#ffffff", bg="#A9A9A9").grid(row=3, column=0, padx=5, pady=5)
                entry_destino = tk.Entry(ventana_edicion)
                entry_destino.grid(row=3, column=1, padx=5, pady=5)
                entry_destino.insert(0, entrada["destino"])

                # Función para guardar los cambios
                def guardar_cambios():
                    entrada["producto"] = entry_producto.get()
                    try:
                        entrada["cantidad"] = int(entry_cantidad.get())
                    except ValueError:
                        messagebox.showerror("Error", "Cantidad debe ser un número entero.")
                        return
                    entrada["fecha"] = entry_fecha.get()
                    entrada["destino"] = entry_destino.get()
                    # Formatear la fecha a una cadena legible para la tabla
                    fecha_str_tabla = entrada["fecha"].strftime("%Y-%m-%d") if isinstance(entrada["fecha"], datetime.date) else str(entrada["fecha"])
                    tabla_entradas.item(seleccion, values=(entrada["producto"], entrada["cantidad"], fecha_str_tabla, entrada["destino"]))
                    ventana_edicion.destroy()

                # Botón para guardar los cambios
                ttk.Button(ventana_edicion, text="Guardar", command=guardar_cambios).grid(row=4, column=0, columnspan=2, pady=10)
            else:
                messagebox.showerror("Error", "Índice de elemento no válido.")

    def buscar_producto_abreviatura():
        """Abre una ventana para buscar producto por abreviatura."""
        ventana_busqueda_abreviatura = tk.Toplevel(ventana_reporte)
        ventana_busqueda_abreviatura.title("Buscar Producto por Abreviatura")
        ventana_busqueda_abreviatura.configure(bg="#A9A9A9")

        tk.Label(ventana_busqueda_abreviatura, text="Ingrese abreviatura:", fg="#ffffff", bg="#A9A9A9").pack(padx=10, pady=10)
        entry_abreviatura = ttk.Entry(ventana_busqueda_abreviatura)
        entry_abreviatura.pack(padx=10, pady=5)

        def filtrar_por_abreviatura(event):
            abreviatura = entry_abreviatura.get().lower()
            tabla_entradas.delete(*tabla_entradas.get_children())
            for entrada in entradas_departamentos:
                if abreviatura in entrada["producto"].lower():
                    fecha_str = entrada["fecha"].strftime("%Y-%m-%d") if isinstance(entrada["fecha"], datetime.date) else str(entrada["fecha"])
                    tabla_entradas.insert("", tk.END, values=(
                        entrada["producto"],
                        entrada["cantidad"],
                        fecha_str,
                        entrada["destino"]
                    ))

        entry_abreviatura.bind("<KeyRelease>", filtrar_por_abreviatura)

    # Crear menú contextual (clic derecho)
    menu_contextual = tk.Menu(ventana_reporte, tearoff=0)
    menu_contextual.add_command(label="Eliminar", command=eliminar_entrada)
    menu_contextual.add_command(label="Editar", command=editar_entrada)
    menu_contextual.add_command(label="Buscar por Abreviatura", command=buscar_producto_abreviatura)

    # Vincular el menú contextual al clic derecho
    def mostrar_menu_contextual(event):
        item = tabla_entradas.identify_row(event.y)
        if item:
            tabla_entradas.selection_set(item)
            menu_contextual.post(event.x_root, event.y_root)

    tabla_entradas.bind("<Button-3>", mostrar_menu_contextual)
    


def generar_reporte_salidas():
    """Genera un reporte del historial de salidas."""
    ventana_reporte_salidas = tk.Toplevel(ventana)
    ventana_reporte_salidas.title("Reporte de Salidas")
    ventana_reporte_salidas.geometry("900x500")
    ventana_reporte_salidas.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_reporte_salidas)
    style.theme_use('clam')

    style.configure("CustomLabel.TLabel",
                    foreground="#ffffff",
                    background="#A9A9A9",
                    font=("Segoe UI", 10, "bold"))

    style.configure("CustomEntry.TEntry",
                    foreground="#000000",
                    background="#ffffff",
                    insertcolor="#000000",
                    font=("Segoe UI", 10))

    style.configure("Grid.Treeview",
                    foreground="#000000",
                    background="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading",
                    foreground="#000000",
                    background="#d9d9d9",
                    font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview",
              background=[('selected', '#bddfff')],
              foreground=[('selected', '#000000')])

    tree = ttk.Treeview(ventana_reporte_salidas, columns=("Producto", "Cantidad", "Fecha", "Destino", "Requisición"), show="headings", style="Grid.Treeview")
    tree.heading("Producto", text="Producto", anchor=tk.W)
    tree.heading("Cantidad", text="Cantidad", anchor=tk.W)
    tree.heading("Fecha", text="Fecha", anchor=tk.W)
    tree.heading("Destino", text="Destino", anchor=tk.W)
    tree.heading("Requisición", text="Requisición", anchor=tk.W)
    tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    scrollbar = ttk.Scrollbar(ventana_reporte_salidas, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

    for salida in salidas_departamentos:
        fecha_str = salida["fecha"].strftime("%Y-%m-%d") if isinstance(salida["fecha"], datetime.date) else str(salida["fecha"])
        tree.insert("", "end", values=(salida["producto"], salida["cantidad"], fecha_str, salida["destino"], salida["requisicion"]))

    def eliminar_salida():
        seleccion = tree.selection()
        if seleccion:
            item_id = seleccion[0]
            index = tree.index(item_id)
            if 0 <= index < len(salidas_departamentos):
                del salidas_departamentos[index]
                tree.delete(item_id)
            else:
                messagebox.showerror("Error", "Índice de elemento no válido.")

    def editar_salida():
        seleccion = tree.selection()
        if seleccion:
            item_id = seleccion[0]
            index = tree.index(item_id)
            if 0 <= index < len(salidas_departamentos):
                salida = salidas_departamentos[index]

                # Crear ventana de edición
                ventana_edicion = tk.Toplevel(ventana_reporte_salidas)
                ventana_edicion.title("Editar Salida")
                ventana_edicion.configure(bg="#A9A9A9")

                # Crear etiquetas y campos de entrada para cada columna
                tk.Label(ventana_edicion, text="Producto:", fg="#ffffff", bg="#A9A9A9").grid(row=0, column=0, padx=5, pady=5)
                entry_producto = tk.Entry(ventana_edicion)
                entry_producto.grid(row=0, column=1, padx=5, pady=5)
                entry_producto.insert(0, salida["producto"])

                tk.Label(ventana_edicion, text="Cantidad:", fg="#ffffff", bg="#A9A9A9").grid(row=1, column=0, padx=5, pady=5)
                entry_cantidad = tk.Entry(ventana_edicion)
                entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
                entry_cantidad.insert(0, salida["cantidad"])

                tk.Label(ventana_edicion, text="Fecha:", fg="#ffffff", bg="#A9A9A9").grid(row=2, column=0, padx=5, pady=5)
                entry_fecha = tk.Entry(ventana_edicion)
                entry_fecha.grid(row=2, column=1, padx=5, pady=5)
                entry_fecha.insert(0, salida["fecha"])

                tk.Label(ventana_edicion, text="Destino:", fg="#ffffff", bg="#A9A9A9").grid(row=3, column=0, padx=5, pady=5)
                entry_destino = tk.Entry(ventana_edicion)
                entry_destino.grid(row=3, column=1, padx=5, pady=5)
                entry_destino.insert(0, salida["destino"])

                tk.Label(ventana_edicion, text="Requisición:", fg="#ffffff", bg="#A9A9A9").grid(row=4, column=0, padx=5, pady=5)
                entry_requisicion = tk.Entry(ventana_edicion)
                entry_requisicion.grid(row=4, column=1, padx=5, pady=5)
                entry_requisicion.insert(0, salida["requisicion"])

                # Función para guardar los cambios
                def guardar_cambios():
                    salida["producto"] = entry_producto.get()
                    try:
                        salida["cantidad"] = int(entry_cantidad.get())
                    except ValueError:
                        messagebox.showerror("Error", "Cantidad debe ser un número entero.")
                        return
                    salida["fecha"] = entry_fecha.get()
                    salida["destino"] = entry_destino.get()
                    salida["requisicion"] = entry_requisicion.get()
                    fecha_str_tabla = salida["fecha"].strftime("%Y-%m-%d") if isinstance(salida["fecha"], datetime.date) else str(salida["fecha"])
                    tree.item(seleccion, values=(salida["producto"], salida["cantidad"], fecha_str_tabla, salida["destino"], salida["requisicion"]))
                    ventana_edicion.destroy()

                # Botón para guardar los cambios
                ttk.Button(ventana_edicion, text="Guardar", command=guardar_cambios).grid(row=5, column=0, columnspan=2, pady=10)
            else:
                messagebox.showerror("Error", "Índice de elemento no válido.")

    def buscar_producto_abreviatura():
        """Abre una ventana para buscar producto por abreviatura."""
        ventana_busqueda_abreviatura = tk.Toplevel(ventana_reporte_salidas)
        ventana_busqueda_abreviatura.title("Buscar Producto por Abreviatura")
        ventana_busqueda_abreviatura.configure(bg="#A9A9A9")

        tk.Label(ventana_busqueda_abreviatura, text="Ingrese abreviatura:", fg="#ffffff", bg="#A9A9A9").pack(padx=10, pady=10)
        entry_abreviatura = ttk.Entry(ventana_busqueda_abreviatura)
        entry_abreviatura.pack(padx=10, pady=5)

        def filtrar_por_abreviatura(event):
            abreviatura = entry_abreviatura.get().lower()
            tree.delete(*tree.get_children())
            for salida in salidas_departamentos:
                if abreviatura in salida["producto"].lower():
                    fecha_str = salida["fecha"].strftime("%Y-%m-%d") if isinstance(salida["fecha"], datetime.date) else str(salida["fecha"])
                    tree.insert("", "end", values=(
                        salida["producto"],
                        salida["cantidad"],
                        fecha_str,
                        salida["destino"],
                        salida["requisicion"]
                    ))

        entry_abreviatura.bind("<KeyRelease>", filtrar_por_abreviatura)

    # Crear menú contextual (clic derecho)
    menu_contextual = tk.Menu(ventana_reporte_salidas, tearoff=0)
    menu_contextual.add_command(label="Eliminar", command=eliminar_salida)
    menu_contextual.add_command(label="Editar", command=editar_salida)
    menu_contextual.add_command(label="Buscar por Abreviatura", command=buscar_producto_abreviatura)

    # Vincular el menú contextual al clic derecho
    def mostrar_menu_contextual(event):
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            menu_contextual.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", mostrar_menu_contextual)

    ventana_reporte_salidas.grid_columnconfigure(0, weight=1)
    ventana_reporte_salidas.grid_rowconfigure(0, weight=1)

ventana_reporte_salidas_espera = None  # Variable global para la ventana del reporte de espera
tabla_salidas_espera = None           # Variable global para la tabla

def actualizar_tabla_salidas_espera():
    """Actualiza el contenido de la tabla de salidas en espera."""
    global tabla_salidas_espera
    if tabla_salidas_espera:
        tabla_salidas_espera.delete(*tabla_salidas_espera.get_children())
        for salida in salidas_espera:
            tabla_salidas_espera.insert("", tk.END, values=(
                salida["producto"],
                salida["cantidad"],
                salida["departamento"],
            ))

def generar_reporte_salidas_espera():
    """Genera o trae al frente la ventana del reporte de salidas en espera."""
    global ventana_reporte_salidas_espera, tabla_salidas_espera # Declarar tabla_salidas_espera como global

    if ventana_reporte_salidas_espera and ventana_reporte_salidas_espera.winfo_exists():
        ventana_reporte_salidas_espera.lift()  # Traer la ventana al frente
        actualizar_tabla_salidas_espera()
        return

    ventana_reporte_salidas_espera = tk.Toplevel(ventana)
    ventana_reporte_salidas_espera.title("Reporte de Salidas en Espera")
    ventana_reporte_salidas_espera.geometry("700x500")
    ventana_reporte_salidas_espera.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_reporte_salidas_espera)
    style.theme_use('clam')
    style.configure("CustomLabel.TLabel", foreground="#ffffff", background="#A9A9A9", font=("Segoe UI", 10, "bold"))
    style.configure("CustomEntry.TEntry", foreground="#000000", background="#ffffff", insertcolor="#000000", font=("Segoe UI", 10))
    style.configure("Grid.Treeview", foreground="#000000", background="#ffffff", font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading", foreground="#000000", background="#d9d9d9", font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview", background=[('selected', '#bddfff')], foreground=[('selected', '#000000')])

    # Treeview (tabla) para mostrar las salidas en espera
    tabla_salidas_espera = ttk.Treeview(ventana_reporte_salidas_espera, columns=("Producto", "Cantidad", "Departamento"), show="headings", style="Grid.Treeview")
    tabla_salidas_espera.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Definir encabezados de columna
    tabla_salidas_espera.heading("Producto", text="Producto", anchor=tk.W)
    tabla_salidas_espera.heading("Cantidad", text="Cantidad", anchor=tk.W)
    tabla_salidas_espera.heading("Departamento", text="Departamento", anchor=tk.W)

    # Configurar ancho de columnas
    tabla_salidas_espera.column("Producto", width=200)
    tabla_salidas_espera.column("Cantidad", width=100)
    tabla_salidas_espera.column("Departamento", width=200)

    # Barras de desplazamiento
    scrollbar_vertical = ttk.Scrollbar(ventana_reporte_salidas_espera, orient="vertical", command=tabla_salidas_espera.yview)
    scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=10)
    tabla_salidas_espera.configure(yscrollcommand=scrollbar_vertical.set)

    # Insertar datos iniciales en la tabla
    actualizar_tabla_salidas_espera()

    # Función para agregar número de requisición
    def agregar_requisicion():
        item_seleccionado = tabla_salidas_espera.selection()
        if item_seleccionado:
            item = item_seleccionado[0]
            valores = tabla_salidas_espera.item(item, "values")
            if len(valores) >= 3:
                producto = valores[0]
                cantidad = valores[1]
                destino = valores[2]

                def confirmar_requisicion():
                    numero_requisicion = entry_requisicion.get()
                    fecha_salida = entry_fecha.get()

                    salidas_departamentos.append({
                        "producto": producto,
                        "cantidad": cantidad,
                        "fecha": fecha_salida,
                        "destino": destino,
                        "requisicion": numero_requisicion
                    })

                    try:
                        diccionario_a_eliminar = {
                            "producto": producto,
                            "cantidad": int(cantidad),
                            "departamento": destino
                        }
                    except ValueError:
                        messagebox.showerror("Error", "Cantidad inválida. Debe ser un número entero.")
                        return

                    for i, salida_espera in enumerate(salidas_espera):
                        if (salida_espera["producto"] == diccionario_a_eliminar["producto"] and
                                salida_espera["cantidad"] == diccionario_a_eliminar["cantidad"] and
                                salida_espera["departamento"] == diccionario_a_eliminar["departamento"]):
                            del salidas_espera[i]
                            break

                    guardar_datos()
                    tabla_salidas_espera.delete(item_seleccionado)  # Eliminar la fila seleccionada
                    actualizar_tabla_salidas_espera()  # Actualizar la tabla existente

                    if ventana_requisicion.winfo_exists():
                        ventana_requisicion.destroy()

                ventana_requisicion = tk.Toplevel(ventana_reporte_salidas_espera) # Usar la ventana existente como parent
                ventana_requisicion.title("Agregar Requisición y Fecha")
                ventana_requisicion.configure(bg="#A9A9A9")

                tk.Label(ventana_requisicion, text="Número de Requisición:", fg="#ffffff", bg="#A9A9A9").grid(row=0, column=0, padx=5, pady=5)
                entry_requisicion = ttk.Entry(ventana_requisicion)
                entry_requisicion.grid(row=0, column=1, padx=5, pady=5)

                tk.Label(ventana_requisicion, text="Fecha de Salida:", fg="#ffffff", bg="#A9A9A9").grid(row=1, column=0, padx=5, pady=5)
                entry_fecha = ttk.Entry(ventana_requisicion)
                entry_fecha.grid(row=1, column=1, padx=5, pady=5)
                ttk.Button(ventana_requisicion, text="Calendario", command=lambda: abrir_calendario(ventana_requisicion, entry_fecha)).grid(row=1, column=2, padx=5, pady=5)

                ttk.Button(ventana_requisicion, text="Confirmar", command=confirmar_requisicion).grid(row=2, column=0, columnspan=3, pady=10)
            else:
                messagebox.showerror("Error", "Datos de producto incompletos.")
        else:
            messagebox.showerror("Error", "Seleccione un producto.")

    # Función para eliminar una salida en espera
    def eliminar_salida_espera():
        seleccion = tabla_salidas_espera.selection()
        if seleccion:
            item_id = seleccion[0]
            index = tabla_salidas_espera.index(item_id)
            if 0 <= index < len(salidas_espera):
                del salidas_espera[index]
                actualizar_tabla_salidas_espera()
            else:
                messagebox.showerror("Error", "Índice de elemento no válido.")

    # Función para editar una salida en espera
    def editar_salida_espera():
        seleccion = tabla_salidas_espera.selection()
        if seleccion:
            item_id = seleccion[0]
            index = tabla_salidas_espera.index(item_id)
            if 0 <= index < len(salidas_espera):
                salida = salidas_espera[index]

                # Crear ventana de edición
                ventana_edicion = tk.Toplevel(ventana_reporte_salidas_espera) # Usar la ventana existente como parent
                ventana_edicion.title("Editar Salida en Espera")
                ventana_edicion.configure(bg="#A9A9A9")

                # Crear etiquetas y campos de entrada para cada columna
                tk.Label(ventana_edicion, text="Producto:", fg="#ffffff", bg="#A9A9A9").grid(row=0, column=0, padx=5, pady=5)
                entry_producto = ttk.Entry(ventana_edicion)
                entry_producto.grid(row=0, column=1, padx=5, pady=5)
                entry_producto.insert(0, salida["producto"])

                tk.Label(ventana_edicion, text="Cantidad:", fg="#ffffff", bg="#A9A9A9").grid(row=1, column=0, padx=5, pady=5)
                entry_cantidad = ttk.Entry(ventana_edicion)
                entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
                entry_cantidad.insert(0, salida["cantidad"])

                tk.Label(ventana_edicion, text="Departamento:", fg="#ffffff", bg="#A9A9A9").grid(row=2, column=0, padx=5, pady=5)
                entry_departamento = ttk.Entry(ventana_edicion)
                entry_departamento.grid(row=2, column=1, padx=5, pady=5)
                entry_departamento.insert(0, salida["departamento"])

                # Función para guardar los cambios
                def guardar_cambios():
                    salida["producto"] = entry_producto.get()
                    try:
                        salida["cantidad"] = int(entry_cantidad.get())
                    except ValueError:
                        messagebox.showerror("Error", "Cantidad inválida. Debe ser un número entero.")
                        return
                    salida["departamento"] = entry_departamento.get()
                    tabla_salidas_espera.item(seleccion, values=(salida["producto"], salida["cantidad"], salida["departamento"]))
                    ventana_edicion.destroy()
                    actualizar_tabla_salidas_espera() # Actualizar la tabla principal

                # Botón para guardar los cambios
                ttk.Button(ventana_edicion, text="Guardar", command=guardar_cambios).grid(row=3, column=0, columnspan=2, pady=10)
            else:
                messagebox.showerror("Error", "Índice de elemento no válido.")

    def buscar_producto_abreviatura():
        """Abre una ventana para buscar producto por abreviatura."""
        ventana_busqueda_abreviatura = tk.Toplevel(ventana_reporte_salidas_espera) # Usar la ventana existente como parent
        ventana_busqueda_abreviatura.title("Buscar Producto por Abreviatura")
        ventana_busqueda_abreviatura.configure(bg="#A9A9A9")

        tk.Label(ventana_busqueda_abreviatura, text="Ingrese abreviatura:", fg="#ffffff", bg="#A9A9A9").pack(padx=10, pady=10)
        entry_abreviatura = ttk.Entry(ventana_busqueda_abreviatura)
        entry_abreviatura.pack(padx=10, pady=5)

        def filtrar_por_abreviatura(event):
            abreviatura = entry_abreviatura.get().lower()
            tabla_salidas_espera.delete(*tabla_salidas_espera.get_children())
            for salida in salidas_espera:
                if abreviatura in salida["producto"].lower():
                    tabla_salidas_espera.insert("", tk.END, values=(
                        salida["producto"],
                        salida["cantidad"],
                        salida["departamento"],
                    ))

        entry_abreviatura.bind("<KeyRelease>", filtrar_por_abreviatura)

    # Crear menú contextual (clic derecho)
    menu_contextual = tk.Menu(ventana_reporte_salidas_espera, tearoff=0)
    menu_contextual.add_command(label="Eliminar", command=eliminar_salida_espera)
    menu_contextual.add_command(label="Editar", command=editar_salida_espera)
    menu_contextual.add_command(label="Agregar Requisición", command=agregar_requisicion)
    menu_contextual.add_command(label="Buscar por Abreviatura", command=buscar_producto_abreviatura)

    # Vincular el menú contextual al clic derecho
    def mostrar_menu_contextual(event):
        item = tabla_salidas_espera.identify_row(event.y)
        if item:
            tabla_salidas_espera.selection_set(item)
            menu_contextual.post(event.x_root, event.y_root)

    tabla_salidas_espera.bind("<Button-3>", mostrar_menu_contextual)

    ventana_reporte_salidas_espera.grid_columnconfigure(0, weight=1)
    ventana_reporte_salidas_espera.grid_rowconfigure(0, weight=1)



def ventana_reportes():
    """Crea una ventana para generar reportes con opciones de filtrado y nuevos reportes."""
    ventana_reporte = tk.Toplevel()
    ventana_reporte.title("Generar Reportes")
    ventana_reporte.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_reporte)
    style.theme_use('clam')
    style.configure("CustomLabel.TLabel", foreground="#ffffff", background="#A9A9A9", font=("Segoe UI", 10, "bold"))
    style.configure("CustomEntry.TEntry", foreground="#000000", background="#ffffff", insertcolor="#000000", font=("Segoe UI", 10))
    style.configure("TCombobox", foreground="#000000", background="#ffffff", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("Small.TButton", font=("Segoe UI", 8)) # Define un estilo más pequeño
    style.configure("Grid.Treeview", foreground="#000000", background="#ffffff", font=("Segoe UI", 10))
    style.configure("Grid.Treeview.Heading", foreground="#000000", background="#d9d9d9", font=("Segoe UI", 10, "bold"))
    style.map("Grid.Treeview", background=[('selected', '#bddfff')], foreground=[('selected', '#000000')])
    style.configure("TFrame", background="#A9A9A9") # Estilo para los frames

    # Marco principal para centrar el contenido
    main_frame = ttk.Frame(ventana_reporte, style="TFrame")
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)
    main_frame.grid_columnconfigure(0, weight=1) # Para centrar horizontalmente

    # Marcos para organizar los widgets
    frame_filtros = ttk.Frame(main_frame, style="TFrame")
    frame_filtros.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    frame_tabla = ttk.Frame(main_frame, style="TFrame")
    frame_tabla.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    # --- Filtro por Categoría con Selección de Lapso ---
    label_categoria = ttk.Label(frame_filtros, text="Filtrar por Categoría:", style="CustomLabel.TLabel")
    label_categoria.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    categorias = ["Todas"] + sorted(list(set(datos["categoria"] for datos in inventario.values())))
    categoria_seleccionada = ttk.Combobox(frame_filtros, values=categorias, style="TCombobox", width=20)
    categoria_seleccionada.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    categoria_seleccionada.set("Todas")

    fecha_inicio_cat = tk.StringVar()
    fecha_fin_cat = tk.StringVar()
    fecha_inicio_cat.set("")
    fecha_fin_cat.set("")

    def seleccionar_fecha_inicio_cat():
        top = tk.Toplevel(ventana_reporte)
        top.configure(bg="#A9A9A9")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd', background="#ffffff", foreground="#000000", bordercolor="#d9d9d9", selectbackground="#bddfff", selectforeground="#000000")
        cal.pack(padx=10, pady=10)
        def grabar_fecha():
            fecha_inicio_cat.set(cal.get_date())
            label_fecha_inicio_seleccionada_cat.config(text="Inicio: " + fecha_inicio_cat.get())
            top.destroy()
        boton_seleccionar = ttk.Button(top, text="Seleccionar", command=grabar_fecha)
        boton_seleccionar.pack(pady=5)

    def seleccionar_fecha_fin_cat():
        top = tk.Toplevel(ventana_reporte)
        top.configure(bg="#A9A9A9")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd', background="#ffffff", foreground="#000000", bordercolor="#d9d9d9", selectbackground="#bddfff", selectforeground="#000000")
        cal.pack(padx=10, pady=10)
        def grabar_fecha():
            fecha_fin_cat.set(cal.get_date())
            label_fecha_fin_seleccionada_cat.config(text="Fin: " + fecha_fin_cat.get())
            top.destroy()
        boton_seleccionar = ttk.Button(top, text="Seleccionar", command=grabar_fecha)
        boton_seleccionar.pack(pady=5)

    boton_fecha_inicio_cat = ttk.Button(frame_filtros, text="Inicio", command=seleccionar_fecha_inicio_cat)
    boton_fecha_inicio_cat.grid(row=0, column=2, padx=5, pady=5)
    label_fecha_inicio_seleccionada_cat = ttk.Label(frame_filtros, text="Inicio: --", style="CustomLabel.TLabel")
    label_fecha_inicio_seleccionada_cat.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    boton_fecha_fin_cat = ttk.Button(frame_filtros, text="Fin", command=seleccionar_fecha_fin_cat)
    boton_fecha_fin_cat.grid(row=0, column=4, padx=5, pady=5)
    label_fecha_fin_seleccionada_cat = ttk.Label(frame_filtros, text="Fin: --", style="CustomLabel.TLabel")
    label_fecha_fin_seleccionada_cat.grid(row=0, column=5, padx=5, pady=5, sticky="w")

    lista_de_departamentos_completa = ["OTIC", "Oficina de Gestion Administrativa", "Oficina Contabilidad", "Oficina Compras", "Oficina de Bienes", "Direccion de Servicios Generales y Transporte", "Oficina de Seguimiento y Proyectos Estructurales", "Direccion General de Planificacion Estrategica", "Planoteca", "Biblioteca", "Direccion General de Seguimiento de Proyectos", "Gestion Participativa Parque la isla", "Oficina de Atencion ciudadana", "Oficina de gestion Humana", "Presidencia", "Secretaria General", "Consultoria Juridica", "Oficina de Planificacion y Presupuesto", "Auditoria", "Direccion de informacion y Comunicacion", "Direccion General de Formacion"]
    lista_de_departamentos_completa.sort()

    label_departamento = ttk.Label(frame_filtros, text="Filtrar por Departamento:", style="CustomLabel.TLabel")
    label_departamento.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    lista_departamentos_reporte = ["Todos"] + lista_de_departamentos_completa
    departamento_seleccionado = ttk.Combobox(frame_filtros, values=lista_departamentos_reporte, style="TCombobox", width=30)
    departamento_seleccionado.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    departamento_seleccionado.set("Todos")

    fecha_inicio_dep = tk.StringVar()
    fecha_fin_dep = tk.StringVar()
    fecha_inicio_dep.set("")
    fecha_fin_dep.set("")

    def seleccionar_fecha_inicio_dep():
        top = tk.Toplevel(ventana_reporte)
        top.configure(bg="#A9A9A9")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd', background="#ffffff", foreground="#000000", bordercolor="#d9d9d9", selectbackground="#bddfff", selectforeground="#000000")
        cal.pack(padx=10, pady=10)
        def grabar_fecha():
            fecha_inicio_dep.set(cal.get_date())
            label_fecha_inicio_seleccionada_dep.config(text="Inicio: " + fecha_inicio_dep.get())
            top.destroy()
        boton_seleccionar = ttk.Button(top, text="Seleccionar", command=grabar_fecha)
        boton_seleccionar.pack(pady=5)

    def seleccionar_fecha_fin_dep():
        top = tk.Toplevel(ventana_reporte)
        top.configure(bg="#A9A9A9")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd', background="#ffffff", foreground="#000000", bordercolor="#d9d9d9", selectbackground="#bddfff", selectforeground="#000000")
        cal.pack(padx=10, pady=10)
        def grabar_fecha():
            fecha_fin_dep.set(cal.get_date())
            label_fecha_fin_seleccionada_dep.config(text="Fin: " + fecha_fin_dep.get())
            top.destroy()
        boton_seleccionar = ttk.Button(top, text="Seleccionar", command=grabar_fecha)
        boton_seleccionar.pack(pady=5)

    boton_fecha_inicio_dep = ttk.Button(frame_filtros, text="Inicio", command=seleccionar_fecha_inicio_dep)
    boton_fecha_inicio_dep.grid(row=1, column=2, padx=5, pady=5)
    label_fecha_inicio_seleccionada_dep = ttk.Label(frame_filtros, text="Inicio: --", style="CustomLabel.TLabel")
    label_fecha_inicio_seleccionada_dep.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    boton_fecha_fin_dep = ttk.Button(frame_filtros, text="Fin", command=seleccionar_fecha_fin_dep)
    boton_fecha_fin_dep.grid(row=1, column=4, padx=5, pady=5)
    label_fecha_fin_seleccionada_dep = ttk.Label(frame_filtros, text="Fin: --", style="CustomLabel.TLabel")
    label_fecha_fin_seleccionada_dep.grid(row=1, column=5, padx=5, pady=5, sticky="w")

    # --- Filtro por Stock Dinámico ---
    label_stock = ttk.Label(frame_filtros, text="Filtrar por Stock:", style="CustomLabel.TLabel")
    label_stock.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    opciones_stock = ["Todos", "Bajo Stock (<= 2)", "Stock Medio (3-10)", "Stock Alto (>= 11)"]
    stock_seleccionado = ttk.Combobox(frame_filtros, values=opciones_stock, style="TCombobox", width=25)
    stock_seleccionado.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    stock_seleccionado.set("Todos")

   

    
    global tabla_reporte
    tabla_reporte = ttk.Treeview(frame_tabla, style="Grid.Treeview")
    tabla_reporte.pack(fill="both", expand=True)

    def limpiar_tabla_reporte():
        tabla_reporte.delete(*tabla_reporte.get_children())

    boton_limpiar = ttk.Button(frame_tabla, text="Limpiar", command=limpiar_tabla_reporte, style="Small.TButton")
    boton_limpiar.pack(side="bottom", anchor="se", padx=10, pady=10) # Abajo a la derecha

    def generar_reporte():
        categoria = categoria_seleccionada.get()
        departamento = departamento_seleccionado.get()
        fecha_inicio_cat_str = fecha_inicio_cat.get()
        fecha_fin_cat_str = fecha_fin_cat.get()
        fecha_inicio_dep_str = fecha_inicio_dep.get()
        fecha_fin_dep_str = fecha_fin_dep.get()
        stock = stock_seleccionado.get() # Obtener el valor del Combobox de stock

        if departamento != "Todos":
            generar_reporte_departamento(departamento, categoria, fecha_inicio_dep_str, fecha_fin_dep_str, tabla_reporte, ventana_reporte, stock)
        else:
            generar_reporte_consumo_lapso_filtrado(categoria, fecha_inicio_cat_str, fecha_fin_cat_str, departamento, stock, tabla_reporte, ventana_reporte)

    boton_generar_filtrado = ttk.Button(frame_filtros, text="Generar Reporte Filtrado", command=generar_reporte)
    boton_generar_filtrado.grid(row=3, column=0, columnspan=6, pady=10)

    boton_pdf = ttk.Button(main_frame, text="Exportar a PDF", command=lambda: exportar_tabla_pdf(tabla_reporte))
    boton_pdf.grid(row=2, column=0, pady=10)
    boton_pdf.anchor(tk.CENTER)

    # Configuración de pesos para el frame de filtros para que se expanda con la ventana
    for i in range(6):
        frame_filtros.grid_columnconfigure(i, weight=1)

    # Configuración de pesos para el frame de la tabla para que se expanda
    frame_tabla.grid_columnconfigure(0, weight=1)

def generar_reporte_consumo_lapso_filtrado(categoria_filtro, fecha_inicio_str, fecha_fin_str, departamento, stock_filtro_texto, tabla, ventana):
    """Genera un reporte de consumo por lapso, filtrado por categoría, departamento y stock."""
    global salidas_departamentos
    tabla.delete(*tabla.get_children())

    fecha_inicio = None
    fecha_fin = None
    lapso_texto = ""
    stock_filtro_condicion = None

    if stock_filtro_texto == "Bajo Stock (<= 2)":
        stock_filtro_condicion = lambda stock: stock <= 2
    elif stock_filtro_texto == "Stock Alto (>= 11)":
        stock_filtro_condicion = lambda stock: stock >= 11
    elif stock_filtro_texto == "Stock Medio (3-10)":
        stock_filtro_condicion = lambda stock: 3 <= stock <= 10

    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            lapso_texto = f"{fecha_inicio.strftime('%Y-%m-%d')} al {fecha_fin.strftime('%Y-%m-%d')}"

            tabla["columns"] = ("Categoría", "Producto", "Cantidad Consumida", "Lapso", "Stock Actual")
            tabla.heading("#1", text="Categoría")
            tabla.column("#1", minwidth=100, stretch=tk.YES)
            tabla.heading("#2", text="Producto")
            tabla.column("#2", minwidth=150, stretch=tk.YES)
            tabla.heading("#3", text="Cantidad Consumida")
            tabla.column("#3", minwidth=100, stretch=tk.YES)
            tabla.heading("#4", text="Lapso")
            tabla.column("#4", minwidth=200, stretch=tk.YES)
            tabla.heading("#5", text="Stock Actual")
            tabla.column("#5", minwidth=100, stretch=tk.YES)

            consumo_por_producto = {}
            for salida in salidas_departamentos:
                try:
                    fecha_salida = datetime.datetime.strptime(salida["fecha"], "%Y-%m-%d").date()
                    producto_salida = salida["producto"]
                    cantidad_salida = salida["cantidad"]
                    categoria_producto = inventario.get(producto_salida, {}).get("categoria")
                    stock_actual = inventario.get(producto_salida, {}).get("stock", 0)

                    if categoria_filtro != "Todas" and categoria_filtro != categoria_producto:
                        continue
                    if departamento != "Todos" and departamento != salida.get("destino", "N/A"):
                        continue
                    if fecha_inicio and fecha_salida < fecha_inicio:
                        continue
                    if fecha_fin and fecha_salida > fecha_fin:
                        continue
                    consumo_por_producto[producto_salida] = consumo_por_producto.get(producto_salida, 0) + int(cantidad_salida)

                except ValueError:
                    print(f"Error al procesar fecha de salida: {salida.get('fecha')}")

            for producto, cantidad in consumo_por_producto.items():
                categoria_prod = inventario.get(producto, {}).get("categoria", "N/A")
                stock_prod = inventario.get(producto, {}).get("stock", "N/A")
                if stock_filtro_texto == "Todos" or (stock_filtro_condicion and stock_filtro_condicion(stock_prod)):
                    tabla.insert("", tk.END, values=(categoria_prod, producto, cantidad, lapso_texto, stock_prod))

        except ValueError:
            messagebox.showerror("Error de Fecha", "Formato de fecha incorrecto.", parent=ventana)
            return

    else:
        tabla["columns"] = ("Categoría", "Producto", "Stock", "Unidad Medida")
        tabla.heading("#1", text="Categoría")
        tabla.column("#1", minwidth=100, stretch=tk.YES)
        tabla.heading("#2", text="Producto")
        tabla.column("#2", minwidth=150, stretch=tk.YES)
        tabla.heading("#3", text="Stock")
        tabla.column("#3", minwidth=70, stretch=tk.YES)
        tabla.heading("#4", text="Unidad Medida")
        tabla.column("#4", minwidth=100, stretch=tk.YES)

        for producto_inventario, datos in inventario.items():
            if categoria_filtro == "Todas" or datos["categoria"] == categoria_filtro:
                if departamento == "Todos" or datos.get("departamento", "N/A") == departamento:
                    stock_actual = datos.get("stock", 0)
                    if stock_filtro_texto == "Todos" or (stock_filtro_condicion and stock_filtro_condicion(stock_actual)):
                        tabla.insert("", tk.END, values=(datos["categoria"], producto_inventario, datos["stock"], datos["unidad_medida"]))

def generar_reporte_departamento(departamento_filtro, categoria_filtro, fecha_inicio_str, fecha_fin_str, tabla, ventana, stock_filtro_texto):
    """Genera un reporte de consumo por departamento y lapso, filtrado por categoría y stock."""
    global salidas_departamentos
    tabla.delete(*tabla.get_children())

    fecha_inicio = None
    fecha_fin = None
    lapso_texto = ""
    stock_filtro_condicion = None

    if stock_filtro_texto == "Bajo Stock (<= 2)":
        stock_filtro_condicion = lambda stock: stock <= 2
    elif stock_filtro_texto == "Stock Alto (>= 11)":
        stock_filtro_condicion = lambda stock: stock >= 11
    elif stock_filtro_texto == "Stock Medio (3-10)":
        stock_filtro_condicion = lambda stock: 3 <= stock <= 10

    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            lapso_texto = f"{fecha_inicio.strftime('%Y-%m-%d')} al {fecha_fin.strftime('%Y-%m-%d')}"

            # --- Reporte de Salidas por Departamento y Lapso (incluyendo Producto y filtro de stock) ---
            tabla["columns"] = ("Departamento", "Producto", "Categoría", "Cantidad", "Lapso", "Stock Actual")
            tabla.heading("#1", text="Departamento")
            tabla.column("#1", minwidth=150, stretch=tk.YES)
            tabla.heading("#2", text="Producto")
            tabla.column("#2", minwidth=150, stretch=tk.YES)
            tabla.heading("#3", text="Categoría")
            tabla.column("#3", minwidth=100, stretch=tk.YES)
            tabla.heading("#4", text="Cantidad")
            tabla.column("#4", minwidth=100, stretch=tk.YES)
            tabla.heading("#5", text="Lapso")  # Cambiamos "Fecha Salida" por "Lapso"
            tabla.column("#5", minwidth=200, stretch=tk.YES)
            tabla.heading("#6", text="Stock Actual")
            tabla.column("#6", minwidth=100, stretch=tk.YES)

            for salida in salidas_departamentos:
                try:
                    fecha_salida_obj = datetime.datetime.strptime(salida["fecha"], "%Y-%m-%d").date()
                    producto_salida = salida["producto"]
                    cantidad_salida = salida["cantidad"]
                    categoria_producto = inventario.get(producto_salida, {}).get("categoria")
                    departamento_salida = salida.get("destino")
                    stock_actual = inventario.get(producto_salida, {}).get("stock", 0)

                    if departamento_salida == departamento_filtro:
                        if categoria_filtro == "Todas" or categoria_producto == categoria_filtro:
                            if fecha_inicio and fecha_salida_obj < fecha_inicio:
                                continue
                            if fecha_fin and fecha_salida_obj > fecha_fin:
                                continue
                            if stock_filtro_texto == "Todos" or (stock_filtro_condicion and stock_filtro_condicion(stock_actual)):
                                tabla.insert("", tk.END, values=(departamento_salida, producto_salida, categoria_producto, cantidad_salida, lapso_texto, stock_actual)) # Usamos lapso_texto aquí

                except ValueError:
                    print(f"Error al procesar fecha de salida: {salida.get('fecha')}")

        except ValueError:
            messagebox.showerror("Error de Fecha", "Formato de fecha incorrecto.", parent=ventana)
            return

    else:
        # --- Reporte de Consumo Total por Departamento (sin lapso, incluyendo Producto y filtro de stock) ---
        tabla["columns"] = ("Departamento", "Producto", "Categoría", "Cantidad Consumida", "Stock Actual")
        tabla.heading("#1", text="Departamento")
        tabla.column("#1", minwidth=150, stretch=tk.YES)
        tabla.heading("#2", text="Producto")
        tabla.column("#2", minwidth=150, stretch=tk.YES)
        tabla.heading("#3", text="Categoría")
        tabla.column("#3", minwidth=150, stretch=tk.YES)
        tabla.heading("#4", text="Cantidad Consumida")
        tabla.column("#4", minwidth=150, stretch=tk.YES)
        tabla.heading("#5", text="Stock Actual")
        tabla.column("#5", minwidth=100, stretch=tk.YES)

        consumo_por_producto = {}
        for salida in salidas_departamentos:
            departamento_salida = salida.get("destino")
            categoria_producto = inventario.get(salida["producto"], {}).get("categoria", "N/A")
            producto_salida = salida["producto"]
            cantidad_salida = salida["cantidad"]
            stock_actual = inventario.get(salida["producto"], {}).get("stock", 0)

            if departamento_salida == departamento_filtro:
                try:
                    cantidad_salida_int = int(cantidad_salida)
                    if producto_salida not in consumo_por_producto:
                        consumo_por_producto[producto_salida] = {"categoria": categoria_producto, "cantidad": 0, "stock": stock_actual}
                    consumo_por_producto[producto_salida]["cantidad"] += cantidad_salida_int
                except ValueError:
                    print(f"Error: La cantidad de salida '{cantidad_salida}' no es un número entero.")
                    continue

        for producto, datos_consumo in consumo_por_producto.items():
            if stock_filtro_texto == "Todos" or (stock_filtro_condicion and stock_filtro_condicion(datos_consumo["stock"])):
                tabla.insert("", tk.END, values=(departamento_filtro, producto, datos_consumo["categoria"], datos_consumo["cantidad"], datos_consumo["stock"]))


class PDFConMembrete(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.membrete_superior_altura = 20
        self.membrete_inferior_altura = 15
        self.margen_horizontal = 5  # Reducimos aún más los márgenes horizontales
        self.espacio_entre_tabla_y_membrete = 15
        self.altura_encabezados = 10
        self.altura_fila = 7  # Reducimos ligeramente la altura de la fila
        self.y_despues_membrete_superior = 5 + self.membrete_superior_altura + self.espacio_entre_tabla_y_membrete
        self.filas_por_pagina = self.calcular_filas_por_pagina()

    def calcular_filas_por_pagina(self):
        altura_disponible = self.h - self.t_margin - self.b_margin - self.membrete_inferior_altura - self.y_despues_membrete_superior - self.altura_encabezados - 5
        return int(altura_disponible / self.altura_fila)

    def header(self):
        self.set_y(5)
        ancho_disponible = self.w - (self.l_margin + self.r_margin)
        try:
            self.image(
                "C:/Users/monster/Desktop/src/server/routes/imagenes/OFICIOS-CORPOANDES-1.png",
                x=self.l_margin,
                y=self.get_y(),
                w=ancho_disponible,
                h=self.membrete_superior_altura,
            )
        except FileNotFoundError:
            self.set_font("Arial", 'B', 10)
            self.cell(0, 10, "¡Error: Membrete superior no encontrado!", ln=1, align='C')

    def footer(self):
        self.set_y(-1 * (self.membrete_inferior_altura + 10))
        self.set_x(self.margen_horizontal)
        self.set_font("Arial", 'I', 8)
        self.cell(
            0,
            5,
            "Av. Los Próceres Entrada al Parque La Isla Edificio CORPOANDES Mérida.",
            ln=1,
            align="C",
        )
        self.cell(
            0, 5, "Teléfonos: (0274) 2440511-2446293. Fax (0274) 2440451", ln=1, align="C"
        )
        self.cell(
            0, 5, "Correo corpoandespresidencia@gmail.com", ln=1, align="C"
        )

    def print_titulo(self):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "Reporte", ln=1, align='C')
        self.set_font("Arial", size=10)

    def print_encabezados_tabla(self, headers, col_widths, x_start):
        self.set_x(x_start)
        self.set_font("Arial", 'B', 8)  # Reducimos también la fuente del encabezado
        self.set_fill_color(200, 220, 255)
        self.set_text_color(0, 0, 0)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, txt=header, border=1, align='C', fill=True)  # Reducimos la altura del encabezado
        self.ln()


def exportar_tabla_pdf(tabla_treeview):
    """Exporta los datos del Treeview a un PDF con membrete según el diseño."""

    filename = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        title="Guardar reporte como PDF",
    )
    if not filename:
        return

    pdf = PDFConMembrete(orientation="L", unit="mm", format="A4")
    pdf.set_margins(left=5, top=20, right=5)
    pdf.set_auto_page_break(auto=False, margin=0)
    pdf.set_font("Arial", size=7)
    pdf.add_page()

    # --- Configuración de Anchos de Columna Dinámica Basada en Encabezados Comunes ---
    cols = tabla_treeview["columns"]
    headers = [tabla_treeview.heading(col)["text"] for col in cols]
    available_width = pdf.w - pdf.l_margin - pdf.r_margin
    lapso_width_fixed = 50  # Mantenemos un ancho fijo para "Lapso"
    col_widths = []

    new_headers = list(headers)
    if "Stock Actual" in new_headers:
        index_stock = new_headers.index("Stock Actual")
        new_headers[index_stock] = "Stock"
    if "Cantidad Consumida" in new_headers:
        index_cantidad = new_headers.index("Cantidad Consumida")
        new_headers[index_cantidad] = "Cantidad"

    if tuple(new_headers) == ("Departamento", "Producto", "Categoría", "Cantidad", "Lapso", "Stock"):
        col_widths = [
            available_width * 0.15,  # Departamento
            available_width * 0.30,  # Producto
            available_width * 0.15,  # Categoría
            available_width * 0.10,  # Cantidad
            lapso_width_fixed,       # Lapso
            available_width * 0.10,  # Stock
        ]
    elif tuple(new_headers) == ("Categoría", "Producto", "Cantidad", "Lapso", "Stock"):
        remaining_width = available_width - lapso_width_fixed
        col_widths = [
            remaining_width * 0.15,  # Categoría (Mismo ancho que Departamento)
            remaining_width * 0.30,  # Producto (Mismo ancho)
            remaining_width * 0.10,  # Cantidad (Mismo ancho)
            lapso_width_fixed,       # Lapso (Mismo ancho fijo)
            remaining_width * 0.10,  # Stock (Mismo ancho)
        ]
    else:
        # Configuración de anchos por defecto si no coinciden los encabezados esperados
        col_widths = [available_width / len(headers)] * len(headers)

    total_width = sum(col_widths)
    x_start = (pdf.w - total_width) / 2
    row_height = 7

    # --- Iterar sobre los Datos e Imprimir Filas por página ---
    pdf.set_text_color(0, 0, 0)
    items = tabla_treeview.get_children()
    num_items = len(items)
    filas_impresas = 0

    while filas_impresas < num_items:
        pdf.set_y(pdf.y_despues_membrete_superior)
        pdf.print_titulo()
        pdf.print_encabezados_tabla(new_headers, col_widths, x_start)

        for i in range(filas_impresas, min(filas_impresas + pdf.filas_por_pagina, num_items)):
            child = items[i]
            pdf.set_x(x_start)
            if i % 2 == 0:
                pdf.set_fill_color(240, 240, 240)
            else:
                pdf.set_fill_color(255, 255, 255)
            for j, col in enumerate(cols):
                value = tabla_treeview.set(child, col)
                pdf.cell(col_widths[j], row_height, txt=str(value), border=1, align='L', fill=True)
            pdf.ln()
        filas_impresas += pdf.filas_por_pagina
        if filas_impresas < num_items:
            pdf.add_page()

    pdf.output(filename, "F")
    messagebox.showinfo("Exportar a PDF", "Reporte exportado exitosamente a PDF.", parent=tabla_treeview)
















    


                            # Función para configurar la aplicación
def configuracion():
    """Abre una ventana de configuración para ajustar unidades de medida y umbrales."""
    ventana_config = tk.Toplevel(ventana)
    ventana_config.title("Configuración")
    ventana_config.configure(bg="#A9A9A9")  # Fondo gris oscuro medio

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana_config)
    style.theme_use('clam')
    style.configure("CustomLabel.TLabel", foreground="#ffffff", background="#A9A9A9", font=("Segoe UI", 10, "bold"))
    style.configure("CustomEntry.TEntry", foreground="#000000", background="#ffffff", insertcolor="#000000", font=("Segoe UI", 10))
    style.configure("TCombobox", foreground="#000000", background="#ffffff", font=("Segoe UI", 10))
    style.configure("TCheckbutton", foreground="#ffffff", background="#A9A9A9", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("TFrame", background="#A9A9A9") # Estilo para los frames

    # Variables para almacenar la configuración
    formato_fecha_var = tk.StringVar(ventana_config)
    notificaciones_var = tk.IntVar(ventana_config)
    tema_color_var = tk.StringVar(ventana_config)

    # Cargar configuración actual (si existe)
    try:
        with open("configuracion.json", "r") as archivo_config:
            configuracion = json.load(archivo_config)
            formato_fecha_var.set(configuracion.get("formato_fecha", "YYYY-MM-DD"))
            notificaciones_var.set(configuracion.get("notificaciones", 0))
            tema_color_var.set(configuracion.get("tema_color", "Claro"))
    except FileNotFoundError:
        # Configuración predeterminada si no existe el archivo
        formato_fecha_var.set("YYYY-MM-DD")
        notificaciones_var.set(0)
        tema_color_var.set("Claro")

    # Marco principal para centrar el contenido
    main_frame = ttk.Frame(ventana_config, style="TFrame")
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)
    main_frame.grid_columnconfigure(0, weight=1)

    # Marco para los controles de configuración
    config_frame = ttk.Frame(main_frame, style="TFrame")
    config_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    config_frame.columnconfigure(0, weight=1)
    config_frame.columnconfigure(1, weight=1)

    # Interfaz de configuración
    label_formato_fecha = ttk.Label(config_frame, text="Formato de Fecha:", style="CustomLabel.TLabel")
    label_formato_fecha.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    formatos_fecha = ["YYYY-MM-DD", "DD-MM-YYYY", "MM/DD/YYYY"]
    combo_formato_fecha = ttk.Combobox(config_frame, textvariable=formato_fecha_var, values=formatos_fecha, style="TCombobox")
    combo_formato_fecha.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    check_notificaciones = ttk.Checkbutton(config_frame, text="Notificaciones de Bajo Stock", variable=notificaciones_var, style="TCheckbutton")
    check_notificaciones.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    label_tema_color = ttk.Label(config_frame, text="Tema de Color:", style="CustomLabel.TLabel")
    label_tema_color.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    temas_color = ["Claro", "Oscuro", "Azul", "Verde", "Rojo", "Amarillo", "Morado"]
    combo_tema_color = ttk.Combobox(config_frame, textvariable=tema_color_var, values=temas_color, style="TCombobox")
    combo_tema_color.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    # Marco para los botones de copia de seguridad y restaurar
    backup_restore_frame = ttk.Frame(main_frame, style="TFrame")
    backup_restore_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
    backup_restore_frame.columnconfigure(0, weight=1)
    backup_restore_frame.columnconfigure(1, weight=1)

    # Botón "Copia de Seguridad"
    def realizar_copia_seguridad():
        try:
            fecha_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_copia_seguridad = f"inventario_backup_{fecha_hora}.json"
            shutil.copy2("inventario.json", nombre_copia_seguridad)
            messagebox.showinfo("Copia de Seguridad", f"Copia de seguridad creada: {nombre_copia_seguridad}", parent=ventana_config)
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la copia de seguridad: {e}", parent=ventana_config)

    btn_copia_seguridad = ttk.Button(backup_restore_frame, text="Copia de Seguridad", command=realizar_copia_seguridad)
    btn_copia_seguridad.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

    # Botón "Restaurar"
    def restaurar_copia_seguridad():
        try:
            archivos_copia_seguridad = [f for f in os.listdir() if f.startswith("inventario_backup_")]
            if not archivos_copia_seguridad:
                messagebox.showerror("Error", "No se encontraron copias de seguridad.", parent=ventana_config)
                return

            ventana_restaurar = tk.Toplevel(ventana_config)
            ventana_restaurar.title("Restaurar Copia de Seguridad")
            ventana_restaurar.configure(bg="#A9A9A9")

            label_seleccionar = ttk.Label(ventana_restaurar, text="Seleccione la copia de seguridad a restaurar:", style="CustomLabel.TLabel")
            label_seleccionar.pack(pady=5, padx=10)

            lista_copias_seguridad = tk.Listbox(ventana_restaurar, bg="#ffffff", fg="#000000")
            for archivo in archivos_copia_seguridad:
                lista_copias_seguridad.insert(tk.END, archivo)
            lista_copias_seguridad.pack(padx=10, pady=5, fill="both", expand=True)

            botones_restaurar_eliminar_frame = ttk.Frame(ventana_restaurar, style="TFrame")
            botones_restaurar_eliminar_frame.pack(pady=5, padx=10)
            botones_restaurar_eliminar_frame.columnconfigure(0, weight=1)
            botones_restaurar_eliminar_frame.columnconfigure(1, weight=1)

            def restaurar_seleccionada():
                seleccion = lista_copias_seguridad.curselection()
                if seleccion:
                    archivo_seleccionado = lista_copias_seguridad.get(seleccion[0])
                    shutil.copy2(archivo_seleccionado, "inventario.json")
                    messagebox.showinfo("Restaurar", f"Datos restaurados desde: {archivo_seleccionado}", parent=ventana_restaurar)
                    ventana_restaurar.destroy()
                else:
                    messagebox.showerror("Error", "Seleccione una copia de seguridad.", parent=ventana_restaurar)

            btn_restaurar_seleccionada = ttk.Button(botones_restaurar_eliminar_frame, text="Restaurar", command=restaurar_seleccionada)
            btn_restaurar_seleccionada.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            def eliminar_seleccionada():
                seleccion = lista_copias_seguridad.curselection()
                if seleccion:
                    archivo_seleccionado = lista_copias_seguridad.get(seleccion[0])
                    os.remove(archivo_seleccionado)
                    lista_copias_seguridad.delete(seleccion[0])
                    messagebox.showinfo("Eliminar", f"Copia de seguridad '{archivo_seleccionado}' eliminada.", parent=ventana_restaurar)
                else:
                    messagebox.showerror("Error", "Seleccione una copia de seguridad.", parent=ventana_restaurar)

            btn_eliminar_seleccionada = ttk.Button(botones_restaurar_eliminar_frame, text="Eliminar", command=eliminar_seleccionada)
            btn_eliminar_seleccionada.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar la copia de seguridad: {e}", parent=ventana_config)

    btn_restaurar = ttk.Button(backup_restore_frame, text="Restaurar", command=restaurar_copia_seguridad)
    btn_restaurar.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

    # Botón "Gestión de Usuarios"
    def gestionar_usuarios():
        ventana_usuarios = tk.Toplevel(ventana_config)
        ventana_usuarios.title("Gestión de Usuarios")
        ventana_usuarios.configure(bg="#A9A9A9")

        label_usuarios = ttk.Label(ventana_usuarios, text="Usuarios:", style="CustomLabel.TLabel")
        label_usuarios.pack(pady=5, padx=10)

        lista_usuarios = tk.Listbox(ventana_usuarios, bg="#ffffff", fg="#000000")
        for usuario in usuarios:
            lista_usuarios.insert(tk.END, usuario)
        lista_usuarios.pack(padx=10, pady=5, fill="both", expand=True)

        frame_crear_usuario = ttk.Frame(ventana_usuarios, style="TFrame")
        frame_crear_usuario.pack(pady=5, padx=10, fill="x")
        frame_crear_usuario.columnconfigure(1, weight=1)

        label_nombre = ttk.Label(frame_crear_usuario, text="Nombre:", style="CustomLabel.TLabel")
        label_nombre.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        entry_nombre = ttk.Entry(frame_crear_usuario, style="CustomEntry.TEntry")
        entry_nombre.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        label_contrasena = ttk.Label(frame_crear_usuario, text="Contraseña:", style="CustomLabel.TLabel")
        label_contrasena.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        entry_contrasena = ttk.Entry(frame_crear_usuario, show="*", style="CustomEntry.TEntry")
        entry_contrasena.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        def verificar_codigo_administrador(codigo):
            """Verifica si el código de administrador es correcto."""
            return hashlib.sha256(codigo.encode()).hexdigest() == clave_admin

        def crear_usuario():
            nombre = entry_nombre.get()
            contrasena = entry_contrasena.get()
            codigo_admin = simpledialog.askstring("Código de Administrador", "Ingrese el código de administrador:", parent=ventana_usuarios)
            if codigo_admin and verificar_codigo_administrador(codigo_admin):
                if nombre and contrasena:
                    usuarios[nombre] = hashlib.sha256(contrasena.encode()).hexdigest()
                    lista_usuarios.insert(tk.END, nombre)
                    messagebox.showinfo("Usuario Creado", f"Usuario '{nombre}' creado.", parent=ventana_usuarios)
                    entry_nombre.delete(0, tk.END)
                    entry_contrasena.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Ingrese nombre y contraseña.", parent=ventana_usuarios)
            else:
                messagebox.showerror("Error", "Código de administrador incorrecto.", parent=ventana_usuarios)

        btn_crear_usuario = ttk.Button(ventana_usuarios, text="Crear Usuario", command=crear_usuario)
        btn_crear_usuario.pack(pady=5, padx=10, fill="x")

        def eliminar_usuario():
            seleccion = lista_usuarios.curselection()
            if seleccion:
                usuario_seleccionado = lista_usuarios.get(seleccion[0])
                del usuarios[usuario_seleccionado]
                lista_usuarios.delete(seleccion[0])
                messagebox.showinfo("Usuario Eliminado", f"Usuario '{usuario_seleccionado}' eliminado.", parent=ventana_usuarios)
            else:
                messagebox.showerror("Error", "Seleccione un usuario.", parent=ventana_usuarios)

        btn_eliminar_usuario = ttk.Button(ventana_usuarios, text="Eliminar Usuario", command=eliminar_usuario)
        btn_eliminar_usuario.pack(pady=5, padx=10, fill="x")

    btn_gestion_usuarios = ttk.Button(main_frame, text="Gestión de Usuarios", command=gestionar_usuarios)
    btn_gestion_usuarios.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

    # Botón "Aceptar" al final y separado
    def guardar_configuracion():
        configuracion = {
            "formato_fecha": formato_fecha_var.get(),
            "notificaciones": notificaciones_var.get(),
            "tema_color": tema_color_var.get(),
        }
        with open("configuracion.json", "w") as archivo_config:
            json.dump(configuracion, archivo_config)
        messagebox.showinfo("Configuración Guardada", "La configuración se ha guardado correctamente.", parent=ventana_config)
        ventana_config.destroy()
        aplicar_tema_color(tema_color_var.get())  # Aplicar el tema de color seleccionado
        if notificaciones_var.get():
            mostrar_notificacion_bajo_stock()  # Mostrar notificación si las notificaciones están activadas

    btn_aceptar = ttk.Button(main_frame, text="Aceptar", command=guardar_configuracion)
    btn_aceptar.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

# Función para aplicar el tema de color
def aplicar_tema_color(tema):
    """Aplica el tema de color seleccionado a la interfaz."""
    colores_tema = {
        "Claro": {"bg": "white", "fg": "black"},
        "Oscuro": {"bg": "#333333", "fg": "white"},
        "Azul": {"bg": "#E8F5E9", "fg": "black"},
        "Verde": {"bg": "#E8F5E9", "fg": "black"},
        "Rojo": {"bg": "#FFEBEE", "fg": "black"},
        "Amarillo": {"bg": "#FFFDE7", "fg": "black"},
        "Morado": {"bg": "#F3E5F5", "fg": "black"}
    }
    colores = colores_tema.get(tema, colores_tema["Claro"])  # Usar "Claro" como predeterminado

    ventana.config(bg=colores["bg"])
    for widget in ventana.winfo_children():
        widget.config(bg=colores["bg"], fg=colores["fg"])

def mostrar_notificacion_bajo_stock():
    """Muestra una notificación de advertencia general sobre bajo stock."""
    global ventana  # Hacer la variable 'ventana' global
    umbral_stock_minimo = 1  # Ajusta este valor según tus necesidades
    productos_bajo_stock = []
    for producto, datos in inventario.items():
        if datos["stock"] < umbral_stock_minimo:
            productos_bajo_stock.append(producto)

    if productos_bajo_stock:
        mensaje = "¡Advertencia! Hay productos con bajo stock"

        # Crear ventana de notificación flotante
        ventana_notificacion = tk.Toplevel(ventana)
        ventana_notificacion.title("Advertencia: Bajo Stock")
        ventana_notificacion.geometry("+{}+0".format(ventana.winfo_screenwidth() - 300))  # Posición superior derecha
        ventana_notificacion.overrideredirect(True)  # Eliminar bordes y barra de título
        ventana_notificacion.configure(bg="yellow")

        # Etiqueta con el mensaje
        label_mensaje = ttk.Label(ventana_notificacion, text=mensaje, background="yellow", foreground="black", padding=10, font=("Segoe UI", 10, "bold"))
        label_mensaje.pack()

        # Botón para cerrar la notificación
        boton_cerrar = ttk.Button(ventana_notificacion, text="Cerrar", command=ventana_notificacion.destroy)
        boton_cerrar.pack(pady=5)

        # Destruir la notificación después de un tiempo (opcional)
        ventana_notificacion.after(5000, ventana_notificacion.destroy)

def importar_datos():
    """Importa datos desde el archivo JSON y actualiza el inventario."""
    global inventario, entradas_departamentos  # Asegurarse de que estamos usando las variables globales

    try:
        with open("inventario.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        inventario = {}
        for producto, datos_producto in datos.get("inventario", {}).items():
            try:
                fecha_entrada = datetime.date.fromisoformat(datos_producto["fecha_entrada"]) if datos_producto["fecha_entrada"] and datos_producto["fecha_entrada"] != 'None' else None
                fecha_salida = datetime.date.fromisoformat(datos_producto["fecha_salida"]) if datos_producto["fecha_salida"] and datos_producto["fecha_salida"] != 'None' else None
            except ValueError:
                messagebox.showerror("Error", f"Fecha inválida para el producto {producto}. Se omitirá.")
                continue  # Saltar al siguiente producto
            inventario[producto] = {
                **datos_producto,
                "fecha_entrada": fecha_entrada,
                "fecha_salida": fecha_salida
            }
        # Asegurarse de que entradas_departamentos sea una lista
        entradas_departamentos = datos.get("entradas_departamentos", [])
        if not isinstance(entradas_departamentos, list): #Verificamos si es lista, sino se asigna una lista vacía.
            entradas_departamentos = []

        messagebox.showinfo("Importar Datos", f"Se importaron {len(inventario)} productos.")

    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el archivo inventario.json.")
    except json.JSONDecodeError as e:
        messagebox.showerror("Error", f"Error al cargar los datos: Formato JSON incorrecto.\nDetalles: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al importar los datos: {e}")

def exportar_datos():
    """Exporta los datos del inventario a un archivo CSV."""
    global inventario  # Asegurarse de que estamos usando la variable global

    try:
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")])

        if archivo:
            with open(archivo, 'w', newline='', encoding='utf-8') as file:
                campos = ["producto", "categoria", "destino_entrada", "entrada", "salida", "stock", "unidad_medida", "fecha_entrada", "fecha_salida", "destino_salida"]
                escritor_csv = csv.DictWriter(file, fieldnames=campos)
                escritor_csv.writeheader()

                for producto, datos in inventario.items():
                    # Verificar si las fechas son válidas antes de formatearlas
                    fecha_entrada = datos["fecha_entrada"]
                    fecha_salida = datos["fecha_salida"]

                    if isinstance(fecha_entrada, datetime.date):
                        fecha_entrada_str = fecha_entrada.strftime("%Y-%m-%d")
                    else:
                        fecha_entrada_str = "Fecha no disponible"  # O algún otro valor predeterminado

                    if isinstance(fecha_salida, datetime.date):
                        fecha_salida_str = fecha_salida.strftime("%Y-%m-%d")
                    else:
                        fecha_salida_str = "Fecha no disponible"  # O algún otro valor predeterminado

                    fila = {
                        "producto": producto,
                        "categoria": datos["categoria"],
                        "destino_entrada": datos["destino_entrada"],
                        "entrada": datos["entrada"],
                        "salida": datos["salida"],
                        "stock": datos["stock"],
                        "unidad_medida": datos["unidad_medida"],
                        "fecha_entrada": fecha_entrada_str,
                        "fecha_salida": fecha_salida_str,
                        "destino_salida": datos["destino_salida"]
                    }
                    escritor_csv.writerow(fila)

            messagebox.showinfo("Exportar Datos", f"Se exportaron {len(inventario)} productos.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al exportar los datos: {e}")

def guardar_como():
    """Permite al usuario elegir la ubicación y el nombre del archivo para guardar."""
    archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivos JSON", "*.json")])
    if archivo:
        guardar_datos(archivo)
            














                                    #Funcion de Mostrar el Menu


def mostrar_menu():
    """Muestra el menú principal con la estructura original y colores oscuros."""
    global ventana

    ventana = tk.Tk()
    ventana.title("Menú Principal")
    ventana.configure(bg="#263238")

    # --- Estilos ttk Personalizados ---
    style = ttk.Style(ventana)
    style.theme_use('clam')

    style.configure("MenuButtonDarkGrid.TButton",
                    foreground="#eceff1",
                    background="#37474F",
                    font=("Segoe UI", 12, "bold"),
                    padding=15,
                    relief="raised",
                    anchor="center")
    style.map("MenuButtonDarkGrid.TButton",
              background=[('active', '#455a64')],
              foreground=[('active', '#fff')])

    # --- Cargar Logos ---
    try:
        logo_agregar = tk.PhotoImage(file="C:/Users/monster/Desktop/src/server/routes/imagenes/agregar-producto.png").subsample(3, 3)
        logo_salida = tk.PhotoImage(file="C:/Users/monster/Desktop/src/server/routes/imagenes/espera.png").subsample(3, 3)
        logo_mostrar = tk.PhotoImage(file="C:/Users/monster/Desktop/src/server/routes/imagenes/inventario.png").subsample(3, 3)
        logo_consumo = tk.PhotoImage(file="C:/Users/monster/Desktop/src/server/routes/imagenes/consumo.png").subsample(3, 3)
    except tk.TclError as e:
        print(f"Error al cargar imágenes: {e}")
        logo_agregar = None
        logo_salida = None
        logo_mostrar = None
        logo_consumo = None

    # --- Barra de Menú Superior  ---
    menu_principal = tk.Menu(ventana)
    ventana.config(menu=menu_principal)
    menu_archivo = tk.Menu(menu_principal, tearoff=0)
    menu_principal.add_cascade(label="Archivo", menu=menu_archivo)
    menu_archivo.add_command(label="Guardar", command=guardar_datos)
    menu_archivo.add_command(label="Guardar como...", command=guardar_como)
    menu_archivo.add_command(label="Importar", command=importar_datos)
    menu_archivo.add_command(label="Exportar", command=exportar_datos)
    menu_archivo.add_separator()
    menu_archivo.add_command(label="Salir", command=ventana.destroy)

    menu_reportes = tk.Menu(menu_principal, tearoff=0)
    menu_principal.add_cascade(label="Reportes", menu=menu_reportes)
    menu_reportes.add_command(label="Productos con bajo stock", command=generar_reporte_bajo_stock)
    menu_reportes.add_command(label="Historial de entradas", command=generar_reporte_entradas)
    menu_reportes.add_command(label="Historial de salidas", command=generar_reporte_salidas)
    menu_reportes.add_command(label="Historial de salidas en espera", command=generar_reporte_salidas_espera)
    menu_reportes.add_command(label="Reporte completo", command=ventana_reportes)

    menu_configuracion = tk.Menu(menu_principal, tearoff=0)
    menu_principal.add_cascade(label="Configuración", menu=menu_configuracion)
    menu_configuracion.add_command(label="Ajustes generales", command=configuracion)

    # --- Crear botones para cada opción con logos encima ---
    boton_agregar = ttk.Button(ventana, text="Agregar producto", image=logo_agregar, compound=tk.TOP, style="MenuButtonDarkGrid.TButton", command=agregar_producto)
    boton_salida = ttk.Button(ventana, text="Realizar salida en espera", image=logo_salida, compound=tk.TOP, style="MenuButtonDarkGrid.TButton", command=realizar_salida)
    boton_mostrar = ttk.Button(ventana, text="Mostrar inventario", image=logo_mostrar, compound=tk.TOP, style="MenuButtonDarkGrid.TButton", command=mostrar_inventario)
    boton_consumo = ttk.Button(ventana, text="Calcular consumo por departamento", image=logo_consumo, compound=tk.TOP, style="MenuButtonDarkGrid.TButton", command=calcular_consumo_departamento)

    # --- Organizar los botones en una cuadrícula ---
    boton_agregar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    boton_salida.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    boton_mostrar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    boton_consumo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    # --- Configurar la expansión de las columnas ---
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_columnconfigure(1, weight=1)

    # Cargar los datos y mostrar la notificación de bajo stock
    cargar_datos()
    mostrar_notificacion_bajo_stock()

    ventana.mainloop()

# --- Ejecución de la aplicación ---
iniciar_sesion()
