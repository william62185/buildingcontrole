import tkinter as tk
import csv
import datetime
import os
from tkinter import messagebox, Toplevel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Crear ventana principal
root = tk.Tk()
root.title("Control de Edificio")
root.geometry("400x300")


# Funciones básicas para botones (aún no implementadas)
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
            renta = round(renta)
        except ValueError:
            messagebox.showerror("Error", "La renta debe ser un número.")
            return
        with open("inquilinos.csv", mode="a", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([nombre, apto, renta])
        messagebox.showinfo("Guardado", f"Inquilino {nombre} registrado exitosamente.")
        ventana_inquilinos.destroy()

    tk.Button(ventana_inquilinos, text="Guardar", command=guardar_inquilino).pack(pady=10)

        # Generar el recibo
def generar_recibo_pago(inquilino, apartamento, monto, fecha):
    nombre_archivo = f"recibo_pago_{inquilino}_{apartamento}_{fecha}.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=letter)

    ancho, alto = letter
    margen_izquierdo = 1 * inch
    y = alto - 1 * inch

    lineas = [
                f"Fecha: {fecha}",
                "",
                "",
                "Muñoz & Asociados Buildings",
                "Pitalito - Huila",
                "",
                "",
                f"Asunto: Constancia de pago del canon de arrendamiento - Apto:{apartamento}.",
                "",
                "",
                f"A la fecha de este documento, recibimos del señor(a) {inquilino}",
                f"el valor de ${round(monto)} por concepto de pago del canon de",
                f"arrendamiento correspondiente al siguiente mes.",
                "",
                "",
                "",
                 "Atentamente,",
                 "Administración - Muñoz y Asociados Buildings."
            ]

    text = c.beginText(margen_izquierdo, y)
    text.setFont("Helvetica", 12)
    text.setLeading(18)  # Espaciado entre líneas
    text.textLines(lineas)
    c.drawText(text)
    c.save()
    return nombre_archivo

def registrar_pago():
    ventana_pago = Toplevel()
    ventana_pago.title("Registrar Pago")
    ventana_pago.geometry("350x250")

    # Leer inquilinos desde el archivo
    try:
        with open("inquilinos.csv", newline="") as archivo:
            lector = csv.reader(archivo)
            datos_inquilinos = [fila for fila in lector]  # nombre, apartamento, renta
    except FileNotFoundError:
        messagebox.showerror("Error", "No hay inquilinos registrados aún.")
        return

    # Crear mapa para acceder a renta por selección
    mapa_renta = {
        f"{fila[0]} - Apto {fila[1]}": round(int(fila[2]))
        for fila in datos_inquilinos
    }

    lista_inquilinos = list(mapa_renta.keys())
    tk.Label(ventana_pago, text="Seleccionar Inquilino:").pack(pady=5)
    var_inquilino = tk.StringVar(ventana_pago)
    var_inquilino.set(lista_inquilinos[0])  # Valor inicial
    dropdown = tk.OptionMenu(ventana_pago, var_inquilino, *lista_inquilinos)
    dropdown.pack()

    tk.Label(ventana_pago, text="Monto pagado:").pack(pady=5)
    entry_monto = tk.Entry(ventana_pago)
    entry_monto.pack()

    def actualizar_monto(*args):
        inquilino = var_inquilino.get()
        renta = mapa_renta.get(inquilino, 0)
        entry_monto.delete(0, tk.END)
        entry_monto.insert(0, f"{renta}")

    var_inquilino.trace_add("write", actualizar_monto)
    actualizar_monto()  # inicial

    def guardar_pago():
        inquilino = var_inquilino.get()
        monto = entry_monto.get()
        fecha = datetime.date.today().isoformat()

        if not monto:
            messagebox.showwarning("Faltan datos", "Debes ingresar el monto.")
            return

        try:
            monto = float(monto)
            if monto <= 0:  # Validar que el monto sea un número positivo
                raise ValueError("El monto debe ser mayor que 0.")
        except ValueError as e:
            messagebox.showerror("Error", f"El monto debe ser un número positivo. ({str(e)})")
            return

        with open("pagos.csv", mode="a", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([fecha, inquilino, monto])

        # Separar nombre y apartamento
        nombre, apto_raw = inquilino.split(" - Apto ")
        apartamento = apto_raw.strip()

        archivo_recibo = generar_recibo_pago(nombre, apartamento, monto, fecha)
        messagebox.showinfo("Éxito", f"Pago registrado y recibo generado:\n{archivo_recibo}")
        os.startfile(archivo_recibo)
        ventana_pago.destroy()
    tk.Button(ventana_pago, text="Registrar Pago", command=guardar_pago).pack(pady=10)

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
            monto = round(float(monto))
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return
        with open("gastos.csv", mode="a", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([fecha, tipo, descripcion, monto])

        messagebox.showinfo("Éxito", f"Gasto registrado correctamente.")
        ventana_gasto.destroy()

    tk.Button(ventana_gasto, text="Registrar Gasto", command=guardar_gasto).pack(pady=10)

def ver_reporte():
    ventana_reporte = Toplevel()
    ventana_reporte.title("Reporte General")
    ventana_reporte.geometry("400x350")

    # Selector de tipo de reporte
    tk.Label(ventana_reporte, text="Seleccionar tipo de reporte:").pack(pady=5)
    tipo_reporte_var = tk.StringVar()
    tipo_reporte_var.set("Mensual")  # Valor predeterminado

    tipo_reporte = tk.OptionMenu(ventana_reporte, tipo_reporte_var, "Mensual", "Anual")
    tipo_reporte.pack(pady=5)

    # Entrada de mes (solo visible si se selecciona "Mensual")
    tk.Label(ventana_reporte, text="Seleccionar Año:").pack(pady=5)
    entry_anio = tk.Entry(ventana_reporte)
    entry_anio.pack()

    tk.Label(ventana_reporte, text="Seleccionar Mes (1-12):").pack(pady=5)
    entry_mes = tk.Entry(ventana_reporte)
    entry_mes.pack()
    entry_mes.config(state='disabled')  # Se desactiva por defecto

    # Habilitar o deshabilitar el campo de mes dependiendo del tipo de reporte
    def habilitar_mes(*args):
        if tipo_reporte_var.get() == "Mensual":
            entry_mes.config(state='normal')
        else:
            entry_mes.config(state='disabled')

    tipo_reporte_var.trace_add("write", habilitar_mes)

    def filtrar_reportes():
        try:
            anio = int(entry_anio.get())
            if tipo_reporte_var.get() == "Mensual":
                mes = int(entry_mes.get())
                if mes < 1 or mes > 12:
                    messagebox.showerror("Error", "El mes debe estar entre 1 y 12.")
                    return
            else:
                mes = None  # Para el reporte anual no necesitamos mes
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un año (y mes si es necesario) válidos.")
            return

        total_ingresos = 0
        total_gastos = {"Servicios Públicos": 0, "Impuestos": 0, "Otros": 0}

        # Leer ingresos
        try:
            with open("pagos.csv", newline="") as archivo:
                lector = csv.reader(archivo)
                for fila in lector:
                    if len(fila) >= 3:
                        fecha = fila[0].split("-")
                        if int(fecha[0]) == anio and (mes is None or int(fecha[1]) == mes):
                            total_ingresos += round(float(fila[2]))
        except FileNotFoundError:
            pass

        # Leer gastos
        try:
            with open("gastos.csv", newline="") as archivo:
                lector = csv.reader(archivo)
                for fila in lector:
                    if len(fila) >= 4:
                        fecha = fila[0].split("-")
                        if int(fecha[0]) == anio and (mes is None or int(fecha[1]) == mes):
                            tipo = fila[1]
                            monto = round(float(fila[3]))
                            if tipo in total_gastos:
                                total_gastos[tipo] += monto
        except FileNotFoundError:
            pass

        total_gastos_sum = sum(total_gastos.values())
        balance = total_ingresos - total_gastos_sum

        # Mostrar resultados
        reporte = tk.Text(ventana_reporte, height=15, width=50)
        reporte.pack(pady=10)
        if mes is not None:
            reporte.insert(tk.END, f"--- REPORTE DEL {mes}/{anio} ---\n")
        else:
            reporte.insert(tk.END, f"--- REPORTE DEL AÑO {anio} ---\n")
        reporte.insert(tk.END, f"Ingresos totales: ${total_ingresos}\n\n")
        reporte.insert(tk.END, f"Gastos:\n")
        for tipo, monto in total_gastos.items():
            reporte.insert(tk.END, f"  {tipo}: ${monto}\n")
        reporte.insert(tk.END, f"\nTotal gastos: ${total_gastos_sum}\n")
        reporte.insert(tk.END, f"\nBALANCE: ${balance}\n")
        reporte.config(state='disabled')

        # Crear botón PDF aquí, con los valores ya calculados
        tk.Button(ventana_reporte, text="Generar Reporte PDF", command=lambda: generar_pdf_reporte(
            anio, mes, total_ingresos, total_gastos, total_gastos_sum, balance)).pack(pady=5)

    # Botón para generar el reporte visual
    tk.Button(ventana_reporte, text="Generar Reporte", command=filtrar_reportes).pack(pady=10)


def generar_pdf_reporte(anio, mes, total_ingresos, total_gastos, total_gastos_sum, balance):
    nombre_archivo = f"reporte_{anio}_{mes if mes else 'anual'}.pdf"  # Se ajusta según mes o anual
    c = canvas.Canvas(nombre_archivo, pagesize=letter)

    c.setFont("Helvetica", 12)
    if mes:
        c.drawString(100, 750, f"--- REPORTE DEL {mes}/{anio} ---")
    else:
        c.drawString(100, 750, f"--- REPORTE DEL AÑO {anio} ---")

    c.drawString(100, 730, f"Ingresos totales: ${total_ingresos}")

    y = 710
    c.drawString(100, y, "Gastos:")
    y -= 20
    for tipo, monto in total_gastos.items():
        c.drawString(100, y, f"{tipo}: ${monto}")
        y -= 20

    c.drawString(100, y, f"Total gastos: ${total_gastos_sum}")
    y -= 20
    c.drawString(100, y, f"BALANCE: ${balance}")

    c.save()
    messagebox.showinfo("Éxito", f"Reporte PDF generado como: {nombre_archivo}")
    os.startfile(nombre_archivo)  # Abre el PDF automáticamente (solo en Windows)

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
