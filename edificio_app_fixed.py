import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, StringVar
import sqlite3
import datetime
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import shutil

# Define la clase TenantModule primero
class TenantModule:
    def __init__(self, manager):
        self.manager = manager

    def setup_ui(self, parent):
        """Configura la interfaz de gestión de inquilinos"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill="both", expand=True)

        # Frame superior para agregar inquilinos
        add_frame = ttk.LabelFrame(frame, text="Agregar Nuevo Inquilino", padding="10")
        add_frame.pack(fill="x", pady=10)

        # Contenido del frame de agregar
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill="x")

        # Primera fila
        row1 = ttk.Frame(form_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Nombre:").pack(side="left", padx=(0, 5))
        self.entry_nombre = ttk.Entry(row1, width=30)
        self.entry_nombre.pack(side="left", padx=(0, 15))

        ttk.Label(row1, text="Apartamento:").pack(side="left", padx=(0, 5))
        self.entry_apto = ttk.Entry(row1, width=10)
        self.entry_apto.pack(side="left")

        # Segunda fila
        row2 = ttk.Frame(form_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Renta mensual:").pack(side="left", padx=(0, 5))
        self.entry_renta = ttk.Entry(row2, width=15)
        self.entry_renta.pack(side="left")

        # Botón de guardar
        btn_frame = ttk.Frame(add_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Guardar Inquilino",
                   command=self.guardar_inquilino).pack(side="right")

        # Frame de búsqueda
        search_frame = ttk.LabelFrame(frame, text="Buscar Inquilinos", padding="10")
        search_frame.pack(fill="x", pady=10)

        # Campo de búsqueda
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill="x", pady=5)

        ttk.Label(search_row, text="Buscar:").pack(side="left", padx=(0, 5))
        self.entry_buscar = ttk.Entry(search_row, width=30)
        self.entry_buscar.pack(side="left", padx=(0, 5))
        self.entry_buscar.bind("<KeyRelease>", self.on_search_key_release)

        ttk.Button(search_row, text="Buscar",
                   command=self.buscar_inquilinos).pack(side="left")

        # Lista de inquilinos
        list_frame = ttk.LabelFrame(frame, text="Lista de Inquilinos", padding="10")
        list_frame.pack(fill="both", expand=True, pady=10)

        # Treeview para mostrar inquilinos
        columns = ("id", "nombre", "apartamento", "renta")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apartamento", text="Apartamento")
        self.tree.heading("renta", text="Renta Mensual")

        # Ajustar anchos de columna
        self.tree.column("id", width=50)
        self.tree.column("nombre", width=200)
        self.tree.column("apartamento", width=100)
        self.tree.column("renta", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        btn_frame2 = ttk.Frame(frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Editar Seleccionado",
                   command=self.editar_inquilino).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Eliminar Seleccionado",
                   command=self.eliminar_inquilino).pack(side="left")

        # Cargar inquilinos al inicio
        self.cargar_inquilinos()

    def cargar_inquilinos(self):
        """Carga todos los inquilinos desde la base de datos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apartamento, renta FROM inquilinos ORDER BY apartamento")

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def guardar_inquilino(self):
        """Guarda un nuevo inquilino en la base de datos"""
        nombre = self.entry_nombre.get()
        apto = self.entry_apto.get()
        renta = self.entry_renta.get()

        # Validaciones
        if not nombre or not apto or not renta:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
            return

        try:
            renta = float(renta)
            if renta <= 0:
                messagebox.showerror("Error", "La renta debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "La renta debe ser un número.")
            return

        # Guardar en la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO inquilinos (nombre, apartamento, renta) VALUES (?, ?, ?)",
                       (nombre, apto, renta))

        conn.commit()
        conn.close()

        messagebox.showinfo("Guardado", f"Inquilino {nombre} registrado exitosamente.")

        # Limpiar campos
        self.entry_nombre.delete(0, tk.END)
        self.entry_apto.delete(0, tk.END)
        self.entry_renta.delete(0, tk.END)

        # Recargar lista
        self.cargar_inquilinos()

    def buscar_inquilinos(self):
        """Busca inquilinos según el término ingresado"""
        termino = self.entry_buscar.get().lower()

        # Si el término está vacío, mostrar todos
        if not termino:
            self.cargar_inquilinos()
            return

        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Buscar en la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        # Búsqueda por nombre o apartamento
        cursor.execute("""
            SELECT id, nombre, apartamento, renta FROM inquilinos 
            WHERE LOWER(nombre) LIKE ? OR LOWER(apartamento) LIKE ?
            ORDER BY apartamento
        """, (f"%{termino}%", f"%{termino}%"))

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def on_search_key_release(self, event):
        """Realiza búsqueda al escribir"""
        self.buscar_inquilinos()

    def editar_inquilino(self):
        """Abre ventana para editar el inquilino seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un inquilino para editar.")
            return

        # Obtener datos del inquilino seleccionado
        values = self.tree.item(selected[0], "values")
        inquilino_id = values[0]

        # Crear ventana de edición
        edit_window = Toplevel()
        edit_window.title("Editar Inquilino")
        edit_window.geometry("300x220")
        edit_window.transient(self.manager.root)  # Hacer ventana modal

        # Contenido de la ventana
        ttk.Label(edit_window, text="Nombre:").pack(pady=5)
        entry_nombre = ttk.Entry(edit_window, width=30)
        entry_nombre.insert(0, values[1])
        entry_nombre.pack()

        ttk.Label(edit_window, text="Apartamento:").pack(pady=5)
        entry_apto = ttk.Entry(edit_window, width=15)
        entry_apto.insert(0, values[2])
        entry_apto.pack()

        ttk.Label(edit_window, text="Renta mensual:").pack(pady=5)
        entry_renta = ttk.Entry(edit_window, width=15)
        entry_renta.insert(0, values[3])
        entry_renta.pack()

        def guardar_cambios():
            nombre = entry_nombre.get()
            apto = entry_apto.get()
            renta = entry_renta.get()

            # Validaciones
            if not nombre or not apto or not renta:
                messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
                return

            try:
                renta = float(renta)
                if renta <= 0:
                    messagebox.showerror("Error", "La renta debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error", "La renta debe ser un número.")
                return

            # Actualizar en la base de datos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE inquilinos 
                SET nombre = ?, apartamento = ?, renta = ? 
                WHERE id = ?
            """, (nombre, apto, renta, inquilino_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Actualizado", f"Inquilino {nombre} actualizado exitosamente.")
            edit_window.destroy()

            # Recargar lista
            self.cargar_inquilinos()

        ttk.Button(edit_window, text="Guardar Cambios",
                   command=guardar_cambios).pack(pady=15)

    def eliminar_inquilino(self):
        """Elimina el inquilino seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un inquilino para eliminar.")
            return

        # Obtener datos del inquilino seleccionado
        values = self.tree.item(selected[0], "values")
        inquilino_id = values[0]
        nombre = values[1]

        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Estás seguro de eliminar a {nombre}?"):
            return

        # Verificar si hay pagos asociados
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pagos WHERE inquilino_id = ?", (inquilino_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            if not messagebox.askyesno("Pagos existentes",
                                       f"Hay {count} pagos asociados a este inquilino. "
                                       f"¿Deseas eliminar el inquilino y todos sus pagos?"):
                conn.close()
                return

            # Eliminar pagos asociados
            cursor.execute("DELETE FROM pagos WHERE inquilino_id = ?", (inquilino_id,))

        # Eliminar inquilino
        cursor.execute("DELETE FROM inquilinos WHERE id = ?", (inquilino_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Eliminado", f"Inquilino {nombre} eliminado exitosamente.")

        # Recargar lista
        self.cargar_inquilinos()

# Luego define la clase PaymentModule
class PaymentModule:
    def __init__(self, manager):
        self.manager = manager

    def setup_ui(self, parent):
        """Configura la interfaz de gestión de pagos"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill="both", expand=True)

        # Frame para registrar pagos
        register_frame = ttk.LabelFrame(frame, text="Registrar Nuevo Pago", padding="10")
        register_frame.pack(fill="x", pady=10)

        # Seleccionar inquilino
        row1 = ttk.Frame(register_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Inquilino:").pack(side="left", padx=(0, 5))

        # Dropdown de inquilinos
        self.inquilino_var = StringVar()
        self.combo_inquilinos = ttk.Combobox(row1, textvariable=self.inquilino_var, width=40)
        self.combo_inquilinos.pack(side="left", fill="x", expand=True)
        self.combo_inquilinos.bind("<<ComboboxSelected>>", self.actualizar_monto)

        # Monto
        row2 = ttk.Frame(register_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Monto:").pack(side="left", padx=(0, 5))
        self.entry_monto = ttk.Entry(row2, width=15)
        self.entry_monto.pack(side="left")

        # Fecha
        ttk.Label(row2, text="Fecha:").pack(side="left", padx=(15, 5))

        self.entry_fecha = ttk.Entry(row2, width=15)
        # Fecha actual por defecto
        self.entry_fecha.insert(0, datetime.date.today().isoformat())
        self.entry_fecha.pack(side="left")

        # Botón de registrar
        btn_frame = ttk.Frame(register_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Registrar Pago",
                   command=self.registrar_pago).pack(side="right")

        # Frame para historial de pagos
        history_frame = ttk.LabelFrame(frame, text="Historial de Pagos", padding="10")
        history_frame.pack(fill="both", expand=True, pady=10)

        # Filtro de historial
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Filtrar por inquilino:").pack(side="left", padx=(0, 5))

        # Dropdown para filtro
        self.filtro_var = StringVar()
        self.combo_filtro = ttk.Combobox(filter_frame, textvariable=self.filtro_var, width=40)
        self.combo_filtro.pack(side="left", padx=(0, 5))

        ttk.Button(filter_frame, text="Filtrar",
                   command=self.filtrar_pagos).pack(side="left")
        ttk.Button(filter_frame, text="Mostrar Todos",
                   command=self.cargar_pagos).pack(side="left", padx=(5, 0))

        # Treeview para historial
        columns = ("id", "fecha", "inquilino", "apartamento", "monto")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("inquilino", text="Inquilino")
        self.tree.heading("apartamento", text="Apartamento")
        self.tree.heading("monto", text="Monto")

        # Ajustar anchos de columna
        self.tree.column("id", width=50)
        self.tree.column("fecha", width=100)
        self.tree.column("inquilino", width=200)
        self.tree.column("apartamento", width=100)
        self.tree.column("monto", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        btn_frame2 = ttk.Frame(frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Generar Recibo",
                   command=self.generar_recibo).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Eliminar Pago",
                   command=self.eliminar_pago).pack(side="left")

        # Cargar datos iniciales
        self.cargar_inquilinos_combo()
        self.cargar_pagos()

    def cargar_inquilinos_combo(self):
        """Carga la lista de inquilinos en los combos"""
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombre, apartamento FROM inquilinos 
            ORDER BY nombre
        """)

        inquilinos = []
        self.mapa_inquilinos = {}  # Para mantener relación ID-nombre
        self.mapa_rentas = {}  # Para acceder a la renta por ID

        for id, nombre, apto in cursor.fetchall():
            texto = f"{nombre} - Apto {apto}"
            inquilinos.append(texto)
            self.mapa_inquilinos[texto] = id

            # Obtener renta
            cursor.execute("SELECT renta FROM inquilinos WHERE id = ?", (id,))
            renta = cursor.fetchone()[0]
            self.mapa_rentas[texto] = renta

        # Actualizar combos
        self.combo_inquilinos['values'] = inquilinos
        if inquilinos:
            self.combo_inquilinos.current(0)
            self.actualizar_monto()

        # Combo de filtro con opción adicional "Todos"
        self.combo_filtro['values'] = ["Todos"] + inquilinos
        self.combo_filtro.current(0)

        conn.close()

    def actualizar_monto(self, event=None):
        """Actualiza el monto según el inquilino seleccionado"""
        inquilino = self.inquilino_var.get()
        if inquilino in self.mapa_rentas:
            self.entry_monto.delete(0, tk.END)
            self.entry_monto.insert(0, str(self.mapa_rentas[inquilino]))

    def cargar_pagos(self):
        """Carga todos los pagos en el treeview"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar desde la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.fecha, i.nombre, i.apartamento, p.monto 
            FROM pagos p
            JOIN inquilinos i ON p.inquilino_id = i.id
            ORDER BY p.fecha DESC
        """)

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def filtrar_pagos(self):
        """Filtra los pagos por inquilino seleccionado"""
        filtro = self.filtro_var.get()
        if filtro == "Todos":
            self.cargar_pagos()
            return

        # Obtener ID del inquilino
        inquilino_id = self.mapa_inquilinos.get(filtro)
        if not inquilino_id:
            return

        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar pagos filtrados
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.fecha, i.nombre, i.apartamento, p.monto 
            FROM pagos p
            JOIN inquilinos i ON p.inquilino_id = i.id
            WHERE p.inquilino_id = ?
            ORDER BY p.fecha DESC
        """, (inquilino_id,))

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def registrar_pago(self):
        """Registra un nuevo pago"""
        inquilino = self.inquilino_var.get()
        monto = self.entry_monto.get()
        fecha = self.entry_fecha.get()

        # Validaciones
        if not inquilino:
            messagebox.showwarning("Selección", "Por favor selecciona un inquilino.")
            return

        if not monto:
            messagebox.showwarning("Monto", "Por favor ingresa el monto del pago.")
            return

        try:
            monto = float(monto)
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return

        try:
            datetime.date.fromisoformat(fecha)
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
            return

        # Obtener ID del inquilino
        inquilino_id = self.mapa_inquilinos.get(inquilino)
        if not inquilino_id:
            messagebox.showerror("Error", "Inquilino no encontrado.")
            return

        # Guardar en la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO pagos (fecha, inquilino_id, monto) VALUES (?, ?, ?)",
                       (fecha, inquilino_id, monto))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Pago registrado correctamente.")

        # Generar recibo
        self.generar_recibo_pago(inquilino, monto, fecha)

        # Recargar lista de pagos
        self.cargar_pagos()

    def generar_recibo_pago(self, inquilino_texto, monto, fecha):
        """Genera un recibo de pago en PDF"""
        # Extraer nombre y apartamento
        nombre, apto_texto = inquilino_texto.split(" - Apto ")
        apartamento = apto_texto.strip()

        # Generar nombre de archivo
        nombre_archivo = f"recibo_pago_{nombre.replace(' ', '_')}_{apartamento}_{fecha}.pdf"

        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        ancho, alto = letter
        margen_izquierdo = 1 * inch
        y = alto - 1 * inch

        # Contenido del recibo
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
            f"A la fecha de este documento, recibimos del señor(a) {nombre}",
            f"el valor de ${round(monto)} por concepto de pago del canon de",
            f"arrendamiento correspondiente al siguiente mes.",
            "",
            "",
            "",
            "Atentamente,",
            "Administración - Muñoz y Asociados Buildings."
        ]

        # Dibujar texto
        text = c.beginText(margen_izquierdo, y)
        text.setFont("Helvetica", 12)
        text.setLeading(18)  # Espaciado entre líneas
        text.textLines(lineas)
        c.drawText(text)

        # Guardar y abrir el PDF
        c.save()
        messagebox.showinfo("Recibo generado", f"Se ha generado el recibo: {nombre_archivo}")

        # Abrir el PDF (solo funciona en Windows)
        try:
            os.startfile(nombre_archivo)
        except:
            messagebox.showinfo("Información", f"El recibo se guardó como: {nombre_archivo}")

    def generar_recibo(self):
        """Genera un recibo para el pago seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un pago para generar su recibo.")
            return

        # Obtener datos del pago
        values = self.tree.item(selected[0], "values")
        fecha = values[1]
        nombre = values[2]
        apartamento = values[3]
        monto = float(values[4])

        # Generar nombre de archivo
        nombre_archivo = f"recibo_pago_{nombre.replace(' ', '_')}_{apartamento}_{fecha}.pdf"

        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        ancho, alto = letter
        margen_izquierdo = 1 * inch
        y = alto - 1 * inch

        # Contenido del recibo
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
            f"A la fecha de este documento, recibimos del señor(a) {nombre}",
            f"el valor de ${round(monto)} por concepto de pago del canon de",
            f"arrendamiento correspondiente al siguiente mes.",
            "",
            "",
            "",
            "Atentamente,",
            "Administración - Muñoz y Asociados Buildings."
        ]

        # Dibujar texto
        text = c.beginText(margen_izquierdo, y)
        text.setFont("Helvetica", 12)
        text.setLeading(18)  # Espaciado entre líneas
        text.textLines(lineas)
        c.drawText(text)

        # Guardar y abrir el PDF
        c.save()
        messagebox.showinfo("Recibo generado", f"Se ha generado el recibo: {nombre_archivo}")

        # Abrir el PDF (solo funciona en Windows)
        try:
            os.startfile(nombre_archivo)
        except:
            messagebox.showinfo("Información", f"El recibo se guardó como: {nombre_archivo}")

    def eliminar_pago(self):
        """Elimina el pago seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un pago para eliminar.")
            return

        # Obtener datos del pago
        values = self.tree.item(selected[0], "values")
        pago_id = values[0]
        fecha = values[1]
        nombre = values[2]

        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Estás seguro de eliminar el pago de {nombre} del {fecha}?"):
            return

        # Eliminar de la base de datos (corregido: eliminar indentación)
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Eliminado", "Pago eliminado exitosamente.")

        # Recargar lista
        self.cargar_pagos()

