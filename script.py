# This is a sample Python script.

import tkinter as tk
from tkinter import messagebox

# Crear ventana principal
root = tk.Tk()
root.title("Control de Edificio")
root.geometry("400x300")

# Funciones básicas para botones (aún no implementadas)
def abrir_inquilinos():
    messagebox.showinfo("Inquilinos", "Aquí iría la gestión de inquilinos.")

def registrar_pago():
    messagebox.showinfo("Pagos", "Aquí iría el registro de pagos.")

def registrar_gasto():
    messagebox.showinfo("Gastos", "Aquí iría el registro de gastos.")

def ver_reporte():
    messagebox.showinfo("Reporte", "Aquí se mostraría el reporte mensual.")

# Etiqueta principal
label = tk.Label(root, text="Panel de Control del Edificio", font=("Helvetica", 16))
label.pack(pady=20)

# Botones
btn_inquilinos = tk.Button(root, text="Inquilinos", width=20, command=abrir_inquilinos)
btn_inquilinos.pack(pady=5)

btn_pagos = tk.Button(root, text="Registrar Pago", width=20, command=registrar_pago)
btn_pagos.pack(pady=5)

btn_gastos = tk.Button(root, text="Registrar Gasto", width=20, command=registrar_gasto)
btn_gastos.pack(pady=5)

btn_reporte = tk.Button(root, text="Ver Reporte", width=20, command=ver_reporte)
btn_reporte.pack(pady=5)

# Ejecutar la ventana
root.mainloop()

import csv
import tkinter as tk
from tkinter import messagebox, Toplevel

def abrir_inquilinos():
    ventana_inquilinos = Toplevel()
    ventana_inquilinos.title("Agregar Inquilino")
    ventana_inquilinos.geometry("300x250")

    # Etiquetas y campos
    tk.Label(ventana_inquilinos, text="Nombre:").pack(pady=5)
    entry_nombre = tk.Entry(ventana_inquilinos)
    entry_nombre.pack()

    tk.Label(ventana_inquilinos, text="Apartamento:").pack(pady=5)
    entry_apto = tk.Entry(ventana_inquilinos)
    entry_apto.pack()

    tk.Label(ventana_inquilinos, text="Renta mensual:").pack(pady=5)
    entry_renta = tk.Entry(ventana_inquilinos)
    entry_renta.pack()

    def guardar_inquilino():
        nombre = entry_nombre.get()
        apto = entry_apto.get()
        renta = entry_renta.get()


if not nombre or not apto or not renta:
    messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
    return

try:
    renta = float(renta)
except ValueError:
    messagebox.showerror("Error", "La renta debe ser un número.")
    return

with open("inquilinos.csv", mode="a", newline="") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow([nombre, apto, renta])

messagebox.showinfo("Guardado", f"Inquilino {nombre} registrado exitosamente.")
ventana_inquilinos.destroy()

tk.Button(ventana_inquilinos, text="Guardar", command=guardar_inquilino).pack(pady=10)



def registrar_pago():
    ventana_pago = Toplevel()
    ventana_pago.title("Registrar Pago")
    ventana_pago.geometry("350x250")

    # Leer inquilinos desde el archivo
    try:
        with open("inquilinos.csv", newline="") as archivo:
            lector = csv.reader(archivo)
            datos_inquilinos = [fila for fila in lector]  # Guardamos nombre, apto, renta
    except FileNotFoundError:
        messagebox.showerror("Error", "No hay inquilinos registrados aún.")
        return

    # Diccionario para acceder rápido a la renta
    mapa_renta = {
        f"{fila[0]} - Apto {fila[1]}": float(fila[2])
        for fila in datos_inquilinos
    }

    lista_inquilinos = list(mapa_renta.keys())

    tk.Label(ventana_pago, text="Seleccionar Inquilino:").pack(pady=5)
    var_inquilino = tk.StringVar(ventana_pago)
    var_inquilino.set(lista_inquilinos[0])  # Primer inquilino como default
    dropdown = tk.OptionMenu(ventana_pago, var_inquilino, *lista_inquilinos)
    dropdown.pack()

    tk.Label(ventana_pago, text="Monto pagado:").pack(pady=5)
    entry_monto = tk.Entry(ventana_pago)
    entry_monto.pack()

    def actualizar_monto(*args):
        inquilino = var_in