class ExpenseModule:
    def __init__(self, manager):
        self.manager = manager

    def setup_ui(self, parent):
        """Configura la interfaz de gestión de gastos"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill="both", expand=True)

        # Frame para registrar gastos
        register_frame = ttk.LabelFrame(frame, text="Registrar Nuevo Gasto", padding="10")
        register_frame.pack(fill="x", pady=10)

        # Tipo de gasto
        row1 = ttk.Frame(register_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Tipo de gasto:").pack(side="left", padx=(0, 5))

        self.tipo_var = StringVar()
        self.tipo_var.set("Servicios Públicos")

        tipos_gasto = ["Servicios Públicos", "Impuestos", "Mantenimiento", "Reparaciones", "Otros"]
        self.combo_tipo = ttk.Combobox(row1, textvariable=self.tipo_var, values=tipos_gasto, width=20)
        self.combo_tipo.pack(side="left")

        # Fecha
        ttk.Label(row1, text="Fecha:").pack(side="left", padx=(15, 5))

        self.entry_fecha = ttk.Entry(row1, width=15)
        self.entry_fecha.insert(0, datetime.date.today().isoformat())
        self.entry_fecha.pack(side="left")

        # Descripción
        row2 = ttk.Frame(register_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Descripción:").pack(side="left", padx=(0, 5))
        self.entry_desc = ttk.Entry(row2, width=50)
        self.entry_desc.pack(side="left", fill="x", expand=True)

        # Monto
        row3 = ttk.Frame(register_frame)
        row3.pack(fill="x", pady=5)

        ttk.Label(row3, text="Monto:").pack(side="left", padx=(0, 5))
        self.entry_monto = ttk.Entry(row3, width=15)
        self.entry_monto.pack(side="left")

        # Botón de registrar
        btn_frame = ttk.Frame(register_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Registrar Gasto",
                   command=self.registrar_gasto).pack(side="right")

        # Frame para historial de gastos
        history_frame = ttk.LabelFrame(frame, text="Historial de Gastos", padding="10")
        history_frame.pack(fill="both", expand=True, pady=10)

        # Filtro de historial
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Filtrar por tipo:").pack(side="left", padx=(0, 5))

        self.filtro_var = StringVar()
        self.filtro_var.set("Todos")

        filtro_tipos = ["Todos"] + tipos_gasto
        self.combo_filtro = ttk.Combobox(filter_frame, textvariable=self.filtro_var,
                                         values=filtro_tipos, width=20)
        self.combo_filtro.pack(side="left", padx=(0, 5))

        ttk.Button(filter_frame, text="Filtrar",
                   command=self.filtrar_gastos).pack(side="left")

        # Treeview para historial
        columns = ("id", "fecha", "tipo", "descripcion", "monto")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("monto", text="Monto")

        # Ajustar anchos de columna
        self.tree.column("id", width=50)
        self.tree.column("fecha", width=100)
        self.tree.column("tipo", width=120)
        self.tree.column("descripcion", width=250)
        self.tree.column("monto", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        btn_frame2 = ttk.Frame(frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Editar Gasto",
                   command=self.editar_gasto).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Eliminar Gasto",
                   command=self.eliminar_gasto).pack(side="left")

        # Cargar datos iniciales
        self.cargar_gastos()

    def cargar_gastos(self):
        """Carga todos los gastos en el treeview"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar desde la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fecha, tipo, descripcion, monto
            FROM gastos
            ORDER BY fecha DESC
        """)

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def filtrar_gastos(self):
        """Filtra los gastos por tipo"""
        filtro = self.filtro_var.get()
        if filtro == "Todos":
            self.cargar_gastos()
            return

        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar gastos filtrados
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fecha, tipo, descripcion, monto
            FROM gastos
            WHERE tipo = ?
            ORDER BY fecha DESC
        """, (filtro,))

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def registrar_gasto(self):
        """Registra un nuevo gasto"""
        tipo = self.tipo_var.get()
        fecha = self.entry_fecha.get()
        descripcion = self.entry_desc.get()
        monto = self.entry_monto.get()

        # Validaciones
        if not tipo:
            messagebox.showwarning("Tipo", "Por favor selecciona un tipo de gasto.")
            return

        if not monto:
            messagebox.showwarning("Monto", "Por favor ingresa el monto del gasto.")
            return

        try:
            monto = float(monto)
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return

        try:
            datetime.date.fromisoformat(fecha)
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
            return

        # Guardar en la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gastos (fecha, tipo, descripcion, monto) 
            VALUES (?, ?, ?, ?)
        """, (fecha, tipo, descripcion, monto))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Gasto registrado correctamente.")

        # Limpiar campos
        self.entry_desc.delete(0, tk.END)
        self.entry_monto.delete(0, tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.date.today().isoformat())

        # Recargar lista
        self.cargar_gastos()

    def editar_gasto(self):
        """Abre ventana para editar el gasto seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un gasto para editar.")
            return

        # Obtener datos del gasto seleccionado
        values = self.tree.item(selected[0], "values")
        gasto_id = values[0]

        # Crear ventana de edición
        edit_window = Toplevel()
        edit_window.title("Editar Gasto")
        edit_window.geometry("400x250")
        edit_window.transient(self.manager.root)  # Hacer ventana modal

        # Contenido de la ventana
        ttk.Label(edit_window, text="Tipo de gasto:").pack(pady=5)

        tipo_var = StringVar()
        tipo_var.set(values[2])

        tipos_gasto = ["Servicios Públicos", "Impuestos", "Mantenimiento", "Reparaciones", "Otros"]
        combo_tipo = ttk.Combobox(edit_window, textvariable=tipo_var, values=tipos_gasto, width=20)
        combo_tipo.pack()

        ttk.Label(edit_window, text="Fecha (YYYY-MM-DD):").pack(pady=5)
        entry_fecha = ttk.Entry(edit_window, width=15)
        entry_fecha.insert(0, values[1])
        entry_fecha.pack()

        ttk.Label(edit_window, text="Descripción:").pack(pady=5)
        entry_desc = ttk.Entry(edit_window, width=50)
        entry_desc.insert(0, values[3])
        entry_desc.pack()

        ttk.Label(edit_window, text="Monto:").pack(pady=5)
        entry_monto = ttk.Entry(edit_window, width=15)
        entry_monto.insert(0, values[4])
        entry_monto.pack()

        def guardar_cambios():
            tipo = tipo_var.get()
            fecha = entry_fecha.get()
            descripcion = entry_desc.get()
            monto = entry_monto.get()

            # Validaciones básicas
            if not tipo or not fecha or not monto:
                messagebox.showwarning("Campos vacíos", "Por favor completa los campos obligatorios.")
                return

            try:
                monto = float(monto)
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error", "El monto debe ser un número.")
                return

            # Actualizar en la base de datos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE gastos 
                SET fecha = ?, tipo = ?, descripcion = ?, monto = ? 
                WHERE id = ?
            """, (fecha, tipo, descripcion, monto, gasto_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Actualizado", "Gasto actualizado exitosamente.")
            edit_window.destroy()

            # Recargar lista
            self.cargar_gastos()

        ttk.Button(edit_window, text="Guardar Cambios",
                   command=guardar_cambios).pack(pady=15)

    def eliminar_gasto(self):
        """Elimina el gasto seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un gasto para eliminar.")
            return

        # Obtener datos del gasto seleccionado
        values = self.tree.item(selected[0], "values")
        gasto_id = values[0]
        tipo = values[2]
        monto = values[4]

        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Estás seguro de eliminar el gasto de {tipo} por ${monto}?"):
            return

        # Eliminar de la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Eliminado", "Gasto eliminado exitosamente.")

        # Recargar lista
        self.cargar_gastos()

class ReportModule:
    def __init__(self, manager):
        self.manager = manager
        self.current_report_data = None  # Para almacenar datos del reporte actual

    def setup_ui(self, parent):
        """Configura la interfaz de reportes"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill="both", expand=True)

        # Frame para selección de reportes
        select_frame = ttk.LabelFrame(frame, text="Generar Reporte", padding="10")
        select_frame.pack(fill="x", pady=10)

        # Tipo de reporte
        row1 = ttk.Frame(select_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Tipo de reporte:").pack(side="left", padx=(0, 5))

        self.tipo_reporte_var = StringVar()
        self.tipo_reporte_var.set("Mensual")

        tipos_reporte = ["Mensual", "Anual"]
        self.combo_tipo = ttk.Combobox(row1, textvariable=self.tipo_reporte_var,
                                       values=tipos_reporte, width=15)
        self.combo_tipo.pack(side="left")
        self.combo_tipo.bind("<<ComboboxSelected>>", self.actualizar_campos_fecha)

        # Año
        ttk.Label(row1, text="Año:").pack(side="left", padx=(15, 5))

        # Obtener año actual
        anio_actual = datetime.date.today().year
        anios = list(range(anio_actual - 5, anio_actual + 1))

        self.anio_var = StringVar()
        self.anio_var.set(str(anio_actual))

        self.combo_anio = ttk.Combobox(row1, textvariable=self.anio_var,
                                       values=[str(a) for a in anios], width=10)
        self.combo_anio.pack(side="left")

        # Mes (visible solo para reporte mensual)
        ttk.Label(row1, text="Mes:").pack(side="left", padx=(15, 5))

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        self.mes_var = StringVar()
        self.mes_var.set(meses[datetime.date.today().month - 1])

        self.combo_mes = ttk.Combobox(row1, textvariable=self.mes_var,
                                      values=meses, width=15)
        self.combo_mes.pack(side="left")

        # Botón para generar
        btn_frame = ttk.Frame(select_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Generar Reporte",
                   command=self.generar_reporte).pack(side="right")

        # Frame para mostrar reporte
        report_frame = ttk.LabelFrame(frame, text="Vista Previa del Reporte", padding="10")
        report_frame.pack(fill="both", expand=True, pady=10)

        # Widget de texto para mostrar reporte
        self.text_reporte = tk.Text(report_frame, height=15, width=70)
        self.text_reporte.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.text_reporte.yview)
        self.text_reporte.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Frame para gráficos
        self.graph_frame = ttk.LabelFrame(frame, text="Gráficos", padding="10")
        self.graph_frame.pack(fill="both", expand=True, pady=10)

        # Se añadirá el gráfico dinámicamente
        self.graph_container = ttk.Frame(self.graph_frame)
        self.graph_container.pack(fill="both", expand=True)

        # Botones de acción
        btn_frame2 = ttk.Frame(frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Exportar a PDF",
                   command=self.exportar_pdf).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Exportar a Excel",
                   command=self.exportar_excel).pack(side="left")

    def actualizar_campos_fecha(self, event=None):
        """Actualiza la visibilidad de los campos de fecha según el tipo de reporte"""
        if self.tipo_reporte_var.get() == "Mensual":
            self.combo_mes.config(state="readonly")
        else:
            self.combo_mes.config(state="disabled")

    def obtener_numero_mes(self, nombre_mes):
        """Convierte el nombre del mes a su número correspondiente"""
        meses = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
                 "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
        return meses.get(nombre_mes, 1)

    def obtener_nombre_mes(self, numero_mes):
        """Convierte el número del mes a su nombre correspondiente"""
        meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
        return meses.get(numero_mes, "")

    def generar_reporte(self):
        """Genera y muestra el reporte según los parámetros seleccionados"""
        tipo_reporte = self.tipo_reporte_var.get()

        try:
            anio = int(self.anio_var.get())
            if tipo_reporte == "Mensual":
                mes = self.obtener_numero_mes(self.mes_var.get())
            else:
                mes = None
        except (ValueError, KeyError):
            messagebox.showerror("Error", "Por favor selecciona valores válidos para año y mes.")
            return

        # Obtener datos desde la base de datos
        total_ingresos = 0
        ingresos_por_mes = {i: 0 for i in range(1, 13)} if tipo_reporte == "Anual" else {}

        total_gastos = {"Servicios Públicos": 0, "Impuestos": 0, "Mantenimiento": 0,
                        "Reparaciones": 0, "Otros": 0}
        gastos_por_mes = {i: 0 for i in range(1, 13)} if tipo_reporte == "Anual" else {}

        # Conectar a la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        # Consultar ingresos
        if tipo_reporte == "Mensual":
            cursor.execute("""
                SELECT SUM(monto) FROM pagos
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (str(anio), f"{mes:02d}"))

            result = cursor.fetchone()
            if result[0]:
                total_ingresos = result[0]
        else:  # Anual
            cursor.execute("""
                SELECT strftime('%m', fecha) as mes, SUM(monto) 
                FROM pagos
                WHERE strftime('%Y', fecha) = ?
                GROUP BY mes
            """, (str(anio),))

            for row in cursor.fetchall():
                mes_num = int(row[0])
                ingresos_por_mes[mes_num] = row[1]
                total_ingresos += row[1]

        # Consultar gastos
        if tipo_reporte == "Mensual":
            cursor.execute("""
                SELECT tipo, SUM(monto) FROM gastos
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
                GROUP BY tipo
            """, (str(anio), f"{mes:02d}"))

            for tipo, monto in cursor.fetchall():
                if tipo in total_gastos:
                    total_gastos[tipo] = monto
        else:  # Anual
            # Total por tipo
            cursor.execute("""
                SELECT tipo, SUM(monto) FROM gastos
                WHERE strftime('%Y', fecha) = ?
                GROUP BY tipo
            """, (str(anio),))

            for tipo, monto in cursor.fetchall():
                if tipo in total_gastos:
                    total_gastos[tipo] = monto

            # Por mes para el gráfico
            cursor.execute("""
                SELECT strftime('%m', fecha) as mes, SUM(monto) 
                FROM gastos
                WHERE strftime('%Y', fecha) = ?
                GROUP BY mes
            """, (str(anio),))

            for row in cursor.fetchall():
                mes_num = int(row[0])
                gastos_por_mes[mes_num] = row[1]

        conn.close()

        # Calcular totales
        total_gastos_sum = sum(total_gastos.values())
        balance = total_ingresos - total_gastos_sum

        # Guardar datos del reporte actual
        self.current_report_data = {
            'tipo': tipo_reporte,
            'anio': anio,
            'mes': mes,
            'total_ingresos': total_ingresos,
            'total_gastos': total_gastos,
            'total_gastos_sum': total_gastos_sum,
            'balance': balance,
            'ingresos_por_mes': ingresos_por_mes,
            'gastos_por_mes': gastos_por_mes
        }

        # Mostrar reporte en el widget de texto
        self.text_reporte.config(state='normal')
        self.text_reporte.delete(1.0, tk.END)

        if tipo_reporte == "Mensual":
            nombre_mes = self.mes_var.get()
            self.text_reporte.insert(tk.END, f"--- REPORTE DEL MES DE {nombre_mes.upper()} {anio} ---\n\n")
        else:
            self.text_reporte.insert(tk.END, f"--- REPORTE ANUAL {anio} ---\n\n")

        self.text_reporte.insert(tk.END, f"Ingresos totales: ${total_ingresos:.2f}\n\n")
        self.text_reporte.insert(tk.END, f"Gastos por categoría:\n")

        for tipo, monto in total_gastos.items():
            if monto > 0:  # Solo mostrar categorías con gastos
                self.text_reporte.insert(tk.END, f"  {tipo}: ${monto:.2f}\n")

        self.text_reporte.insert(tk.END, f"\nTotal gastos: ${total_gastos_sum:.2f}\n")
        self.text_reporte.insert(tk.END, f"\nBALANCE: ${balance:.2f}\n")

        # Colorear el balance según sea positivo o negativo
        self.text_reporte.tag_configure("positivo", foreground="green")
        self.text_reporte.tag_configure("negativo", foreground="red")

        balance_line = self.text_reporte.get("end-2l", "end-1l")
        self.text_reporte.delete("end-2l", "end-1l")

        if balance >= 0:
            self.text_reporte.insert(tk.END, balance_line, "positivo")
        else:
            self.text_reporte.insert(tk.END, balance_line, "negativo")

        self.text_reporte.config(state='disabled')

        # Generar gráfico
        self.generar_grafico()

    def generar_grafico(self):
        """Genera y muestra gráficos según el tipo de reporte"""
        if not self.current_report_data:
            return

        # Limpiar gráfico anterior
        for widget in self.graph_container.winfo_children():
            widget.destroy()

        # Crear nueva figura
        fig = plt.Figure(figsize=(8, 4))

        if self.current_report_data['tipo'] == "Mensual":
            # Gráfico de pastel para gastos mensuales
            ax = fig.add_subplot(111)

            # Filtrar solo categorías con gastos
            gastos_filtrados = {k: v for k, v in self.current_report_data['total_gastos'].items() if v > 0}

            if gastos_filtrados:
                labels = list(gastos_filtrados.keys())
                sizes = list(gastos_filtrados.values())

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                ax.set_title(f'Distribución de Gastos - {self.mes_var.get()} {self.current_report_data["anio"]}')
            else:
                ax.text(0.5, 0.5, "No hay datos de gastos para mostrar", ha='center', va='center')
                ax.axis('off')
        else:
            # Gráfico de barras para ingresos vs gastos anuales
            ax = fig.add_subplot(111)

            meses = range(1, 13)
            ingresos = [self.current_report_data['ingresos_por_mes'].get(m, 0) for m in meses]
            gastos = [self.current_report_data['gastos_por_mes'].get(m, 0) for m in meses]

            etiquetas_meses = [self.obtener_nombre_mes(m) for m in meses]

            x = range(len(meses))
            ancho = 0.35

            ax.bar([i - ancho / 2 for i in x], ingresos, ancho, label='Ingresos')
            ax.bar([i + ancho / 2 for i in x], gastos, ancho, label='Gastos')

            ax.set_ylabel('Monto ($)')
            ax.set_title(f'Ingresos vs Gastos por Mes - {self.current_report_data["anio"]}')
            ax.set_xticks(x)
            ax.set_xticklabels(etiquetas_meses, rotation=45, ha='right')
            ax.legend()

            # Ajustar layout
            fig.tight_layout()

        # Mostrar gráfico en la interfaz
        canvas = FigureCanvasTkAgg(fig, self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exportar_pdf(self):
        """Exporta el reporte actual a PDF"""
        if not self.current_report_data:
            messagebox.showwarning("Sin datos", "Primero debes generar un reporte.")
            return

        # Crear nombre de archivo
        if self.current_report_data['tipo'] == "Mensual":
            nombre_mes = self.obtener_nombre_mes(self.current_report_data['mes'])
            nombre_archivo = f"reporte_{self.current_report_data['anio']}_{nombre_mes}.pdf"
        else:
            nombre_archivo = f"reporte_anual_{self.current_report_data['anio']}.pdf"

        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        ancho, alto = letter

        # Título
        c.setFont("Helvetica-Bold", 16)
        if self.current_report_data['tipo'] == "Mensual":
            nombre_mes = self.obtener_nombre_mes(self.current_report_data['mes'])
            titulo = f"REPORTE DEL MES DE {nombre_mes.upper()} {self.current_report_data['anio']}"
        else:
            titulo = f"REPORTE ANUAL {self.current_report_data['anio']}"

        c.drawCentredString(ancho / 2, alto - 40, titulo)

        # Fecha de generación
        c.setFont("Helvetica", 10)
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawRightString(ancho - 50, alto - 60, f"Generado: {fecha_actual}")

        # Contenido
        y = alto - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "RESUMEN FINANCIERO")
        y -= 20

        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Ingresos totales: ${self.current_report_data['total_ingresos']:.2f}")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Gastos por categoría:")
        y -= 20

        c.setFont("Helvetica", 12)
        for tipo, monto in self.current_report_data['total_gastos'].items():
            if monto > 0:  # Solo mostrar categorías con gastos
                c.drawString(70, y, f"{tipo}: ${monto:.2f}")
                y -= 15

        y -= 10
        c.drawString(50, y, f"Total gastos: ${self.current_report_data['total_gastos_sum']:.2f}")
        y -= 20

        # Balance con color
        balance = self.current_report_data['balance']
        if balance >= 0:
            c.setFillColorRGB(0, 0.5, 0)  # Verde
        else:
            c.setFillColorRGB(0.8, 0, 0)  # Rojo

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"BALANCE: ${balance:.2f}")
        c.setFillColorRGB(0, 0, 0)  # Volver a negro

        # Añadir gráfico si hay datos
        if self.current_report_data['tipo'] == "Mensual":
            # Solo añadir gráfico si hay gastos
            gastos_filtrados = {k: v for k, v in self.current_report_data['total_gastos'].items() if v > 0}
            if gastos_filtrados:
                fig = plt.Figure(figsize=(6, 4))
                ax = fig.add_subplot(111)

                labels = list(gastos_filtrados.keys())
                sizes = list(gastos_filtrados.values())

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')

                # Guardar temporalmente y añadir al PDF
                fig.savefig("temp_chart.png")
                c.drawImage("temp_chart.png", 50, y - 300, width=400, height=250)

                # Eliminar archivo temporal
                try:
                    os.remove("temp_chart.png")
                except:
                    pass
        else:
            # Gráfico de barras para reporte anual
            fig = plt.Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)

            meses = range(1, 13)
            ingresos = [self.current_report_data['ingresos_por_mes'].get(m, 0) for m in meses]
            gastos = [self.current_report_data['gastos_por_mes'].get(m, 0) for m in meses]

            etiquetas_meses = [self.obtener_nombre_mes(m)[:3] for m in meses]  # Abreviar nombres

            x = range(len(meses))
            ancho = 0.35

            ax.bar([i - ancho / 2 for i in x], ingresos, ancho, label='Ingresos')
            ax.bar([i + ancho / 2 for i in x], gastos, ancho, label='Gastos')

            ax.set_ylabel('Monto ($)')
            ax.set_xticks(x)
            ax.set_xticklabels(etiquetas_meses)
            ax.legend()

            # Guardar temporalmente y añadir al PDF
            fig.savefig("temp_chart.png")
            c.drawImage("temp_chart.png", 50, y - 300, width=500, height=250)

            # Eliminar archivo temporal
            try:
                os.remove("temp_chart.png")
            except:
                pass

        # Guardar PDF
        c.save()
        messagebox.showinfo("PDF Generado", f"El reporte se ha guardado como: {nombre_archivo}")

        # Abrir el PDF
        try:
            os.startfile(nombre_archivo)
        except:
            pass

    def exportar_excel(self):
        """Exporta el reporte actual a Excel"""
        if not self.current_report_data:
            messagebox.showwarning("Sin datos", "Primero debes generar un reporte.")
            return

        # Crear nombre de archivo
        if self.current_report_data['tipo'] == "Mensual":
            nombre_mes = self.obtener_nombre_mes(self.current_report_data['mes'])
            nombre_archivo = f"reporte_{self.current_report_data['anio']}_{nombre_mes}.xlsx"
        else:
            nombre_archivo = f"reporte_anual_{self.current_report_data['anio']}.xlsx"

        # Crear DataFrame para el resumen
        resumen_data = {
            'Concepto': ['Ingresos Totales'] +
                        [f"Gastos - {tipo}" for tipo in self.current_report_data['total_gastos'].keys()] +
                        ['Total Gastos', 'Balance'],
            'Monto': [self.current_report_data['total_ingresos']] +
                     list(self.current_report_data['total_gastos'].values()) +
                     [self.current_report_data['total_gastos_sum'], self.current_report_data['balance']]
        }

        df_resumen = pd.DataFrame(resumen_data)

        # Crear DataFrames adicionales según el tipo de reporte
        if self.current_report_data['tipo'] == "Anual":
            # Datos mensuales
            meses = range(1, 13)
            nombres_meses = [self.obtener_nombre_mes(m) for m in meses]

            ingresos = [self.current_report_data['ingresos_por_mes'].get(m, 0) for m in meses]
            gastos = [self.current_report_data['gastos_por_mes'].get(m, 0) for m in meses]
            balance = [ingresos[i] - gastos[i] for i in range(len(meses))]

            df_mensual = pd.DataFrame({
                'Mes': nombres_meses,
                'Ingresos': ingresos,
                'Gastos': gastos,
                'Balance': balance
            })

            # Crear Excel con múltiples hojas
            with pd.ExcelWriter(nombre_archivo) as writer:
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                df_mensual.to_excel(writer, sheet_name='Detalle Mensual', index=False)
        else:
            # Solo crear la hoja de resumen para reporte mensual
            df_resumen.to_excel(nombre_archivo, sheet_name='Resumen', index=False)

        messagebox.showinfo("Excel Generado", f"El reporte se ha guardado como: {nombre_archivo}")

        # Abrir el Excel
        try:
            os.startfile(nombre_archivo)
        except:
            pass

class ApartmentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Edificio")
        self.root.geometry("800x600")

        # Inicializar base de datos
        self.setup_database()

        # Configurar módulos
        self.tenant_module = TenantModule(self)
        self.payment_module = PaymentModule(self)
        self.expense_module = ExpenseModule(self)
        self.report_module = ReportModule(self)

        # Configurar interfaz
        self.setup_ui()

    def setup_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        # Tabla de inquilinos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquilinos (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            apartamento TEXT,
            renta REAL
        )
        ''')

        # Tabla de pagos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY,
            fecha TEXT,
            inquilino_id INTEGER,
            monto REAL,
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos (id)
        )
        ''')

        # Tabla de gastos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY,
            fecha TEXT,
            tipo TEXT,
            descripcion TEXT,
            monto REAL
        )
        ''')

        conn.commit()
        conn.close()

        # Migrar datos existentes si existen archivos CSV
        self.migrar_datos_csv_a_sqlite()

    def migrar_datos_csv_a_sqlite(self):
        """Migra los datos de archivos CSV a SQLite si existen"""
        # Migrar inquilinos
        if os.path.exists("inquilinos.csv"):
            try:
                conn = sqlite3.connect('edificio.db')
                cursor = conn.cursor()

                with open("inquilinos.csv", "r") as archivo:
                    import csv
                    lector = csv.reader(archivo)
                    for fila in lector:
                        if len(fila) >= 3:
                            # Verificar si ya existe el inquilino
                            cursor.execute("SELECT id FROM inquilinos WHERE nombre=? AND apartamento=?",
                                           (fila[0], fila[1]))
                            if not cursor.fetchone():
                                cursor.execute("INSERT INTO inquilinos (nombre, apartamento, renta) VALUES (?, ?, ?)",
                                               (fila[0], fila[1], float(fila[2])))

                # Migrar pagos si existe el archivo
                if os.path.exists("pagos.csv"):
                    with open("pagos.csv", "r") as archivo:
                        lector = csv.reader(archivo)
                        for fila in lector:
                            if len(fila) >= 3:
                                fecha = fila[0]
                                inquilino_info = fila[1]
                                monto = float(fila[2])

                                # Extraer nombre del inquilino
                                if " - Apto " in inquilino_info:
                                    nombre, _ = inquilino_info.split(" - Apto ")
                                    cursor.execute("SELECT id FROM inquilinos WHERE nombre=?", (nombre,))
                                    inquilino_id = cursor.fetchone()

                                    if inquilino_id:
                                        cursor.execute(
                                            "INSERT INTO pagos (fecha, inquilino_id, monto) VALUES (?, ?, ?)",
                                            (fecha, inquilino_id[0], monto))

                # Migrar gastos si existe el archivo
                if os.path.exists("gastos.csv"):
                    with open("gastos.csv", "r") as archivo:
                        lector = csv.reader(archivo)
                        for fila in lector:
                            if len(fila) >= 4:
                                fecha = fila[0]
                                tipo = fila[1]
                                descripcion = fila[2]
                                monto = float(fila[3])

                                cursor.execute(
                                    "INSERT INTO gastos (fecha, tipo, descripcion, monto) VALUES (?, ?, ?, ?)",
                                    (fecha, tipo, descripcion, monto))

                conn.commit()
                conn.close()

                # Crear respaldo de archivos CSV originales
                self.crear_respaldo()
            except Exception as e:
                messagebox.showerror("Error en migración", f"Error al migrar datos: {str(e)}")

    def crear_respaldo(self):
        """Crea un respaldo de los archivos de datos"""
        fecha = datetime.datetime.now().strftime("%Y%m%d")
        carpeta_respaldo = f"respaldo_{fecha}"

        if not os.path.exists(carpeta_respaldo):
            os.makedirs(carpeta_respaldo)

        for archivo in ["inquilinos.csv", "pagos.csv", "gastos.csv"]:
            if os.path.exists(archivo):
                shutil.copy2(archivo, os.path.join(carpeta_respaldo, archivo))

    def setup_ui(self):
        """Configura la interfaz principal con pestañas"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Etiqueta principal
        header_label = ttk.Label(main_frame, text="Panel de Control del Edificio",
                                 font=("Helvetica", 16))
        header_label.pack(pady=10)

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)

        # Crear pestañas
        self.tab_inquilinos = ttk.Frame(self.notebook)
        self.tab_pagos = ttk.Frame(self.notebook)
        self.tab_gastos = ttk.Frame(self.notebook)
        self.tab_reportes = ttk.Frame(self.notebook)

        # Añadir pestañas al notebook
        self.notebook.add(self.tab_inquilinos, text='Inquilinos')
        self.notebook.add(self.tab_pagos, text='Pagos')
        self.notebook.add(self.tab_gastos, text='Gastos')
        self.notebook.add(self.tab_reportes, text='Reportes')

        self.notebook.pack(expand=True, fill="both")

        # Configurar contenido de las pestañas
        self.tenant_module.setup_ui(self.tab_inquilinos)
        self.payment_module.setup_ui(self.tab_pagos)
        self.expense_module.setup_ui(self.tab_gastos)
        self.report_module.setup_ui(self.tab_reportes)

        # Botón de respaldo en la parte inferior
        backup_frame = ttk.Frame(main_frame)
        backup_frame.pack(fill="x", pady=5)

        ttk.Button(backup_frame, text="Crear Respaldo de Datos",
                   command=self.crear_respaldo).pack(side="right")

# Función principal
def main():
    root = tk.Tk()
    app = ApartmentManager(root)
    root.mainloop()

# Llamada a la función principal
if __name__ == "__main__":
    main()