def registrar_gasto():
    ventana_gasto = Toplevel()
    ventana_gasto.title("Registrar Gasto")
    ventana_gasto.geometry("350x300")

    # Tipo de gasto
    tk.Label(ventana_gasto, text="Tipo de gasto:").pack(pady=5)
    tipo_var = tk.StringVar()
    tipo_var.set("Servicios Públicos")

    opciones_tipo = ["Servicios Públicos", "Impuestos", "Otros"]
    tk.OptionMenu(ventana_gasto, tipo_var, *opciones_tipo).pack()

    # Descripción del gasto
    tk.Label(ventana_gasto, text="Descripción (opcional):").pack(pady=5)
    entry_desc = tk.Entry(ventana_gasto)
    entry_desc.pack()
 # Monto
    tk.Label(ventana_gasto, text="Monto:").pack(pady=5)
    entry_monto = tk.Entry(ventana_gasto)
    entry_monto.pack()

    def guardar_gasto():
        tipo = tipo_var.get()
        descripcion = entry_desc.get()
        monto = entry_monto.get()
        fecha = datetime.date.today().isoformat()

        if not monto:
            messagebox.showwarning("Faltan datos", "Debes ingresar el monto.")
            return

        try:
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return
 with open("gastos.csv", mode="a", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([fecha, tipo, descripcion, monto])

        messagebox.showinfo("Éxito", f"Gasto registrado correctamente.")
        ventana_gasto.destroy()

    tk.Button(ventana_gasto, text="Registrar Gasto", command=guardar_gasto).pack(pady=10)




    #######

def ver_reporte():
    ventana_reporte = Toplevel()
    ventana_reporte.title("Reporte General")
    ventana_reporte.geometry("400x300")

    # Campos para seleccionar mes y año
    tk.Label(ventana_reporte, text="Seleccionar Mes (1-12):").pack(pady=5)
    entry_mes = tk.Entry(ventana_reporte)
    entry_mes.pack()

    tk.Label(ventana_reporte, text="Seleccionar Año:").pack(pady=5)
    entry_anio = tk.Entry(ventana_reporte)
    entry_anio.pack()

    def filtrar_reportes():
        try:
            mes = int(entry_mes.get())
            anio = int(entry_anio.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un mes y año válidos.")
            return

        if mes < 1 or mes > 12:
            messagebox.showerror("Error", "El mes debe ser entre 1 y 12.")
            return

 total_ingresos = 0.0
        total_gastos = {
            "Servicios Públicos": 0.0,
            "Impuestos": 0.0,
            "Otros": 0.0
        }

        # Leer ingresos (pagos.csv)
        try:
            with open("pagos.csv", newline="") as archivo:
                lector = csv.reader(archivo)
                for fila in lector:
                    if len(fila) >= 3:
                        fecha_pago = fila[0].split("-")  # Fecha en formato YYYY-MM-DD
                        if int(fecha_pago[1]) == mes and int(fecha_pago[0]) == anio:
                            total_ingresos += float(fila[2])
        except FileNotFoundError:
            pass  # No hay pagos aún

# Leer gastos (gastos.csv)
try:
    with open("gastos.csv", newline="") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if len(fila) >= 4:
                fecha_gasto = fila[0].split("-")
                if int(fecha_gasto[1]) == mes and int(fecha_gasto[0]) == anio:
                    tipo = fila[1]
                    monto = float(fila[3])
                    if tipo in total_gastos:
                        total_gastos[tipo] += monto
except FileNotFoundError:
    pass  # No hay gastos aún

total_gastos_sum = sum(total_gastos.values())
balance = total_ingresos - total_gastos_sum

# Mostrar resultados en pantalla
reporte = tk.Text(ventana_reporte, height=15, width=50)
reporte.pack(pady=10)

reporte.insert(tk.END, f"--- REPORTE DEL {mes}/{anio} ---\n")
reporte.insert(tk.END, f"Ingresos totales: ${total_ingresos:.2f}\n\n")
reporte.insert(tk.END, f"Gastos:\n")
for tipo, monto in total_gastos.items():
    reporte.insert(tk.END, f"  {tipo}: ${monto:.2f}\n")
reporte.insert(tk.END, f"\nTotal gastos: ${total_gastos_sum:.2f}\n")
reporte.insert(tk.END, f"\nBALANCE: ${balance:.2f}\n")

reporte.config(state='disabled')

tk.Button(ventana_reporte, text="Generar Reporte", command=filtrar_reportes).pack(pady=10)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generar_pdf_reporte(mes, anio, total_ingresos, total_gastos, total_gastos_sum, balance):
    nombre_archivo = f"reporte_{mes}_{anio}.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=letter)

    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"--- REPORTE DEL {mes}/{anio} ---")
    c.drawString(100, 730, f"Ingresos totales: ${total_ingresos:.2f}")

    y = 710
    c.drawString(100, y, "Gastos:")
    y -= 20
    for tipo, monto in total_gastos.items():
        c.drawString(100, y, f"{tipo}: ${monto:.2f}")
        y -= 20

    c.drawString(100, y, f"Total gastos: ${total_gastos_sum:.2f}")
    y -= 20
    c.drawString(100, y, f"BALANCE: ${balance:.2f}")

    c.save()

 messagebox.showinfo("Éxito", f"Reporte generado como PDF: {nombre_archivo}")


tk.Button(ventana_reporte, text="Generar Reporte PDF", command=lambda: generar_pdf_reporte(mes, anio, total_ingresos, total_gastos, total_gastos_sum, balance)).pack(pady=5)