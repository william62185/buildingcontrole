import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, StringVar, filedialog
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
import zipfile
import json
from pathlib import Path
from tkcalendar import DateEntry

# Define la clase TenantModule primero
class TenantModule:
    def __init__(self, manager):
        self.manager = manager

    def setup_ui(self, parent):
        """Configura la interfaz de gestión de inquilinos"""
        # Crear canvas y scrollbar para scroll vertical
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Ahora usar scrollable_frame en lugar de parent
        frame = ttk.Frame(scrollable_frame, padding="10")
        frame.pack(fill="both", expand=True)

        # === DASHBOARD CON ESTADÍSTICAS ===
        dashboard_frame = ttk.LabelFrame(frame, text="📊 Dashboard - Vista General", padding="15")
        dashboard_frame.pack(fill="x", pady=(0, 10))

        # Frame para las cards de estadísticas
        stats_frame = ttk.Frame(dashboard_frame)
        stats_frame.pack(fill="x", pady=(0, 10))

        # Configurar grid para las cards
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        # Card 1: Total Inquilinos
        self.total_card = ttk.LabelFrame(stats_frame, text="👥 Total Inquilinos", padding="10")
        self.total_card.grid(row=0, column=0, padx=5, sticky="ew")
        self.total_label = ttk.Label(self.total_card, text="0", font=("Segoe UI", 20, "bold"), foreground="#2c3e50")
        self.total_label.pack()

        # Card 2: Inquilinos Activos
        self.active_card = ttk.LabelFrame(stats_frame, text="✅ Activos", padding="10")
        self.active_card.grid(row=0, column=1, padx=5, sticky="ew")
        self.active_label = ttk.Label(self.active_card, text="0", font=("Segoe UI", 20, "bold"), foreground="#27ae60")
        self.active_label.pack()

        # Card 3: Pendientes/Problemas
        self.pending_card = ttk.LabelFrame(stats_frame, text="⚠️ Pendientes", padding="10")
        self.pending_card.grid(row=0, column=2, padx=5, sticky="ew")
        self.pending_label = ttk.Label(self.pending_card, text="0", font=("Segoe UI", 20, "bold"), foreground="#f39c12")
        self.pending_label.pack()

        # Card 4: Renta Total Mensual
        self.rent_card = ttk.LabelFrame(stats_frame, text="💰 Renta Total/Mes", padding="10")
        self.rent_card.grid(row=0, column=3, padx=5, sticky="ew")
        self.rent_label = ttk.Label(self.rent_card, text="$0", font=("Segoe UI", 16, "bold"), foreground="#8e44ad")
        self.rent_label.pack()

        # Botón de actualizar estadísticas
        refresh_btn = ttk.Button(dashboard_frame, text="🔄 Actualizar Estadísticas",
                                 command=self.actualizar_estadisticas)
        refresh_btn.pack(pady=(5, 0))

        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            # Solo funcionar si no hay ventanas modales activas Y no está el scroll del listado activo
            add_modal_active = getattr(self, '_add_modal_active', False)
            details_modal_active = getattr(self, '_details_modal_active', False)
            tree_scroll_active = getattr(self, '_tree_scroll_active', False)

            if not add_modal_active and not details_modal_active and not tree_scroll_active:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # === CARD PARA AGREGAR NUEVO INQUILINO ===
        add_card_frame = ttk.Frame(frame)
        add_card_frame.pack(fill="x", pady=10)

        # Card clickeable para agregar inquilino
        self.add_tenant_card = tk.Frame(add_card_frame,
                                        bg="#e8f4f8",
                                        relief="raised",
                                        bd=2,
                                        cursor="hand2")
        self.add_tenant_card.pack(fill="x", padx=20, pady=10)

        # Contenido del card
        card_content = tk.Frame(self.add_tenant_card, bg="#e8f4f8")
        card_content.pack(fill="x", padx=30, pady=20)

        # Icono grande
        icon_label = tk.Label(card_content,
                              text="👥 ➕",
                              font=("Segoe UI", 32),
                              bg="#e8f4f8",
                              fg="#2c3e50")
        icon_label.pack()

        # Título principal
        title_label = tk.Label(card_content,
                               text="AGREGAR NUEVO INQUILINO",
                               font=("Segoe UI", 14, "bold"),
                               bg="#e8f4f8",
                               fg="#2c3e50")
        title_label.pack(pady=(5, 2))

        # Subtítulo
        subtitle_label = tk.Label(card_content,
                                  text="Click aquí para registrar un nuevo arrendatario",
                                  font=("Segoe UI", 10),
                                  bg="#e8f4f8",
                                  fg="#5a6c7d")
        subtitle_label.pack()

        # Efectos hover mejorados
        def on_enter(event):
            # Colores más vibrantes y profesionales
            hover_bg = "#b8e6ff"  # Azul más vibrante
            hover_border = "#007acc"  # Borde azul oscuro

            self.add_tenant_card.config(
                bg=hover_bg,
                relief="solid",
                bd=2,
                highlightbackground=hover_border,
                highlightthickness=1
            )
            card_content.config(bg=hover_bg)

            # Cambiar colores del texto para mayor contraste
            icon_label.config(bg=hover_bg, fg="#0056b3")  # Icono más oscuro
            title_label.config(bg=hover_bg, fg="#0056b3")  # Título más oscuro
            subtitle_label.config(bg=hover_bg, fg="#495057")  # Subtítulo más legible

            # Efecto de "elevación" visual
            self.add_tenant_card.configure(cursor="hand2")

        def on_leave(event):
            # Colores originales suaves
            original_bg = "#e8f4f8"

            self.add_tenant_card.config(
                bg=original_bg,
                relief="raised",
                bd=2,
                highlightthickness=0
            )
            card_content.config(bg=original_bg)

            # Restaurar colores originales
            icon_label.config(bg=original_bg, fg="#2c3e50")
            title_label.config(bg=original_bg, fg="#2c3e50")
            subtitle_label.config(bg=original_bg, fg="#5a6c7d")

            self.add_tenant_card.configure(cursor="hand2")

        # Efecto adicional para click
        def on_click_effect(event):
            # Efecto visual al hacer click
            click_bg = "#a0d8ff"
            self.add_tenant_card.config(bg=click_bg, relief="sunken", bd=1)
            card_content.config(bg=click_bg)
            icon_label.config(bg=click_bg)
            title_label.config(bg=click_bg)
            subtitle_label.config(bg=click_bg)

            # Restaurar después de un momento
            self.add_tenant_card.after(100, lambda: on_enter(None))

        def on_click(event):
            on_click_effect(event)  # Efecto visual primero
            self.add_tenant_card.after(120, self.mostrar_formulario_agregar)  # Pequeño delay

        # Bind eventos
        self.add_tenant_card.bind("<Enter>", on_enter)
        self.add_tenant_card.bind("<Leave>", on_leave)
        self.add_tenant_card.bind("<Button-1>", on_click)
        card_content.bind("<Button-1>", on_click)
        icon_label.bind("<Button-1>", on_click)
        title_label.bind("<Button-1>", on_click)
        subtitle_label.bind("<Button-1>", on_click)

        # Frame para el formulario (inicialmente oculto)
        self.form_frame = ttk.LabelFrame(frame, text="📝 Registrar Nuevo Inquilino", padding="15")
        self.form_visible = False

        # Frame de búsqueda avanzada
        search_frame = ttk.LabelFrame(frame, text="🔍 Búsqueda y Filtros Avanzados", padding="15")
        search_frame.pack(fill="x", pady=10)

        # Fila 1: Búsqueda general
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill="x", pady=5)

        ttk.Label(search_row1, text="🔍 Buscar:").pack(side="left", padx=(0, 5))
        self.entry_buscar = ttk.Entry(search_row1, width=25)
        self.entry_buscar.pack(side="left", padx=(0, 10))
        self.entry_buscar.bind("<KeyRelease>", self.on_search_key_release)

        ttk.Button(search_row1, text="🔍 Buscar", command=self.aplicar_filtros).pack(side="left", padx=(0, 10))
        ttk.Button(search_row1, text="🗑️ Limpiar", command=self.limpiar_filtros).pack(side="left")

        # Fila 2: Filtros específicos
        filters_row = ttk.Frame(search_frame)
        filters_row.pack(fill="x", pady=10)

        # Filtro por Estado
        ttk.Label(filters_row, text="📊 Estado:").pack(side="left", padx=(0, 5))
        self.filtro_estado = ttk.Combobox(filters_row, width=12,
                                          values=["Todos", "Activo", "Pendiente", "Inactivo", "Moroso", "Suspendido"])
        self.filtro_estado.set("Todos")
        self.filtro_estado.pack(side="left", padx=(0, 15))
        self.filtro_estado.bind("<<ComboboxSelected>>", self.on_filter_change)

        # Filtro por Rango de Renta
        ttk.Label(filters_row, text="💰 Renta:").pack(side="left", padx=(0, 5))
        self.filtro_renta_min = ttk.Entry(filters_row, width=10)
        self.filtro_renta_min.pack(side="left", padx=(0, 5))
        self.filtro_renta_min.insert(0, "Min")
        self.filtro_renta_min.bind("<FocusIn>", self.clear_placeholder)
        self.filtro_renta_min.bind("<KeyRelease>", self.on_filter_change)

        ttk.Label(filters_row, text="-").pack(side="left", padx=2)

        self.filtro_renta_max = ttk.Entry(filters_row, width=10)
        self.filtro_renta_max.pack(side="left", padx=(5, 15))
        self.filtro_renta_max.insert(0, "Max")
        self.filtro_renta_max.bind("<FocusIn>", self.clear_placeholder)
        self.filtro_renta_max.bind("<KeyRelease>", self.on_filter_change)

        # Filtro por Apartamento
        ttk.Label(filters_row, text="🏠 Apto:").pack(side="left", padx=(0, 5))
        self.filtro_apartamento = ttk.Entry(filters_row, width=10)
        self.filtro_apartamento.pack(side="left")
        self.filtro_apartamento.bind("<KeyRelease>", self.on_filter_change)

        # Lista de inquilinos
        list_frame = ttk.LabelFrame(frame, text="Lista de Inquilinos", padding="10")
        list_frame.pack(fill="both", expand=True, pady=10)

        # Treeview para mostrar inquilinos con más columnas
        columns = ("id", "nombre", "apartamento", "identificacion", "email", "celular", "estado", "renta")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apartamento", text="Apto")
        self.tree.heading("identificacion", text="Identificación")
        self.tree.heading("email", text="Email")
        self.tree.heading("celular", text="Celular")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("renta", text="Renta")

        # Ajustar anchos de columna
        self.tree.column("id", width=40)
        self.tree.column("nombre", width=150)
        self.tree.column("apartamento", width=50)
        self.tree.column("identificacion", width=120)
        self.tree.column("email", width=180)
        self.tree.column("celular", width=100)
        self.tree.column("estado", width=80)
        self.tree.column("renta", width=90)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === SCROLL ESPECÍFICO PARA EL LISTADO ===
        def tree_mousewheel(event):
            """Scroll específico para el treeview"""
            try:
                # Obtener la región visible del treeview
                if self.tree.winfo_exists():
                    # Hacer scroll del treeview
                    self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    return "break"  # Detener propagación
            except Exception as e:
                logging.error(f"Error en scroll del treeview: {e}")

        def on_tree_enter(event):
            """Al entrar al área del listado"""
            try:
                # Deshabilitar scroll principal temporalmente
                self._tree_scroll_active = True

                # Activar scroll específico del treeview
                self.tree.bind("<MouseWheel>", tree_mousewheel)
                list_frame.bind("<MouseWheel>", tree_mousewheel)

                # Cambiar cursor para indicar que el scroll está activo
                self.tree.configure(cursor="arrow")

            except Exception as e:
                logging.error(f"Error activando scroll del listado: {e}")

        def on_tree_leave(event):
            """Al salir del área del listado"""
            try:
                # Reactivar scroll principal
                self._tree_scroll_active = False

                # Desactivar scroll específico del treeview
                self.tree.unbind("<MouseWheel>")
                list_frame.unbind("<MouseWheel>")

            except Exception as e:
                logging.error(f"Error desactivando scroll del listado: {e}")

        # Bind eventos al frame del listado y al treeview
        list_frame.bind("<Enter>", on_tree_enter)
        list_frame.bind("<Leave>", on_tree_leave)
        self.tree.bind("<Enter>", on_tree_enter)
        self.tree.bind("<Leave>", on_tree_leave)

        # Variable de control
        self._tree_scroll_active = False

        # Botones de acción
        btn_frame2 = ttk.Frame(frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="👁️ Ver Detalles",
                   command=self.ver_detalles_inquilino).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="✏️ Editar Seleccionado",
                   command=self.editar_inquilino).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="🗑️ Eliminar Seleccionado",
                   command=self.eliminar_inquilino).pack(side="left")

        # Cargar inquilinos al inicio
        self.cargar_inquilinos()

    def cargar_inquilinos(self):
        """Carga todos los inquilinos desde la base de datos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar datos con los nuevos campos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, apartamento, identificacion, email, celular, estado, renta 
            FROM inquilinos 
            ORDER BY 
                CASE 
                    WHEN estado = 'Activo' THEN 1
                    WHEN estado = 'Pendiente' THEN 2
                    WHEN estado = 'Moroso' THEN 3
                    WHEN estado = 'Suspendido' THEN 4
                    ELSE 5
                END,
                apartamento
        """)

        for row in cursor.fetchall():
            # Convertir None a string vacío para mejor visualización
            row_display = []
            for item in row:
                if item is None:
                    row_display.append("")
                else:
                    row_display.append(item)

            self.tree.insert("", "end", values=row_display)

        conn.close()

        # Actualizar estadísticas automáticamente
        self.actualizar_estadisticas()

    def guardar_inquilino(self):
        """Guarda un nuevo inquilino en la base de datos con todos los campos"""
        # Obtener valores de todos los campos
        nombre = self.entry_nombre.get().strip()
        identificacion = self.entry_identificacion.get().strip()
        email = self.entry_email.get().strip()
        celular = self.entry_celular.get().strip()
        profesion = self.entry_profesion.get().strip()
        apto = self.entry_apto.get().strip()
        renta = self.entry_renta.get().strip()
        estado = self.combo_estado.get()
        fecha_ingreso = self.entry_fecha_ingreso.get().strip()
        deposito = self.entry_deposito.get().strip()
        contacto_emergencia = self.entry_contacto_emergencia.get().strip()
        telefono_emergencia = self.entry_telefono_emergencia.get().strip()
        relacion_emergencia = self.combo_relacion.get()
        notas = self.text_notas.get(1.0, tk.END).strip()

        # Validaciones básicas obligatorias
        if not nombre:
            messagebox.showwarning("Campo requerido", "El nombre es obligatorio.")
            self.entry_nombre.focus()
            return

        if not apto:
            messagebox.showwarning("Campo requerido", "El apartamento es obligatorio.")
            self.entry_apto.focus()
            return

        if not renta:
            messagebox.showwarning("Campo requerido", "La renta es obligatoria.")
            self.entry_renta.focus()
            return

        # Validación de renta
        try:
            renta = float(renta)
            if renta <= 0:
                messagebox.showerror("Error", "La renta debe ser un número positivo.")
                self.entry_renta.focus()
                return
        except ValueError:
            messagebox.showerror("Error", "La renta debe ser un número válido.")
            self.entry_renta.focus()
            return

        # Validación de depósito (opcional pero si se ingresa debe ser válido)
        deposito_valor = 0
        if deposito:
            try:
                deposito_valor = float(deposito)
                if deposito_valor < 0:
                    messagebox.showerror("Error", "El depósito no puede ser negativo.")
                    self.entry_deposito.focus()
                    return
            except ValueError:
                messagebox.showerror("Error", "El depósito debe ser un número válido.")
                self.entry_deposito.focus()
                return

        # Validación de email (opcional pero si se ingresa debe ser válido)
        if email and '@' not in email:
            messagebox.showwarning("Email inválido", "Por favor ingresa un email válido.")
            self.entry_email.focus()
            return

        # Validación de fecha (opcional pero si se ingresa debe ser válida)
        if fecha_ingreso:
            try:
                datetime.datetime.fromisoformat(fecha_ingreso)
            except ValueError:
                messagebox.showerror("Fecha inválida", "Formato de fecha debe ser YYYY-MM-DD.")
                self.entry_fecha_ingreso.focus()
                return

        # Verificar que no existe otro inquilino con la misma identificación (si se proporciona)
        if identificacion:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM inquilinos WHERE identificacion = ? AND identificacion != ''",
                           (identificacion,))
            resultado = cursor.fetchone()
            if resultado:
                messagebox.showerror("Identificación duplicada",
                                     f"Ya existe un inquilino con la identificación {identificacion}: {resultado[0]}")
                conn.close()
                self.entry_identificacion.focus()
                return
            conn.close()

        # Verificar que no existe otro inquilino en el mismo apartamento activo
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM inquilinos WHERE apartamento = ? AND estado = 'Activo'", (apto,))
        resultado = cursor.fetchone()
        if resultado:
            if not messagebox.askyesno("Apartamento ocupado",
                                       f"El apartamento {apto} ya tiene un inquilino activo: {resultado[0]}\n"
                                       f"¿Deseas continuar de todas formas?"):
                conn.close()
                self.entry_apto.focus()
                return

        try:
            # Guardar en la base de datos
            cursor.execute("""
                INSERT INTO inquilinos (
                    nombre, identificacion, email, celular, profesion,
                    apartamento, renta, estado, fecha_ingreso, deposito,
                    contacto_emergencia, telefono_emergencia, relacion_emergencia, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, identificacion, email, celular, profesion,
                  apto, renta, estado, fecha_ingreso, deposito_valor,
                  contacto_emergencia, telefono_emergencia, relacion_emergencia, notas))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Inquilino {nombre} registrado exitosamente en el apartamento {apto}.")

            # Limpiar el formulario
            self.limpiar_formulario()

            # Recargar lista
            self.cargar_inquilinos()

            # Cerrar formulario automáticamente después de guardar
            if hasattr(self, 'form_visible') and self.form_visible:
                self.ocultar_formulario()

            # Actualizar estadísticas del dashboard
            self.actualizar_estadisticas()

        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Error al guardar: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def buscar_inquilinos(self):
        """Método legacy - redirige a aplicar_filtros"""
        self.aplicar_filtros()

    def on_search_key_release(self, event):
        """Realiza búsqueda al escribir"""
        self.buscar_inquilinos()

    def editar_inquilino(self):
        """Abre ventana modal para editar el inquilino seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un inquilino para editar.")
            return

        # Obtener ID del inquilino seleccionado
        values = self.tree.item(selected[0], "values")
        inquilino_id = values[0]

        # Obtener datos completos de la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, apartamento, renta, identificacion, email, celular, profesion,
                   fecha_ingreso, deposito, estado, contacto_emergencia, telefono_emergencia,
                   relacion_emergencia, notas, archivo_identificacion, archivo_contrato
            FROM inquilinos WHERE id = ?
        """, (inquilino_id,))

        datos = cursor.fetchone()
        conn.close()

        if not datos:
            messagebox.showerror("Error", "No se pudieron cargar los datos del inquilino.")
            return

        # Abrir ventana modal de edición
        self.mostrar_formulario_editar(inquilino_id, datos)

    def mostrar_formulario_editar(self, inquilino_id, datos):
        """Abre ventana modal para editar inquilino con datos pre-cargados"""

        # Marcar que hay ventana modal activa
        self._add_modal_active = True

        # Crear ventana modal
        edit_window = tk.Toplevel()
        edit_window.title(f"✏️ Editar Inquilino - {datos[0]}")
        edit_window.geometry("750x650")
        edit_window.resizable(True, True)
        edit_window.transient(self.manager.root)
        edit_window.grab_set()

        # === SISTEMA DE SCROLL (igual al de agregar) ===
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con rueda del mouse
        def modal_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        edit_window.bind("<MouseWheel>", modal_scroll)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Función de cleanup
        def cleanup_and_close():
            try:
                self._add_modal_active = False
                edit_window.unbind("<MouseWheel>")
                edit_window.destroy()
            except Exception as e:
                logging.error(f"Error en cleanup: {e}")

        # Centrar ventana
        edit_window.update_idletasks()
        width = 750
        height = 650
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = max(50, (edit_window.winfo_screenheight() // 2) - (height // 2) - 50)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')

        # Crear formulario con datos pre-cargados
        self.setup_edit_form_modal(scrollable_frame, edit_window, cleanup_and_close, inquilino_id, datos)

        # Protocolo de cierre
        edit_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)

        # Foco
        edit_window.focus_force()

        logging.info(f"Ventana de edición abierta para inquilino: {datos[0]}")

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

    def ver_detalles_inquilino(self):
        """Muestra todos los detalles del inquilino seleccionado en una ventana profesional"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un inquilino para ver sus detalles.")
            return

        # Obtener ID del inquilino seleccionado
        values = self.tree.item(selected[0], "values")
        inquilino_id = values[0]

        # Obtener datos completos de la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, apartamento, renta, identificacion, email, celular, profesion,
                   fecha_ingreso, deposito, estado, contacto_emergencia, telefono_emergencia,
                   relacion_emergencia, notas, archivo_identificacion, archivo_contrato
            FROM inquilinos WHERE id = ?
        """, (inquilino_id,))

        datos = cursor.fetchone()

        if not datos:
            conn.close()
            messagebox.showerror("Error", "No se pudieron cargar los datos del inquilino.")
            return

        # Obtener información financiera
        cursor.execute("SELECT SUM(monto), COUNT(*) FROM pagos WHERE inquilino_id = ?", (inquilino_id,))
        pago_info = cursor.fetchone()
        total_pagado = pago_info[0] if pago_info[0] else 0
        num_pagos = pago_info[1] if pago_info[1] else 0

        # Último pago
        cursor.execute("SELECT fecha, monto FROM pagos WHERE inquilino_id = ? ORDER BY fecha DESC LIMIT 1",
                       (inquilino_id,))
        ultimo_pago = cursor.fetchone()
        conn.close()

        # Crear ventana de detalles
        details_window = tk.Toplevel()
        details_window.title(f"📋 Detalles Completos - {datos[0]}")
        details_window.geometry("750x700")
        details_window.resizable(True, True)
        details_window.transient(self.manager.root)
        details_window.grab_set()  # Hacer ventana modal

        # Configurar icono si existe
        try:
            details_window.iconbitmap("icon.ico")  # Si tienes un icono
        except:
            pass

        # === CONFIGURACIÓN DE SCROLL SEGURA ===
        def setup_scroll_system():
            """Configura el sistema de scroll de forma segura"""
            # Frame principal
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Canvas con configuración robusta
            canvas = tk.Canvas(main_frame, highlightthickness=0, bg='#f0f0f0')
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            # Configurar canvas
            canvas.configure(yscrollcommand=scrollbar.set)

            # Función para actualizar scroll region
            def configure_scroll_region(event=None):
                if canvas.winfo_exists():
                    canvas.configure(scrollregion=canvas.bbox("all"))

            scrollable_frame.bind("<Configure>", configure_scroll_region)
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Función mejorada para scroll con validación
            def safe_mousewheel(event):
                try:
                    if canvas.winfo_exists() and details_window.winfo_exists():
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                        return "break"  # ← AGREGAR ESTA LÍNEA para evitar propagación
                except tk.TclError:
                    pass  # Ignorar errores si la ventana fue destruida

            # Función para ajustar ancho del canvas window
            def configure_canvas_window(event):
                try:
                    if canvas.winfo_exists():
                        canvas.itemconfig(canvas_window, width=event.width)
                except tk.TclError:
                    pass

            canvas.bind("<Configure>", configure_canvas_window)

            # Sistema de bind/unbind para evitar conflictos
            def bind_scroll():
                try:
                    # Bind tanto al canvas como a la ventana, pero con mejor control
                    canvas.bind("<MouseWheel>", safe_mousewheel)
                    details_window.bind("<MouseWheel>", safe_mousewheel)
                    # Asegurar que el canvas pueda recibir eventos
                    canvas.focus_set()
                except tk.TclError:
                    pass

            def unbind_scroll():
                try:
                    # Unbind de ambos
                    if details_window.winfo_exists():
                        details_window.unbind("<MouseWheel>")
                    if canvas.winfo_exists():
                        canvas.unbind("<MouseWheel>")
                except tk.TclError:
                    pass

            # Control de scroll basado en posición del mouse
            def on_enter_window(event):
                bind_scroll()

            def on_leave_window(event):
                unbind_scroll()

            # Bind a eventos de entrada y salida del mouse
            details_window.bind("<Enter>", on_enter_window)
            details_window.bind("<Leave>", on_leave_window)
            canvas.bind("<Enter>", on_enter_window)
            canvas.bind("<Leave>", on_leave_window)

            # Activar scroll inicial
            bind_scroll()

            # Empaquetar widgets
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            return scrollable_frame, canvas, unbind_scroll

        # Configurar sistema de scroll
        scrollable_frame, canvas, unbind_scroll = setup_scroll_system()

        # === ESTILOS PROFESIONALES ===
        style_config = {
            'header_font': ("Segoe UI", 14, "bold"),
            'label_font': ("Segoe UI", 10, "bold"),
            'value_font': ("Segoe UI", 10),
            'section_font': ("Segoe UI", 12, "bold"),
            'header_color': "#2c3e50",
            'label_color': "#34495e",
            'value_bg': "#ecf0f1",
            'success_color': "#27ae60",
            'warning_color': "#f39c12",
            'danger_color': "#e74c3c"
        }

        # === ENCABEZADO PRINCIPAL ===
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        # Título principal con icono
        title_label = tk.Label(header_frame,
                               text=f"📋 Información Completa del Inquilino",
                               font=style_config['header_font'],
                               fg=style_config['header_color'])
        title_label.pack()

        # Nombre del inquilino destacado
        name_label = tk.Label(header_frame,
                              text=datos[0],
                              font=("Segoe UI", 16, "bold"),
                              fg="#2980b9")
        name_label.pack(pady=(5, 0))

        # Separador
        separator = ttk.Separator(scrollable_frame, orient='horizontal')
        separator.pack(fill="x", pady=10)

        # === INFORMACIÓN PERSONAL ===
        def create_info_section(parent, title, icon, data_pairs, special_formatting=None):
            """Crea una sección de información profesional"""
            section_frame = ttk.LabelFrame(parent, text=f"{icon} {title}", padding="15")
            section_frame.pack(fill="x", pady=(0, 15))

            for i, (label, value) in enumerate(data_pairs):
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill="x", pady=3)

                # Etiqueta
                label_widget = tk.Label(row_frame, text=f"{label}:",
                                        font=style_config['label_font'],
                                        fg=style_config['label_color'],
                                        width=20, anchor='w')
                label_widget.pack(side="left")

                # Valor con formato especial si aplica
                display_value = value or "No especificado"

                if special_formatting and label in special_formatting:
                    display_value = special_formatting[label](value)

                # Determinar color de fondo según el contenido
                bg_color = style_config['value_bg']
                fg_color = style_config['label_color']

                if label == "Estado" and value:
                    if value == "Activo":
                        bg_color = "#d5edda"
                        fg_color = style_config['success_color']
                    elif value in ["Pendiente", "Suspendido"]:
                        bg_color = "#fff3cd"
                        fg_color = style_config['warning_color']
                    elif value == "Moroso":
                        bg_color = "#f8d7da"
                        fg_color = style_config['danger_color']

                value_widget = tk.Label(row_frame, text=display_value,
                                        font=style_config['value_font'],
                                        fg=fg_color, bg=bg_color,
                                        relief="sunken", bd=1,
                                        anchor='w', padx=8, pady=2)
                value_widget.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Formateo especial para algunos campos
        special_format = {
            "Renta mensual": lambda x: f"${float(x):,.0f}" if x else "No especificado",
            "Depósito": lambda x: f"${float(x):,.0f}" if x else "No especificado"
        }

        # Sección de información personal
        personal_data = [
            ("Nombre completo", datos[0]),
            ("Identificación", datos[3]),
            ("Email", datos[4]),
            ("Celular", datos[5]),
            ("Profesión", datos[6])
        ]
        create_info_section(scrollable_frame, "Información Personal", "👤", personal_data)

        # Sección de arrendamiento
        rental_data = [
            ("Apartamento", datos[1]),
            ("Renta mensual", datos[2]),
            ("Estado", datos[9]),
            ("Fecha de ingreso", datos[7]),
            ("Depósito", datos[8])
        ]
        create_info_section(scrollable_frame, "Información del Arrendamiento", "🏠",
                            rental_data, special_format)

        # Sección de contacto de emergencia (solo si hay datos)
        if any([datos[10], datos[11], datos[12]]):
            emergency_data = [
                ("Nombre del contacto", datos[10]),
                ("Teléfono de emergencia", datos[11]),
                ("Relación", datos[12])
            ]
            create_info_section(scrollable_frame, "Contacto de Emergencia", "🚨", emergency_data)

        # Sección financiera
        financial_format = {
            "Total pagado": lambda x: f"${float(x):,.0f}",
            "Último pago": lambda
                x: f"{ultimo_pago[0]} - ${ultimo_pago[1]:,.0f}" if ultimo_pago else "Sin pagos registrados"
        }

        financial_data = [
            ("Total pagado", total_pagado),
            ("Número de pagos", num_pagos),
            ("Último pago", ultimo_pago)
        ]
        create_info_section(scrollable_frame, "Resumen Financiero", "💰",
                            financial_data, financial_format)

        # === SECCIÓN DE ARCHIVOS ADJUNTOS ===
        archivos_frame = ttk.LabelFrame(scrollable_frame, text="📎 Archivos Adjuntos", padding="15")
        archivos_frame.pack(fill="x", pady=(0, 15))

        # Archivo de Identificación
        id_row = ttk.Frame(archivos_frame)
        id_row.pack(fill="x", pady=5)

        ttk.Label(id_row, text="🆔 Identificación:", font=style_config['label_font']).pack(side="left", padx=(0, 10))

        if datos[14]:  # archivo_identificacion existe
            ttk.Label(id_row, text="📁 Archivo disponible", foreground="#27ae60").pack(side="left", padx=(0, 10))
            ttk.Button(id_row, text="👁️ Abrir",
                       command=lambda: self.abrir_archivo(datos[14])).pack(side="left")
        else:
            ttk.Label(id_row, text="❌ No adjuntado", foreground="#e74c3c").pack(side="left")

        # Archivo de Contrato
        contract_row = ttk.Frame(archivos_frame)
        contract_row.pack(fill="x", pady=5)

        ttk.Label(contract_row, text="📄 Contrato:", font=style_config['label_font']).pack(side="left", padx=(0, 10))

        if datos[15]:  # archivo_contrato existe
            ttk.Label(contract_row, text="📁 Archivo disponible", foreground="#27ae60").pack(side="left", padx=(0, 10))
            ttk.Button(contract_row, text="👁️ Abrir",
                       command=lambda: self.abrir_archivo(datos[15])).pack(side="left")
        else:
            ttk.Label(contract_row, text="❌ No adjuntado", foreground="#e74c3c").pack(side="left")

        # Sección de notas (solo si hay notas)
        if datos[13] and datos[13].strip():
            notes_frame = ttk.LabelFrame(scrollable_frame, text="📝 Notas Adicionales", padding="15")
            notes_frame.pack(fill="x", pady=(0, 15))

            notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD,
                                 font=style_config['value_font'],
                                 bg=style_config['value_bg'],
                                 relief="sunken", bd=1,
                                 state=tk.DISABLED)
            notes_text.pack(fill="x")

            # Insertar texto
            notes_text.config(state=tk.NORMAL)
            notes_text.insert(1.0, datos[13])
            notes_text.config(state=tk.DISABLED)

        # === BOTONES DE ACCIÓN ===
        def create_action_buttons():
            """Crea los botones de acción de forma segura"""
            buttons_frame = ttk.Frame(scrollable_frame)
            buttons_frame.pack(fill="x", pady=20)

            def safe_edit():
                """Editar inquilino de forma segura"""
                try:
                    cleanup_and_close()
                    self.editar_inquilino()
                except Exception as e:
                    logging.error(f"Error editando desde detalles: {e}")

            def safe_generate_pdf():
                """Generar ficha PDF de forma segura"""
                try:
                    generate_tenant_pdf()
                except Exception as e:
                    logging.error(f"Error generando PDF: {e}")
                    messagebox.showerror("Error", f"Error generando PDF: {e}")

            def generate_tenant_pdf():
                """Genera una ficha completa del inquilino en PDF"""
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas as pdf_canvas
                    from reportlab.lib.units import inch
                    import datetime

                    nombre_archivo = f"ficha_inquilino_{datos[0].replace(' ', '_')}_{datos[1]}.pdf"

                    c = pdf_canvas.Canvas(nombre_archivo, pagesize=letter)
                    ancho, alto = letter

                    # Encabezado profesional
                    c.setFont("Helvetica-Bold", 18)
                    c.drawCentredString(ancho / 2, alto - 50, "FICHA COMPLETA DEL INQUILINO")

                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(ancho / 2, alto - 75, f"{datos[0]} - Apartamento {datos[1]}")

                    # Información detallada
                    y = alto - 120
                    c.setFont("Helvetica-Bold", 12)

                    sections = [
                        ("INFORMACIÓN PERSONAL", [
                            ("Nombre:", datos[0]),
                            ("Identificación:", datos[3] or "No especificado"),
                            ("Email:", datos[4] or "No especificado"),
                            ("Celular:", datos[5] or "No especificado"),
                            ("Profesión:", datos[6] or "No especificado")
                        ]),
                        ("INFORMACIÓN DEL ARRENDAMIENTO", [
                            ("Apartamento:", datos[1]),
                            ("Renta mensual:", f"${datos[2]:,.0f}" if datos[2] else "No especificado"),
                            ("Estado:", datos[9] or "No especificado"),
                            ("Fecha de ingreso:", datos[7] or "No especificado"),
                            ("Depósito:", f"${datos[8]:,.0f}" if datos[8] else "No especificado")
                        ]),
                        ("CONTACTO DE EMERGENCIA", [
                            ("Nombre:", datos[10] or "No especificado"),
                            ("Teléfono:", datos[11] or "No especificado"),
                            ("Relación:", datos[12] or "No especificado")
                        ]),
                        ("RESUMEN FINANCIERO", [
                            ("Total pagado:", f"${total_pagado:,.0f}"),
                            ("Número de pagos:", str(num_pagos)),
                            ("Último pago:",
                             f"{ultimo_pago[0]} - ${ultimo_pago[1]:,.0f}" if ultimo_pago else "Sin pagos")
                        ])
                    ]

                    for section_title, section_data in sections:
                        c.setFont("Helvetica-Bold", 12)
                        y -= 25
                        c.drawString(50, y, section_title)
                        y -= 5
                        c.line(50, y, ancho - 50, y)

                        c.setFont("Helvetica", 10)
                        for label, value in section_data:
                            y -= 20
                            c.drawString(70, y, label)
                            c.drawString(200, y, str(value))

                            if y < 100:
                                c.showPage()
                                y = alto - 50

                    # Notas al final
                    if datos[13] and datos[13].strip():
                        y -= 30
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(50, y, "NOTAS ADICIONALES")
                        y -= 20
                        c.setFont("Helvetica", 10)

                        # Dividir notas en líneas
                        notas_lineas = datos[13].split('\n')
                        for linea in notas_lineas:
                            if y < 50:
                                c.showPage()
                                y = alto - 50
                            c.drawString(70, y, linea[:80])
                            y -= 15

                    # Pie de página
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawCentredString(ancho / 2, 30,
                                        f"Generado el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                    c.save()
                    messagebox.showinfo("Ficha Generada", f"Ficha guardada como: {nombre_archivo}")

                    # Abrir PDF
                    try:
                        import os
                        os.startfile(nombre_archivo)
                    except:
                        pass

                except Exception as e:
                    raise Exception(f"Error generando ficha: {e}")

            # Crear botones con estilos
            button_style = {"padding": (10, 5)}

            ttk.Button(buttons_frame, text="✏️ Editar Inquilino",
                       command=safe_edit, **button_style).pack(side="left", padx=(0, 10))

            ttk.Button(buttons_frame, text="📄 Generar Ficha PDF",
                       command=safe_generate_pdf, **button_style).pack(side="left", padx=(0, 10))

            ttk.Button(buttons_frame, text="❌ Cerrar",
                       command=lambda: cleanup_and_close(), **button_style).pack(side="right")

        # Función de limpieza DEFINIDA ANTES de usar
        def cleanup_and_close():
            """Limpia recursos y cierra la ventana de forma segura"""
            try:
                # Desactivar scroll
                unbind_scroll()

                # Limpiar bindings específicos de la ventana
                if details_window.winfo_exists():
                    details_window.unbind("<FocusIn>")
                    details_window.unbind("<FocusOut>")
                    details_window.unbind("<MouseWheel>")

                # Destruir ventana
                details_window.destroy()

            except Exception as e:
                logging.error(f"Error en cleanup: {e}")
                try:
                    details_window.destroy()
                except:
                    pass

        # Crear botones de acción
        create_action_buttons()

        # === CONFIGURACIÓN FINAL DE LA VENTANA ===
        # Centrar ventana con mejor posicionamiento
        details_window.update_idletasks()
        width = 750
        height = 700

        # Obtener dimensiones de la pantalla
        screen_width = details_window.winfo_screenwidth()
        screen_height = details_window.winfo_screenheight()

        # Calcular posición centrada pero más hacia arriba
        x = (screen_width // 2) - (width // 2)
        y = max(50, (screen_height // 2) - (height // 2) - 80)  # Mover 80px hacia arriba y mínimo 50px del borde

        # Asegurar que la ventana no se salga de la pantalla
        if y + height > screen_height - 50:  # Dejar 50px de margen inferior
            y = screen_height - height - 50

        details_window.geometry(f'{width}x{height}+{x}+{y}')

        # Configurar protocolo de cierre
        details_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)

        # Configurar foco inicial en el canvas para que funcione el scroll
        canvas.focus_set()

        # Dar foco a la ventana
        details_window.focus_force()

        logging.info(f"Ventana de detalles abierta para inquilino: {datos[0]}")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_identificacion.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_celular.delete(0, tk.END)
        self.entry_profesion.delete(0, tk.END)
        self.entry_apto.delete(0, tk.END)
        self.entry_renta.delete(0, tk.END)
        self.combo_estado.set("Activo")
        self.entry_fecha_ingreso.delete(0, tk.END)
        self.entry_fecha_ingreso.insert(0, datetime.date.today().isoformat())
        self.entry_deposito.delete(0, tk.END)
        self.entry_contacto_emergencia.delete(0, tk.END)
        self.entry_telefono_emergencia.delete(0, tk.END)
        self.combo_relacion.set("")
        self.text_notas.delete(1.0, tk.END)

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del dashboard"""
        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Total de inquilinos
            cursor.execute("SELECT COUNT(*) FROM inquilinos")
            total = cursor.fetchone()[0] or 0

            # Inquilinos activos
            cursor.execute("SELECT COUNT(*) FROM inquilinos WHERE estado = 'Activo'")
            activos = cursor.fetchone()[0] or 0

            # Inquilinos pendientes/problemáticos
            cursor.execute("""
                SELECT COUNT(*) FROM inquilinos 
                WHERE estado IN ('Pendiente', 'Moroso', 'Suspendido')
            """)
            pendientes = cursor.fetchone()[0] or 0

            # Renta total mensual
            cursor.execute("SELECT SUM(renta) FROM inquilinos WHERE estado = 'Activo'")
            renta_total = cursor.fetchone()[0] or 0

            conn.close()

            # Actualizar labels
            self.total_label.config(text=str(total))
            self.active_label.config(text=str(activos))
            self.pending_label.config(text=str(pendientes))
            self.rent_label.config(text=f"${renta_total:,.0f}")

            # Cambiar color según estado
            if pendientes > 0:
                self.pending_label.config(foreground="#e74c3c")  # Rojo si hay problemas
            else:
                self.pending_label.config(foreground="#27ae60")  # Verde si todo bien

        except Exception as e:
            logging.error(f"Error actualizando estadísticas: {e}")
            messagebox.showerror("Error", f"Error actualizando estadísticas: {e}")

    def clear_placeholder(self, event):
        """Limpia los placeholders de los campos de renta"""
        if event.widget.get() in ["Min", "Max"]:
            event.widget.delete(0, tk.END)

    def on_filter_change(self, event=None):
        """Aplica filtros automáticamente cuando cambian"""
        # Usar after para evitar filtros muy frecuentes
        if hasattr(self, '_filter_after'):
            self.manager.root.after_cancel(self._filter_after)
        self._filter_after = self.manager.root.after(300, self.aplicar_filtros)

    def aplicar_filtros(self):
        """Aplica todos los filtros combinados"""
        try:
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Obtener valores de filtros
            termino_busqueda = self.entry_buscar.get().lower().strip()
            estado_filtro = self.filtro_estado.get()
            apartamento_filtro = self.filtro_apartamento.get().strip()

            # Filtros de renta
            renta_min = self.filtro_renta_min.get().strip()
            renta_max = self.filtro_renta_max.get().strip()

            # Convertir renta a números
            try:
                renta_min_val = float(renta_min) if renta_min and renta_min != "Min" else 0
            except ValueError:
                renta_min_val = 0

            try:
                renta_max_val = float(renta_max) if renta_max and renta_max != "Max" else float('inf')
            except ValueError:
                renta_max_val = float('inf')

            # Construir consulta SQL
            query = """
                SELECT id, nombre, apartamento, identificacion, email, celular, estado, renta 
                FROM inquilinos WHERE 1=1
            """
            params = []

            # Filtro de búsqueda general
            if termino_busqueda:
                query += """ AND (
                    LOWER(nombre) LIKE ? OR 
                    LOWER(apartamento) LIKE ? OR 
                    LOWER(identificacion) LIKE ? OR 
                    LOWER(email) LIKE ? OR 
                    LOWER(celular) LIKE ?
                )"""
                search_pattern = f"%{termino_busqueda}%"
                params.extend([search_pattern] * 5)

            # Filtro por estado
            if estado_filtro and estado_filtro != "Todos":
                query += " AND estado = ?"
                params.append(estado_filtro)

            # Filtro por apartamento
            if apartamento_filtro:
                query += " AND LOWER(apartamento) LIKE ?"
                params.append(f"%{apartamento_filtro.lower()}%")

            # Filtro por renta
            if renta_min_val > 0:
                query += " AND renta >= ?"
                params.append(renta_min_val)

            if renta_max_val < float('inf'):
                query += " AND renta <= ?"
                params.append(renta_max_val)

            query += """ ORDER BY 
                CASE 
                    WHEN estado = 'Activo' THEN 1
                    WHEN estado = 'Pendiente' THEN 2
                    WHEN estado = 'Moroso' THEN 3
                    WHEN estado = 'Suspendido' THEN 4
                    ELSE 5
                END,
                apartamento"""

            # Ejecutar consulta
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

            # Mostrar resultados
            for row in resultados:
                # Convertir None a string vacío
                row_display = []
                for item in row:
                    if item is None:
                        row_display.append("")
                    else:
                        row_display.append(item)

                self.tree.insert("", "end", values=row_display)

            # Actualizar contador
            total_resultados = len(resultados)
            if hasattr(self, 'results_label'):
                self.results_label.config(text=f"📊 Resultados: {total_resultados}")

        except Exception as e:
            logging.error(f"Error aplicando filtros: {e}")
            messagebox.showerror("Error", f"Error en filtros: {e}")

    def limpiar_filtros(self):
        """Limpia todos los filtros y muestra todos los inquilinos"""
        self.entry_buscar.delete(0, tk.END)
        self.filtro_estado.set("Todos")
        self.filtro_apartamento.delete(0, tk.END)

        # Restaurar placeholders
        self.filtro_renta_min.delete(0, tk.END)
        self.filtro_renta_min.insert(0, "Min")
        self.filtro_renta_max.delete(0, tk.END)
        self.filtro_renta_max.insert(0, "Max")

        # Cargar todos los inquilinos
        self.cargar_inquilinos()

    def mostrar_formulario_agregar(self):
        """Abre ventana modal para agregar nuevo inquilino"""
        # Crear ventana modal
        add_window = tk.Toplevel()
        add_window.title("➕ Agregar Nuevo Inquilino")
        add_window.geometry("750x650")
        add_window.resizable(True, True)
        add_window.transient(self.manager.root)
        add_window.grab_set()  # Hacer ventana modal
        self._add_modal_active = True

        # === SISTEMA DE SCROLL PROBADO (igual al de detalles) ===
        def setup_scroll_system():
            """Configura el sistema de scroll de forma segura"""
            # Frame principal
            main_frame = ttk.Frame(add_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Canvas con configuración robusta
            canvas = tk.Canvas(main_frame, highlightthickness=0, bg='#f0f0f0')
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            # Configurar canvas
            canvas.configure(yscrollcommand=scrollbar.set)

            # Función para actualizar scroll region
            def configure_scroll_region(event=None):
                if canvas.winfo_exists():
                    canvas.configure(scrollregion=canvas.bbox("all"))

            scrollable_frame.bind("<Configure>", configure_scroll_region)
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Función mejorada para scroll con validación
            def safe_mousewheel(event):
                try:
                    if canvas.winfo_exists() and add_window.winfo_exists():
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except tk.TclError:
                    pass  # Ignorar errores si la ventana fue destruida

            # Función para ajustar ancho del canvas window
            def configure_canvas_window(event):
                try:
                    if canvas.winfo_exists():
                        canvas.itemconfig(canvas_window, width=event.width)
                except tk.TclError:
                    pass

            canvas.bind("<Configure>", configure_canvas_window)

            # Sistema de scroll exclusivo mejorado
            def bind_scroll():
                try:
                    # Solo bind a la ventana modal, no al canvas
                    add_window.bind("<MouseWheel>", safe_mousewheel)
                    # Asegurar que el canvas tenga foco
                    canvas.focus_set()
                except tk.TclError:
                    pass

            def unbind_scroll():
                try:
                    if add_window.winfo_exists():
                        add_window.unbind("<MouseWheel>")
                except tk.TclError:
                    pass

            # Control basado en entrada/salida del mouse de la ventana
            def on_enter_window(event):
                bind_scroll()

            def on_leave_window(event):
                unbind_scroll()

            # Bind eventos de entrada y salida SOLO a la ventana principal
            add_window.bind("<Enter>", on_enter_window)
            add_window.bind("<Leave>", on_leave_window)

            # Activar scroll inicial
            bind_scroll()

            # Variable para control de scroll
            #self._add_window_active = True

            # Empaquetar widgets
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            return scrollable_frame, canvas, unbind_scroll

        # Configurar sistema de scroll
        scrollable_frame, canvas, unbind_scroll = setup_scroll_system()

        # Función de limpieza MEJORADA
        def cleanup_and_close():
            """Limpia recursos y cierra la ventana de forma segura"""
            try:
                # Marcar ventana como inactiva
                self._add_modal_active = False

                # Desactivar scroll
                unbind_scroll()

                # Limpiar bindings específicos de la ventana
                if add_window.winfo_exists():
                    add_window.unbind("<Enter>")
                    add_window.unbind("<Leave>")
                    add_window.unbind("<MouseWheel>")
                    add_window.unbind("<FocusIn>")
                    add_window.unbind("<FocusOut>")

                # Destruir ventana
                add_window.destroy()

            except Exception as e:
                logging.error(f"Error en cleanup: {e}")
                try:
                    add_window.destroy()
                except:
                    pass

        # Centrar ventana
        add_window.update_idletasks()
        width = 750
        height = 650
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = max(50, (screen_height // 2) - (height // 2) - 80)
        add_window.geometry(f'{width}x{height}+{x}+{y}')

        # Crear formulario en la ventana
        self.setup_add_form_modal(scrollable_frame, add_window, cleanup_and_close)

        # Configurar protocolo de cierre
        add_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)

        # Configurar foco inicial
        canvas.focus_set()
        add_window.focus_force()

        logging.info("Ventana de agregar inquilino abierta")

    def setup_add_form_modal(self, parent, window, cleanup_function):
        """Configura el formulario en ventana modal"""

        # Título
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(title_frame,
                               text="📝 Registrar Nuevo Inquilino",
                               font=("Segoe UI", 16, "bold"),
                               fg="#2c3e50")
        title_label.pack()

        # === TODO EL FORMULARIO (igual al anterior) ===
        # Información Personal
        personal_frame = ttk.LabelFrame(parent, text="👤 Información Personal", padding="15")
        personal_frame.pack(fill="x", pady=(0, 10))

        # Fila 1
        row1 = ttk.Frame(personal_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Nombre completo:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_nombre = ttk.Entry(row1, width=25)
        self.modal_nombre.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row1, text="Identificación:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_identificacion = ttk.Entry(row1, width=15)
        self.modal_identificacion.grid(row=0, column=3, sticky="ew")

        row1.columnconfigure(1, weight=1)
        row1.columnconfigure(3, weight=1)

        # Fila 2
        row2 = ttk.Frame(personal_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Email:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_email = ttk.Entry(row2, width=25)
        self.modal_email.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row2, text="Celular:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_celular = ttk.Entry(row2, width=15)
        self.modal_celular.grid(row=0, column=3, sticky="ew")

        row2.columnconfigure(1, weight=1)
        row2.columnconfigure(3, weight=1)

        # Profesión
        row3 = ttk.Frame(personal_frame)
        row3.pack(fill="x", pady=5)

        ttk.Label(row3, text="Profesión:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_profesion = ttk.Entry(row3, width=40)
        self.modal_profesion.grid(row=0, column=1, sticky="ew")

        row3.columnconfigure(1, weight=1)

        # === INFORMACIÓN DEL ARRENDAMIENTO ===
        rental_frame = ttk.LabelFrame(parent, text="🏠 Información del Arrendamiento", padding="15")
        rental_frame.pack(fill="x", pady=(0, 10))

        # Fila arrendamiento 1
        rent_row1 = ttk.Frame(rental_frame)
        rent_row1.pack(fill="x", pady=5)

        ttk.Label(rent_row1, text="Apartamento:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_apto = ttk.Entry(rent_row1, width=10)
        self.modal_apto.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Renta mensual:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_renta = ttk.Entry(rent_row1, width=15)
        self.modal_renta.grid(row=0, column=3, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Estado:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.modal_estado = ttk.Combobox(rent_row1, width=12,
                                         values=["Activo", "Pendiente", "Inactivo", "Moroso", "Suspendido"])
        self.modal_estado.set("Activo")
        self.modal_estado.grid(row=0, column=5, sticky="w")

        # Fila arrendamiento 2
        rent_row2 = ttk.Frame(rental_frame)
        rent_row2.pack(fill="x", pady=5)

        ttk.Label(rent_row2, text="Fecha ingreso:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        try:
            from tkcalendar import DateEntry
            self.modal_fecha = DateEntry(rent_row2, width=12,
                                         background='darkblue',
                                         foreground='white',
                                         borderwidth=2,
                                         date_pattern='yyyy-mm-dd',
                                         state='readonly',
                                         showweeknumbers=False)
            self.modal_fecha.set_date(datetime.date.today())
        except ImportError:
            self.modal_fecha = ttk.Entry(rent_row2, width=12)
            self.modal_fecha.insert(0, datetime.date.today().isoformat())
        self.modal_fecha.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row2, text="Depósito:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_deposito = ttk.Entry(rent_row2, width=15)
        self.modal_deposito.grid(row=0, column=3, sticky="w")

        # === CONTACTO DE EMERGENCIA ===
        emergency_frame = ttk.LabelFrame(parent, text="🚨 Contacto de Emergencia", padding="15")
        emergency_frame.pack(fill="x", pady=(0, 10))

        emerg_row1 = ttk.Frame(emergency_frame)
        emerg_row1.pack(fill="x", pady=5)

        ttk.Label(emerg_row1, text="Nombre contacto:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_contacto = ttk.Entry(emerg_row1, width=25)
        self.modal_contacto.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(emerg_row1, text="Teléfono:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_tel_emergencia = ttk.Entry(emerg_row1, width=15)
        self.modal_tel_emergencia.grid(row=0, column=3, sticky="ew")

        emerg_row1.columnconfigure(1, weight=1)
        emerg_row1.columnconfigure(3, weight=1)

        emerg_row2 = ttk.Frame(emergency_frame)
        emerg_row2.pack(fill="x", pady=5)

        ttk.Label(emerg_row2, text="Relación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_relacion = ttk.Combobox(emerg_row2, width=15,
                                           values=["Padre", "Madre", "Esposo/a", "Hermano/a", "Hijo/a", "Amigo/a",
                                                   "Otro"])
        self.modal_relacion.grid(row=0, column=1, sticky="w")

        # === NOTAS ===
        notes_frame = ttk.LabelFrame(parent, text="📝 Notas Adicionales", padding="15")
        notes_frame.pack(fill="x", pady=(0, 15))

        self.modal_notas = tk.Text(notes_frame, height=4, width=60)
        self.modal_notas.pack(fill="x")

        # === ARCHIVOS ADJUNTOS ===
        files_frame = ttk.LabelFrame(parent, text="📎 Archivos Adjuntos", padding="15")
        files_frame.pack(fill="x", pady=(0, 10))

        files_row1 = ttk.Frame(files_frame)
        files_row1.pack(fill="x", pady=5)

        # Archivo de Identificación
        ttk.Label(files_row1, text="🆔 Identificación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_id_file_label = ttk.Label(files_row1, text="No seleccionado",
                                             foreground="gray")
        self.modal_id_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row1, text="📁 Seleccionar",
                   command=lambda: self.seleccionar_archivo_id()).grid(row=0, column=2, padx=(0, 5))

        files_row2 = ttk.Frame(files_frame)
        files_row2.pack(fill="x", pady=5)

        # Archivo de Contrato
        ttk.Label(files_row2, text="📄 Contrato:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_contract_file_label = ttk.Label(files_row2, text="No seleccionado",
                                                   foreground="gray")
        self.modal_contract_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row2, text="📁 Seleccionar",
                   command=lambda: self.seleccionar_archivo_contrato()).grid(row=0, column=2, padx=(0, 5))

        # Variables para almacenar rutas de archivos
        self.modal_id_file_path = None
        self.modal_contract_file_path = None

        # === BOTONES ===
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="💾 Guardar Inquilino",
                   command=lambda: self.guardar_inquilino_modal(window, cleanup_function)).pack(side="right",
                                                                                                padx=(10, 0))
        ttk.Button(btn_frame, text="❌ Cancelar",
                   command=cleanup_function).pack(side="right")

    def scroll_to_form(self):
        """Hace scroll automático al formulario"""
        try:
            # Si hay un canvas padre, hacer scroll
            parent = self.form_frame.master
            while parent:
                if isinstance(parent, tk.Canvas):
                    parent.yview_moveto(0.3)  # Scroll al 30% de la página
                    break
                parent = parent.master
        except Exception as e:
            logging.error(f"Error en scroll: {e}")

    def ocultar_formulario(self):
        """Oculta el formulario y muestra el card"""
        self.form_frame.pack_forget()
        self.form_visible = False

        # Mostrar el card nuevamente
        add_card_frame = self.form_frame.master.winfo_children()[1]  # El frame del card
        self.add_tenant_card.pack(fill="x", padx=20, pady=10)

        # Limpiar formulario
        try:
            self.limpiar_formulario()
        except:
            pass  # Los campos pueden no existir aún

    def setup_add_form(self):
        """Configura el formulario de agregar inquilinos"""

        # Limpiar contenido anterior del frame
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        # === INFORMACIÓN PERSONAL ===
        personal_frame = ttk.LabelFrame(self.form_frame, text="Información Personal", padding="10")
        personal_frame.pack(fill="x", pady=5)

        # Fila 1
        row1 = ttk.Frame(personal_frame)
        row1.pack(fill="x", pady=3)

        ttk.Label(row1, text="Nombre completo:").pack(side="left", padx=(0, 5))
        self.entry_nombre = ttk.Entry(row1, width=25)
        self.entry_nombre.pack(side="left", padx=(0, 15))

        ttk.Label(row1, text="Identificación:").pack(side="left", padx=(0, 5))
        self.entry_identificacion = ttk.Entry(row1, width=15)
        self.entry_identificacion.pack(side="left")

        # Fila 2
        row2 = ttk.Frame(personal_frame)
        row2.pack(fill="x", pady=3)

        ttk.Label(row2, text="Email:").pack(side="left", padx=(0, 5))
        self.entry_email = ttk.Entry(row2, width=25)
        self.entry_email.pack(side="left", padx=(0, 15))

        ttk.Label(row2, text="Celular:").pack(side="left", padx=(0, 5))
        self.entry_celular = ttk.Entry(row2, width=15)
        self.entry_celular.pack(side="left")

        # Fila 3
        row3 = ttk.Frame(personal_frame)
        row3.pack(fill="x", pady=3)

        ttk.Label(row3, text="Profesión:").pack(side="left", padx=(0, 5))
        self.entry_profesion = ttk.Entry(row3, width=30)
        self.entry_profesion.pack(side="left")

        # === INFORMACIÓN DEL ARRENDAMIENTO ===
        rental_frame = ttk.LabelFrame(self.form_frame, text="Información del Arrendamiento", padding="10")
        rental_frame.pack(fill="x", pady=5)

        # Fila 4
        row4 = ttk.Frame(rental_frame)
        row4.pack(fill="x", pady=3)

        ttk.Label(row4, text="Apartamento:").pack(side="left", padx=(0, 5))
        self.entry_apto = ttk.Entry(row4, width=10)
        self.entry_apto.pack(side="left", padx=(0, 15))

        ttk.Label(row4, text="Renta mensual:").pack(side="left", padx=(0, 5))
        self.entry_renta = ttk.Entry(row4, width=12)
        self.entry_renta.pack(side="left", padx=(0, 15))

        ttk.Label(row4, text="Estado:").pack(side="left", padx=(0, 5))
        self.combo_estado = ttk.Combobox(row4, width=12,
                                         values=["Activo", "Pendiente", "Inactivo", "Moroso", "Suspendido"])
        self.combo_estado.set("Activo")
        self.combo_estado.pack(side="left")

        # Fila 5
        row5 = ttk.Frame(rental_frame)
        row5.pack(fill="x", pady=3)

        ttk.Label(row5, text="Fecha ingreso:").pack(side="left", padx=(0, 5))
        try:
            from tkcalendar import DateEntry
            self.entry_fecha_ingreso = DateEntry(row5, width=12,
                                                 background='darkblue',
                                                 foreground='white',
                                                 borderwidth=2,
                                                 date_pattern='yyyy-mm-dd',
                                                 state='readonly',
                                                 showweeknumbers=False)
        except ImportError:
            self.entry_fecha_ingreso = ttk.Entry(row5, width=12)
            self.entry_fecha_ingreso.insert(0, datetime.date.today().isoformat())
        self.entry_fecha_ingreso.pack(side="left", padx=(0, 15))

        ttk.Label(row5, text="Depósito:").pack(side="left", padx=(0, 5))
        self.entry_deposito = ttk.Entry(row5, width=12)
        self.entry_deposito.pack(side="left")

        # === CONTACTO DE EMERGENCIA ===
        emergency_frame = ttk.LabelFrame(self.form_frame, text="Contacto de Emergencia", padding="10")
        emergency_frame.pack(fill="x", pady=5)

        # Fila 6
        row6 = ttk.Frame(emergency_frame)
        row6.pack(fill="x", pady=3)

        ttk.Label(row6, text="Nombre contacto:").pack(side="left", padx=(0, 5))
        self.entry_contacto_emergencia = ttk.Entry(row6, width=25)
        self.entry_contacto_emergencia.pack(side="left", padx=(0, 15))

        ttk.Label(row6, text="Teléfono:").pack(side="left", padx=(0, 5))
        self.entry_telefono_emergencia = ttk.Entry(row6, width=15)
        self.entry_telefono_emergencia.pack(side="left")

        # Fila 7
        row7 = ttk.Frame(emergency_frame)
        row7.pack(fill="x", pady=3)

        ttk.Label(row7, text="Relación:").pack(side="left", padx=(0, 5))
        self.combo_relacion = ttk.Combobox(row7, width=15,
                                           values=["Padre", "Madre", "Esposo/a", "Hermano/a", "Hijo/a", "Amigo/a",
                                                   "Otro"])
        self.combo_relacion.pack(side="left")

        # === NOTAS ===
        notes_frame = ttk.LabelFrame(self.form_frame, text="Notas Adicionales", padding="10")
        notes_frame.pack(fill="x", pady=5)

        self.text_notas = tk.Text(notes_frame, height=3, width=60)
        self.text_notas.pack(fill="x")

        # === BOTONES ===
        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="💾 Guardar Inquilino",
                   command=self.guardar_inquilino).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="🗑️ Limpiar Campos",
                   command=self.limpiar_formulario).pack(side="right")

    def guardar_inquilino_modal(self, window, cleanup_function):
        """Guarda un nuevo inquilino desde la ventana modal"""
        try:
            # Obtener valores de todos los campos MODALES
            nombre = self.modal_nombre.get().strip()
            identificacion = self.modal_identificacion.get().strip()
            email = self.modal_email.get().strip()
            celular = self.modal_celular.get().strip()
            profesion = self.modal_profesion.get().strip()
            apto = self.modal_apto.get().strip()
            renta = self.modal_renta.get().strip()
            estado = self.modal_estado.get()
            fecha_ingreso = self.modal_fecha.get().strip()
            deposito = self.modal_deposito.get().strip()
            contacto_emergencia = self.modal_contacto.get().strip()
            telefono_emergencia = self.modal_tel_emergencia.get().strip()
            relacion_emergencia = self.modal_relacion.get()
            notas = self.modal_notas.get(1.0, tk.END).strip()

            # Obtener información de archivos
            archivo_id_path = getattr(self, 'modal_id_file_path', None)
            archivo_contrato_path = getattr(self, 'modal_contract_file_path', None)

            # Validaciones básicas obligatorias
            if not nombre:
                messagebox.showwarning("Campo requerido", "El nombre es obligatorio.")
                self.modal_nombre.focus()
                return

            if not apto:
                messagebox.showwarning("Campo requerido", "El apartamento es obligatorio.")
                self.modal_apto.focus()
                return

            if not renta:
                messagebox.showwarning("Campo requerido", "La renta es obligatoria.")
                self.modal_renta.focus()
                return

            # Validación de renta
            try:
                renta = float(renta)
                if renta <= 0:
                    messagebox.showerror("Error", "La renta debe ser un número positivo.")
                    self.modal_renta.focus()
                    return
            except ValueError:
                messagebox.showerror("Error", "La renta debe ser un número válido.")
                self.modal_renta.focus()
                return

            # Validación de depósito (opcional pero si se ingresa debe ser válido)
            deposito_valor = 0
            if deposito:
                try:
                    deposito_valor = float(deposito)
                    if deposito_valor < 0:
                        messagebox.showerror("Error", "El depósito no puede ser negativo.")
                        self.modal_deposito.focus()
                        return
                except ValueError:
                    messagebox.showerror("Error", "El depósito debe ser un número válido.")
                    self.modal_deposito.focus()
                    return

            # Validación de email (opcional pero si se ingresa debe ser válido)
            if email and '@' not in email:
                messagebox.showwarning("Email inválido", "Por favor ingresa un email válido.")
                self.modal_email.focus()
                return

            # Verificar que no existe otro inquilino con la misma identificación
            if identificacion:
                conn = sqlite3.connect('edificio.db')
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM inquilinos WHERE identificacion = ? AND identificacion != ''",
                               (identificacion,))
                resultado = cursor.fetchone()
                if resultado:
                    messagebox.showerror("Identificación duplicada",
                                         f"Ya existe un inquilino con la identificación {identificacion}: {resultado[0]}")
                    conn.close()
                    self.modal_identificacion.focus()
                    return
                conn.close()

            # Verificar que no existe otro inquilino en el mismo apartamento activo
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM inquilinos WHERE apartamento = ? AND estado = 'Activo'", (apto,))
            resultado = cursor.fetchone()
            if resultado:
                if not messagebox.askyesno("Apartamento ocupado",
                                           f"El apartamento {apto} ya tiene un inquilino activo: {resultado[0]}\n"
                                           f"¿Deseas continuar de todas formas?"):
                    conn.close()
                    self.modal_apto.focus()
                    return

            # Guardar en la base de datos
            cursor.execute("""
                INSERT INTO inquilinos (
                    nombre, identificacion, email, celular, profesion,
                    apartamento, renta, estado, fecha_ingreso, deposito,
                    contacto_emergencia, telefono_emergencia, relacion_emergencia, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, identificacion, email, celular, profesion,
                  apto, renta, estado, fecha_ingreso, deposito_valor,
                  contacto_emergencia, telefono_emergencia, relacion_emergencia, notas))

            # Obtener el ID del inquilino recién creado
            inquilino_id = cursor.lastrowid

            # Copiar archivos adjuntos si existen
            archivos_copiados = self.copiar_archivos_inquilino(inquilino_id, nombre)

            # Actualizar rutas de archivos en la base de datos
            if archivos_copiados:
                archivo_id_final = archivos_copiados.get('identificacion', None)
                archivo_contrato_final = archivos_copiados.get('contrato', None)
                fecha_actual = datetime.datetime.now().isoformat()

                cursor.execute("""
                    UPDATE inquilinos 
                    SET archivo_identificacion = ?, archivo_contrato = ?,
                        fecha_archivo_id = ?, fecha_archivo_contrato = ?
                    WHERE id = ?
                """, (archivo_id_final, archivo_contrato_final,
                      fecha_actual if archivo_id_final else None,
                      fecha_actual if archivo_contrato_final else None,
                      inquilino_id))

            conn.commit()
            conn.close()

            # Mensaje de éxito con información de archivos
            mensaje_exito = f"Inquilino {nombre} registrado exitosamente en el apartamento {apto}."
            if archivos_copiados:
                archivos_info = []
                if 'identificacion' in archivos_copiados:
                    archivos_info.append("identificación")
                if 'contrato' in archivos_copiados:
                    archivos_info.append("contrato")
                mensaje_exito += f"\n\nArchivos adjuntados: {', '.join(archivos_info)}"

            messagebox.showinfo("✅ Éxito", mensaje_exito)

            # Recargar lista y estadísticas
            self.cargar_inquilinos()
            self.actualizar_estadisticas()

            # Cerrar ventana modal
            cleanup_function()

        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Error al guardar: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def seleccionar_archivo_id(self):
        """Selecciona archivo de identificación"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de identificación",
                filetypes=[
                    ("Archivos de imagen", "*.jpg *.jpeg *.png *.pdf"),
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Todos los archivos", "*.*")
                ]
            )

            if file_path:
                self.modal_id_file_path = file_path
                filename = os.path.basename(file_path)
                self.modal_id_file_label.config(text=filename, foreground="green")

        except Exception as e:
            logging.error(f"Error seleccionando archivo ID: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def seleccionar_archivo_contrato(self):
        """Selecciona archivo de contrato"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar contrato de arrendamiento",
                filetypes=[
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Documentos Word", "*.doc *.docx"),
                    ("Todos los archivos", "*.*")
                ]
            )

            if file_path:
                self.modal_contract_file_path = file_path
                filename = os.path.basename(file_path)
                self.modal_contract_file_label.config(text=filename, foreground="green")

        except Exception as e:
            logging.error(f"Error seleccionando archivo contrato: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def copiar_archivos_inquilino(self, inquilino_id, nombre_inquilino):
        """Copia los archivos adjuntos a la carpeta del inquilino"""
        try:
            # Crear carpeta para archivos del inquilino
            carpeta_inquilino = f"Archivos_Inquilinos/{inquilino_id}_{nombre_inquilino.replace(' ', '_')}"

            if not os.path.exists(carpeta_inquilino):
                os.makedirs(carpeta_inquilino)

            archivos_copiados = {}

            # Copiar archivo de identificación
            if self.modal_id_file_path:
                extension = os.path.splitext(self.modal_id_file_path)[1]
                nuevo_nombre = f"identificacion_{inquilino_id}{extension}"
                ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                shutil.copy2(self.modal_id_file_path, ruta_destino)
                archivos_copiados['identificacion'] = ruta_destino

            # Copiar archivo de contrato
            if self.modal_contract_file_path:
                extension = os.path.splitext(self.modal_contract_file_path)[1]
                nuevo_nombre = f"contrato_{inquilino_id}{extension}"
                ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                shutil.copy2(self.modal_contract_file_path, ruta_destino)
                archivos_copiados['contrato'] = ruta_destino

            return archivos_copiados

        except Exception as e:
            logging.error(f"Error copiando archivos: {e}")
            return {}

    def abrir_archivo(self, ruta_archivo):
        """Abre un archivo adjunto"""
        try:
            if not ruta_archivo or not os.path.exists(ruta_archivo):
                messagebox.showerror("Archivo no encontrado",
                                     "El archivo no existe o fue movido de su ubicación original.")
                return

            # Abrir archivo con la aplicación predeterminada del sistema
            import subprocess
            import platform

            if platform.system() == 'Windows':
                os.startfile(ruta_archivo)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', ruta_archivo])
            else:  # Linux
                subprocess.call(['xdg-open', ruta_archivo])

        except Exception as e:
            logging.error(f"Error abriendo archivo: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

    def setup_edit_form_modal(self, parent, window, cleanup_function, inquilino_id, datos):
        """Configura el formulario de edición en ventana modal con datos pre-cargados"""

        # Título
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(title_frame,
                               text=f"✏️ Editar Información del Inquilino",
                               font=("Segoe UI", 16, "bold"),
                               fg="#2c3e50")
        title_label.pack()

        subtitle_label = tk.Label(title_frame,
                                  text=f"Modificando datos de: {datos[0]}",
                                  font=("Segoe UI", 12),
                                  fg="#6c757d")
        subtitle_label.pack()

        # === INFORMACIÓN PERSONAL ===
        personal_frame = ttk.LabelFrame(parent, text="👤 Información Personal", padding="15")
        personal_frame.pack(fill="x", pady=(0, 10))

        # Fila 1
        row1 = ttk.Frame(personal_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Nombre completo:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_nombre = ttk.Entry(row1, width=25)
        self.edit_nombre.insert(0, datos[0] or "")  # Pre-cargar dato
        self.edit_nombre.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row1, text="Identificación:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_identificacion = ttk.Entry(row1, width=15)
        self.edit_identificacion.insert(0, datos[3] or "")  # Pre-cargar dato
        self.edit_identificacion.grid(row=0, column=3, sticky="ew")

        row1.columnconfigure(1, weight=1)
        row1.columnconfigure(3, weight=1)

        # Fila 2
        row2 = ttk.Frame(personal_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Email:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_email = ttk.Entry(row2, width=25)
        self.edit_email.insert(0, datos[4] or "")  # Pre-cargar dato
        self.edit_email.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row2, text="Celular:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_celular = ttk.Entry(row2, width=15)
        self.edit_celular.insert(0, datos[5] or "")  # Pre-cargar dato
        self.edit_celular.grid(row=0, column=3, sticky="ew")

        row2.columnconfigure(1, weight=1)
        row2.columnconfigure(3, weight=1)

        # Profesión
        row3 = ttk.Frame(personal_frame)
        row3.pack(fill="x", pady=5)

        ttk.Label(row3, text="Profesión:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_profesion = ttk.Entry(row3, width=40)
        self.edit_profesion.insert(0, datos[6] or "")  # Pre-cargar dato
        self.edit_profesion.grid(row=0, column=1, sticky="ew")

        row3.columnconfigure(1, weight=1)

        # === INFORMACIÓN DEL ARRENDAMIENTO ===
        rental_frame = ttk.LabelFrame(parent, text="🏠 Información del Arrendamiento", padding="15")
        rental_frame.pack(fill="x", pady=(0, 10))

        # Fila arrendamiento 1
        rent_row1 = ttk.Frame(rental_frame)
        rent_row1.pack(fill="x", pady=5)

        ttk.Label(rent_row1, text="Apartamento:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_apto = ttk.Entry(rent_row1, width=10)
        self.edit_apto.insert(0, datos[1] or "")  # Pre-cargar dato
        self.edit_apto.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Renta mensual:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_renta = ttk.Entry(rent_row1, width=15)
        self.edit_renta.insert(0, str(datos[2]) if datos[2] else "")  # Pre-cargar dato
        self.edit_renta.grid(row=0, column=3, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Estado:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.edit_estado = ttk.Combobox(rent_row1, width=12,
                                        values=["Activo", "Pendiente", "Inactivo", "Moroso", "Suspendido"])
        self.edit_estado.set(datos[9] or "Activo")  # Pre-cargar dato
        self.edit_estado.grid(row=0, column=5, sticky="w")

        # Fila arrendamiento 2
        rent_row2 = ttk.Frame(rental_frame)
        rent_row2.pack(fill="x", pady=5)

        ttk.Label(rent_row2, text="Fecha ingreso:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        try:
            from tkcalendar import DateEntry
            self.edit_fecha = DateEntry(rent_row2, width=12,
                                        background='darkblue',
                                        foreground='white',
                                        borderwidth=2,
                                        date_pattern='yyyy-mm-dd',
                                        state='readonly',
                                        showweeknumbers=False)
            if datos[7]:  # Si hay fecha, cargarla
                try:
                    fecha_obj = datetime.datetime.fromisoformat(datos[7]).date()
                    self.edit_fecha.set_date(fecha_obj)
                except:
                    self.edit_fecha.set_date(datetime.date.today())
            else:
                self.edit_fecha.set_date(datetime.date.today())
        except ImportError:
            self.edit_fecha = ttk.Entry(rent_row2, width=12)
            self.edit_fecha.insert(0, datos[7] or datetime.date.today().isoformat())
        self.edit_fecha.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row2, text="Depósito:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_deposito = ttk.Entry(rent_row2, width=15)
        self.edit_deposito.insert(0, str(datos[8]) if datos[8] else "")  # Pre-cargar dato
        self.edit_deposito.grid(row=0, column=3, sticky="w")

        # === CONTACTO DE EMERGENCIA ===
        emergency_frame = ttk.LabelFrame(parent, text="🚨 Contacto de Emergencia", padding="15")
        emergency_frame.pack(fill="x", pady=(0, 10))

        emerg_row1 = ttk.Frame(emergency_frame)
        emerg_row1.pack(fill="x", pady=5)

        ttk.Label(emerg_row1, text="Nombre contacto:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_contacto = ttk.Entry(emerg_row1, width=25)
        self.edit_contacto.insert(0, datos[10] or "")  # Pre-cargar dato
        self.edit_contacto.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(emerg_row1, text="Teléfono:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_tel_emergencia = ttk.Entry(emerg_row1, width=15)
        self.edit_tel_emergencia.insert(0, datos[11] or "")  # Pre-cargar dato
        self.edit_tel_emergencia.grid(row=0, column=3, sticky="ew")

        emerg_row1.columnconfigure(1, weight=1)
        emerg_row1.columnconfigure(3, weight=1)

        emerg_row2 = ttk.Frame(emergency_frame)
        emerg_row2.pack(fill="x", pady=5)

        ttk.Label(emerg_row2, text="Relación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_relacion = ttk.Combobox(emerg_row2, width=15,
                                          values=["Padre", "Madre", "Esposo/a", "Hermano/a", "Hijo/a", "Amigo/a",
                                                  "Otro"])
        self.edit_relacion.set(datos[12] or "")  # Pre-cargar dato
        self.edit_relacion.grid(row=0, column=1, sticky="w")

        # === NOTAS ===
        notes_frame = ttk.LabelFrame(parent, text="📝 Notas Adicionales", padding="15")
        notes_frame.pack(fill="x", pady=(0, 10))

        self.edit_notas = tk.Text(notes_frame, height=4, width=60)
        self.edit_notas.insert(1.0, datos[13] or "")  # Pre-cargar dato
        self.edit_notas.pack(fill="x")

        # === ARCHIVOS ADJUNTOS ===
        files_frame = ttk.LabelFrame(parent, text="📎 Archivos Adjuntos", padding="15")
        files_frame.pack(fill="x", pady=(0, 10))

        # Mostrar archivos actuales y permitir cambiarlos
        files_row1 = ttk.Frame(files_frame)
        files_row1.pack(fill="x", pady=5)

        # Archivo de Identificación
        ttk.Label(files_row1, text="🆔 Identificación:").grid(row=0, column=0, sticky="w", padx=(0, 10))

        if datos[14]:  # Si ya tiene archivo
            self.edit_id_file_label = ttk.Label(files_row1, text=os.path.basename(datos[14]),
                                                foreground="green")
            self.edit_id_file_path = datos[14]  # Mantener archivo actual
        else:
            self.edit_id_file_label = ttk.Label(files_row1, text="No seleccionado",
                                                foreground="gray")
            self.edit_id_file_path = None

        self.edit_id_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row1, text="📁 Cambiar",
                   command=lambda: self.seleccionar_archivo_edit_id()).grid(row=0, column=2, padx=(0, 5))

        files_row2 = ttk.Frame(files_frame)
        files_row2.pack(fill="x", pady=5)

        # Archivo de Contrato
        ttk.Label(files_row2, text="📄 Contrato:").grid(row=0, column=0, sticky="w", padx=(0, 10))

        if datos[15]:  # Si ya tiene archivo
            self.edit_contract_file_label = ttk.Label(files_row2, text=os.path.basename(datos[15]),
                                                      foreground="green")
            self.edit_contract_file_path = datos[15]  # Mantener archivo actual
        else:
            self.edit_contract_file_label = ttk.Label(files_row2, text="No seleccionado",
                                                      foreground="gray")
            self.edit_contract_file_path = None

        self.edit_contract_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row2, text="📁 Cambiar",
                   command=lambda: self.seleccionar_archivo_edit_contrato()).grid(row=0, column=2, padx=(0, 5))

        # === BOTONES ===
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="💾 Guardar Cambios",
                   command=lambda: self.actualizar_inquilino_modal(window, cleanup_function, inquilino_id)).pack(
            side="right", padx=(10, 0))
        ttk.Button(btn_frame, text="❌ Cancelar",
                   command=cleanup_function).pack(side="right")

    def seleccionar_archivo_edit_id(self):
        """Selecciona nuevo archivo de identificación para edición"""
        try:
            file_path = filedialog.askopenfilename(
                title="Cambiar archivo de identificación",
                filetypes=[
                    ("Archivos de imagen", "*.jpg *.jpeg *.png *.pdf"),
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Todos los archivos", "*.*")
                ]
            )

            if file_path:
                self.edit_id_file_path = file_path
                filename = os.path.basename(file_path)
                self.edit_id_file_label.config(text=filename, foreground="blue")

        except Exception as e:
            logging.error(f"Error seleccionando archivo ID en edición: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def seleccionar_archivo_edit_contrato(self):
        """Selecciona nuevo archivo de contrato para edición"""
        try:
            file_path = filedialog.askopenfilename(
                title="Cambiar contrato de arrendamiento",
                filetypes=[
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Documentos Word", "*.doc *.docx"),
                    ("Todos los archivos", "*.*")
                ]
            )

            if file_path:
                self.edit_contract_file_path = file_path
                filename = os.path.basename(file_path)
                self.edit_contract_file_label.config(text=filename, foreground="blue")

        except Exception as e:
            logging.error(f"Error seleccionando archivo contrato en edición: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def actualizar_inquilino_modal(self, window, cleanup_function, inquilino_id):
        """Actualiza los datos del inquilino editado"""
        try:
            # Obtener valores del formulario de edición
            nombre = self.edit_nombre.get().strip()
            identificacion = self.edit_identificacion.get().strip()
            email = self.edit_email.get().strip()
            celular = self.edit_celular.get().strip()
            profesion = self.edit_profesion.get().strip()
            apto = self.edit_apto.get().strip()
            renta = self.edit_renta.get().strip()
            estado = self.edit_estado.get()
            try:
                fecha_ingreso = self.edit_fecha.get() if hasattr(self.edit_fecha,
                                                                 'get') else self.edit_fecha.get_date().isoformat()
            except:
                fecha_ingreso = ""
            deposito = self.edit_deposito.get().strip()
            contacto_emergencia = self.edit_contacto.get().strip()
            telefono_emergencia = self.edit_tel_emergencia.get().strip()
            relacion_emergencia = self.edit_relacion.get()
            notas = self.edit_notas.get(1.0, tk.END).strip()

            # Validaciones básicas
            if not nombre:
                messagebox.showwarning("Campo requerido", "El nombre es obligatorio.")
                self.edit_nombre.focus()
                return

            if not apto:
                messagebox.showwarning("Campo requerido", "El apartamento es obligatorio.")
                self.edit_apto.focus()
                return

            if not renta:
                messagebox.showwarning("Campo requerido", "La renta es obligatoria.")
                self.edit_renta.focus()
                return

            # Validación de renta
            try:
                renta = float(renta)
                if renta <= 0:
                    messagebox.showerror("Error", "La renta debe ser un número positivo.")
                    self.edit_renta.focus()
                    return
            except ValueError:
                messagebox.showerror("Error", "La renta debe ser un número válido.")
                self.edit_renta.focus()
                return

            # Validación de depósito
            deposito_valor = 0
            if deposito:
                try:
                    deposito_valor = float(deposito)
                    if deposito_valor < 0:
                        messagebox.showerror("Error", "El depósito no puede ser negativo.")
                        self.edit_deposito.focus()
                        return
                except ValueError:
                    messagebox.showerror("Error", "El depósito debe ser un número válido.")
                    self.edit_deposito.focus()
                    return

            # Validación de email
            if email and '@' not in email:
                messagebox.showwarning("Email inválido", "Por favor ingresa un email válido.")
                self.edit_email.focus()
                return

            # Procesar archivos si se cambiaron
            archivos_actualizados = {}

            # Verificar si se seleccionó nuevo archivo de identificación
            if hasattr(self, 'edit_id_file_path') and self.edit_id_file_path:
                # Si la ruta actual no es la misma que tenía antes, es un archivo nuevo
                conn = sqlite3.connect('edificio.db')
                cursor = conn.cursor()
                cursor.execute("SELECT archivo_identificacion FROM inquilinos WHERE id = ?", (inquilino_id,))
                archivo_actual = cursor.fetchone()[0]
                conn.close()

                if self.edit_id_file_path != archivo_actual:
                    # Es un archivo nuevo, copiarlo
                    try:
                        carpeta_inquilino = f"Archivos_Inquilinos/{inquilino_id}_{nombre.replace(' ', '_')}"
                        if not os.path.exists(carpeta_inquilino):
                            os.makedirs(carpeta_inquilino)

                        extension = os.path.splitext(self.edit_id_file_path)[1]
                        nuevo_nombre = f"identificacion_{inquilino_id}{extension}"
                        ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                        shutil.copy2(self.edit_id_file_path, ruta_destino)
                        archivos_actualizados['identificacion'] = ruta_destino
                    except Exception as e:
                        logging.error(f"Error copiando archivo ID: {e}")

            # Verificar si se seleccionó nuevo archivo de contrato
            if hasattr(self, 'edit_contract_file_path') and self.edit_contract_file_path:
                conn = sqlite3.connect('edificio.db')
                cursor = conn.cursor()
                cursor.execute("SELECT archivo_contrato FROM inquilinos WHERE id = ?", (inquilino_id,))
                archivo_actual = cursor.fetchone()[0]
                conn.close()

                if self.edit_contract_file_path != archivo_actual:
                    # Es un archivo nuevo, copiarlo
                    try:
                        carpeta_inquilino = f"Archivos_Inquilinos/{inquilino_id}_{nombre.replace(' ', '_')}"
                        if not os.path.exists(carpeta_inquilino):
                            os.makedirs(carpeta_inquilino)

                        extension = os.path.splitext(self.edit_contract_file_path)[1]
                        nuevo_nombre = f"contrato_{inquilino_id}{extension}"
                        ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                        shutil.copy2(self.edit_contract_file_path, ruta_destino)
                        archivos_actualizados['contrato'] = ruta_destino
                    except Exception as e:
                        logging.error(f"Error copiando archivo contrato: {e}")

            # Actualizar base de datos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Query base de actualización
            update_query = """
                UPDATE inquilinos 
                SET nombre = ?, apartamento = ?, renta = ?, identificacion = ?, email = ?, 
                    celular = ?, profesion = ?, fecha_ingreso = ?, deposito = ?, estado = ?,
                    contacto_emergencia = ?, telefono_emergencia = ?, relacion_emergencia = ?, notas = ?
            """
            update_params = [nombre, apto, renta, identificacion, email, celular, profesion,
                             fecha_ingreso, deposito_valor, estado, contacto_emergencia,
                             telefono_emergencia, relacion_emergencia, notas]

            # Agregar actualización de archivos si hay cambios
            if archivos_actualizados:
                if 'identificacion' in archivos_actualizados:
                    update_query += ", archivo_identificacion = ?, fecha_archivo_id = ?"
                    update_params.extend([archivos_actualizados['identificacion'],
                                          datetime.datetime.now().isoformat()])

                if 'contrato' in archivos_actualizados:
                    update_query += ", archivo_contrato = ?, fecha_archivo_contrato = ?"
                    update_params.extend([archivos_actualizados['contrato'],
                                          datetime.datetime.now().isoformat()])

            update_query += " WHERE id = ?"
            update_params.append(inquilino_id)

            cursor.execute(update_query, update_params)
            conn.commit()
            conn.close()

            # Mensaje de éxito
            mensaje_exito = f"Inquilino {nombre} actualizado exitosamente."
            if archivos_actualizados:
                archivos_info = []
                if 'identificacion' in archivos_actualizados:
                    archivos_info.append("identificación")
                if 'contrato' in archivos_actualizados:
                    archivos_info.append("contrato")
                mensaje_exito += f"\n\nArchivos actualizados: {', '.join(archivos_info)}"

            messagebox.showinfo("✅ Éxito", mensaje_exito)

            # Recargar lista y estadísticas
            self.cargar_inquilinos()
            self.actualizar_estadisticas()

            # Cerrar ventana modal
            cleanup_function()

        except Exception as e:
            logging.error(f"Error actualizando inquilino: {e}")
            messagebox.showerror("Error", f"Error actualizando inquilino: {e}")

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

class BackupModule:
    def __init__(self, manager):
        self.manager = manager
        self.backup_config_file = "backup_config.json"
        self.load_backup_config()

    def load_backup_config(self):
        """Carga la configuración de respaldos"""
        try:
            if os.path.exists(self.backup_config_file):
                with open(self.backup_config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "auto_backup": True,
                    "backup_folder": "Respaldos",
                    "max_backups": 10,
                    "include_pdfs": True,
                    "backup_on_exit": True
                }
                self.save_backup_config()
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando configuración: {e}")
            self.config = {}

    def save_backup_config(self):
        """Guarda la configuración de respaldos"""
        try:
            with open(self.backup_config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {e}")

    def setup_ui(self, parent):
        """Configura la interfaz del módulo de respaldos"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill="both", expand=True)

        # Título
        title_label = ttk.Label(frame, text="Sistema de Respaldos",
                                font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        # Frame de respaldo manual
        manual_frame = ttk.LabelFrame(frame, text="Respaldo Manual", padding="10")
        manual_frame.pack(fill="x", pady=10)

        # Botones de respaldo manual
        btn_frame1 = ttk.Frame(manual_frame)
        btn_frame1.pack(fill="x", pady=5)

        ttk.Button(btn_frame1, text="🗄️ Crear Respaldo Completo",
                   command=self.crear_respaldo_manual).pack(side="left", padx=(0, 10))

        ttk.Button(btn_frame1, text="📁 Abrir Carpeta de Respaldos",
                   command=self.abrir_carpeta_respaldos).pack(side="left")

        # Frame de configuración automática
        auto_frame = ttk.LabelFrame(frame, text="Configuración Automática", padding="10")
        auto_frame.pack(fill="x", pady=10)

        # Checkbox para respaldo automático
        self.auto_backup_var = tk.BooleanVar(value=self.config.get("auto_backup", True))
        ttk.Checkbutton(auto_frame, text="Activar respaldos automáticos al cerrar",
                        variable=self.auto_backup_var,
                        command=self.update_config).pack(anchor="w", pady=2)

        # Checkbox para incluir PDFs
        self.include_pdfs_var = tk.BooleanVar(value=self.config.get("include_pdfs", True))
        ttk.Checkbutton(auto_frame, text="Incluir archivos PDF en respaldos",
                        variable=self.include_pdfs_var,
                        command=self.update_config).pack(anchor="w", pady=2)

        # Configuración de cantidad de respaldos
        qty_frame = ttk.Frame(auto_frame)
        qty_frame.pack(fill="x", pady=5)

        ttk.Label(qty_frame, text="Mantener últimos:").pack(side="left")
        self.max_backups_var = tk.StringVar(value=str(self.config.get("max_backups", 10)))
        max_backups_spin = ttk.Spinbox(qty_frame, from_=1, to=50, width=5,
                                       textvariable=self.max_backups_var,
                                       command=self.update_config)
        max_backups_spin.pack(side="left", padx=5)
        ttk.Label(qty_frame, text="respaldos").pack(side="left")

        # Frame de información
        info_frame = ttk.LabelFrame(frame, text="Información", padding="10")
        info_frame.pack(fill="both", expand=True, pady=10)

        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical",
                                       command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)

        self.info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        # Cargar información inicial
        self.actualizar_info()

    def update_config(self):
        """Actualiza la configuración cuando cambian los valores"""
        self.config["auto_backup"] = self.auto_backup_var.get()
        self.config["include_pdfs"] = self.include_pdfs_var.get()
        try:
            self.config["max_backups"] = int(self.max_backups_var.get())
        except ValueError:
            self.config["max_backups"] = 10

        self.save_backup_config()

    def crear_respaldo_manual(self):
        """Crea un respaldo manual completo"""
        try:
            # Permitir al usuario elegir ubicación
            carpeta_destino = filedialog.askdirectory(
                title="Seleccionar carpeta para respaldo",
                initialdir=os.path.expanduser("~")
            )

            if not carpeta_destino:
                return

            resultado = self.crear_respaldo(carpeta_destino, manual=True)

            if resultado:
                messagebox.showinfo("Respaldo Exitoso",
                                    f"Respaldo creado exitosamente en:\n{resultado}")
                self.actualizar_info()

        except Exception as e:
            messagebox.showerror("Error", f"Error creando respaldo manual: {e}")

    def crear_respaldo_automatico(self):
        """Crea un respaldo automático al cerrar la aplicación"""
        if not self.config.get("auto_backup", True):
            return

        try:
            carpeta_respaldos = self.config.get("backup_folder", "Respaldos")
            resultado = self.crear_respaldo(carpeta_respaldos, manual=False)

            if resultado:
                self.limpiar_respaldos_antiguos()
                print(f"Respaldo automático creado: {resultado}")

        except Exception as e:
            print(f"Error en respaldo automático: {e}")

    def crear_respaldo(self, carpeta_destino, manual=True):
        """Función principal para crear respaldos"""
        try:
            # Crear carpeta de respaldos si no existe
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)

            # Generar nombre único para el respaldo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            tipo = "Manual" if manual else "Auto"
            nombre_respaldo = f"Respaldo_{tipo}_{timestamp}"

            carpeta_respaldo = os.path.join(carpeta_destino, nombre_respaldo)
            os.makedirs(carpeta_respaldo)

            archivos_copiados = []

            # 1. Copiar base de datos
            if os.path.exists("edificio.db"):
                shutil.copy2("edificio.db", os.path.join(carpeta_respaldo, "edificio.db"))
                archivos_copiados.append("Base de datos (edificio.db)")

            # 2. Copiar archivos de configuración
            config_files = ["backup_config.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, os.path.join(carpeta_respaldo, config_file))
                    archivos_copiados.append(f"Configuración ({config_file})")

            # 3. Copiar PDFs si está habilitado
            if self.config.get("include_pdfs", True):
                pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
                if pdf_files:
                    pdf_folder = os.path.join(carpeta_respaldo, "PDFs")
                    os.makedirs(pdf_folder)

                    for pdf_file in pdf_files:
                        shutil.copy2(pdf_file, os.path.join(pdf_folder, pdf_file))

                    archivos_copiados.append(f"Archivos PDF ({len(pdf_files)} archivos)")

            # 4. Crear archivo de información del respaldo
            info_respaldo = {
                "fecha_respaldo": datetime.datetime.now().isoformat(),
                "tipo": tipo,
                "archivos_incluidos": archivos_copiados,
                "version_app": "1.1"
            }

            with open(os.path.join(carpeta_respaldo, "info_respaldo.json"), 'w') as f:
                json.dump(info_respaldo, f, indent=2)

            # 5. Crear ZIP del respaldo
            zip_filename = f"{carpeta_respaldo}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(carpeta_respaldo):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, carpeta_respaldo)
                        zipf.write(file_path, arcname)

            # Eliminar carpeta temporal, mantener solo ZIP
            shutil.rmtree(carpeta_respaldo)

            return zip_filename

        except Exception as e:
            raise Exception(f"Error creando respaldo: {e}")

    def limpiar_respaldos_antiguos(self):
        """Elimina respaldos antiguos manteniendo solo los más recientes"""
        try:
            carpeta_respaldos = self.config.get("backup_folder", "Respaldos")
            max_respaldos = self.config.get("max_backups", 10)

            if not os.path.exists(carpeta_respaldos):
                return

            # Obtener todos los archivos de respaldo
            archivos_respaldo = []
            for archivo in os.listdir(carpeta_respaldos):
                if archivo.startswith("Respaldo_") and archivo.endswith(".zip"):
                    ruta_completa = os.path.join(carpeta_respaldos, archivo)
                    fecha_mod = os.path.getmtime(ruta_completa)
                    archivos_respaldo.append((fecha_mod, ruta_completa))

            # Ordenar por fecha (más reciente primero)
            archivos_respaldo.sort(reverse=True)

            # Eliminar respaldos antiguos
            for _, ruta_archivo in archivos_respaldo[max_respaldos:]:
                os.remove(ruta_archivo)
                print(f"Respaldo antiguo eliminado: {os.path.basename(ruta_archivo)}")

        except Exception as e:
            print(f"Error limpiando respaldos antiguos: {e}")

    def abrir_carpeta_respaldos(self):
        """Abre la carpeta de respaldos en el explorador"""
        try:
            carpeta_respaldos = self.config.get("backup_folder", "Respaldos")

            if not os.path.exists(carpeta_respaldos):
                os.makedirs(carpeta_respaldos)

            # Abrir carpeta en el explorador
            if os.name == 'nt':  # Windows
                os.startfile(carpeta_respaldos)
            elif os.name == 'posix':  # macOS y Linux
                os.system(f'open "{carpeta_respaldos}"')

        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo carpeta: {e}")

    def actualizar_info(self):
        """Actualiza la información mostrada en el panel"""
        try:
            self.info_text.delete(1.0, tk.END)

            info = "=== INFORMACIÓN DEL SISTEMA DE RESPALDOS ===\n\n"

            # Configuración actual
            info += "Configuración Actual:\n"
            info += f"• Respaldo automático: {'Activado' if self.config.get('auto_backup') else 'Desactivado'}\n"
            info += f"• Incluir PDFs: {'Sí' if self.config.get('include_pdfs') else 'No'}\n"
            info += f"• Máximo respaldos: {self.config.get('max_backups', 10)}\n"
            info += f"• Carpeta de respaldos: {self.config.get('backup_folder', 'Respaldos')}\n\n"

            # Estado de la base de datos
            if os.path.exists("edificio.db"):
                tamaño_db = os.path.getsize("edificio.db")
                fecha_db = datetime.datetime.fromtimestamp(os.path.getmtime("edificio.db"))
                info += f"Base de Datos:\n"
                info += f"• Tamaño: {tamaño_db / 1024:.2f} KB\n"
                info += f"• Última modificación: {fecha_db.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Archivos PDF
            pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
            if pdf_files:
                info += f"Archivos PDF encontrados: {len(pdf_files)}\n"
                for pdf in pdf_files[:5]:  # Mostrar solo los primeros 5
                    info += f"• {pdf}\n"
                if len(pdf_files) > 5:
                    info += f"• ... y {len(pdf_files) - 5} más\n"
            else:
                info += "No se encontraron archivos PDF\n"

            info += "\n=== RECOMENDACIONES ===\n"
            info += "• Crea respaldos regularmente\n"
            info += "• Guarda respaldos en ubicaciones seguras (USB, nube)\n"
            info += "• Verifica los respaldos ocasionalmente\n"
            info += "• Mantén múltiples copias de seguridad\n"

            self.info_text.insert(tk.END, info)

        except Exception as e:
            self.info_text.insert(tk.END, f"Error actualizando información: {e}")

class ApartmentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Edificio")
        self.root.state('zoomed')

        # Inicializar base de datos
        self.setup_database()

        # Configurar módulos
        self.tenant_module = TenantModule(self)
        self.payment_module = PaymentModule(self)
        self.expense_module = ExpenseModule(self)
        self.report_module = ReportModule(self)
        self.backup_module = BackupModule(self)

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

        # === MIGRACIÓN AUTOMÁTICA DE COLUMNAS ===
        # Agregar columnas faltantes para compatibilidad con ejecutables
        try:
            cursor.execute("PRAGMA table_info(inquilinos)")
            existing_columns = [col[1] for col in cursor.fetchall()]

            # Definir todas las columnas nuevas que necesitamos
            required_columns = [
                ("identificacion", "TEXT"),
                ("email", "TEXT"),
                ("celular", "TEXT"),
                ("profesion", "TEXT"),
                ("fecha_ingreso", "TEXT"),
                ("deposito", "REAL DEFAULT 0"),
                ("estado", "TEXT DEFAULT 'Activo'"),
                ("contacto_emergencia", "TEXT"),
                ("telefono_emergencia", "TEXT"),
                ("relacion_emergencia", "TEXT"),
                ("notas", "TEXT")
            ]

            # Agregar solo las columnas que no existen
            columns_added = 0
            for col_name, col_type in required_columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE inquilinos ADD COLUMN {col_name} {col_type}")
                        columns_added += 1
                        print(f"✅ Columna agregada automáticamente: {col_name}")
                    except sqlite3.Error as e:
                        print(f"⚠️ Error agregando columna {col_name}: {e}")

            if columns_added > 0:
                print(f"🔄 Migración automática completada: {columns_added} columnas agregadas")
            else:
                print("✅ Base de datos ya está actualizada")

        except Exception as e:
            print(f"❌ Error en migración automática: {e}")
            # Continúa funcionando aunque falle la migración

            # === MIGRACIÓN PARA ARCHIVOS ADJUNTOS ===
            try:
                # Verificar si las columnas de archivos existen
                cursor.execute("PRAGMA table_info(inquilinos)")
                existing_columns = [col[1] for col in cursor.fetchall()]

                # Columnas para archivos adjuntos
                file_columns = [
                    ("archivo_identificacion", "TEXT"),  # Ruta del archivo de identificación
                    ("archivo_contrato", "TEXT"),  # Ruta del archivo de contrato
                    ("fecha_archivo_id", "TEXT"),  # Fecha de carga del archivo ID
                    ("fecha_archivo_contrato", "TEXT")  # Fecha de carga del contrato
                ]

                # Agregar columnas faltantes
                for col_name, col_type in file_columns:
                    if col_name not in existing_columns:
                        cursor.execute(f"ALTER TABLE inquilinos ADD COLUMN {col_name} {col_type}")
                        print(f"✅ Columna de archivo agregada: {col_name}")

            except Exception as e:
                print(f"Error en migración de archivos: {e}")

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
        self.tab_respaldos = ttk.Frame(self.notebook)

        # Añadir pestañas al notebook
        self.notebook.add(self.tab_inquilinos, text='Inquilinos')
        self.notebook.add(self.tab_pagos, text='Ingresos')
        self.notebook.add(self.tab_gastos, text='Gastos')
        self.notebook.add(self.tab_reportes, text='Reportes')
        self.notebook.add(self.tab_respaldos, text='Respaldos')

        self.notebook.pack(expand=True, fill="both")

        # Configurar contenido de las pestañas
        self.tenant_module.setup_ui(self.tab_inquilinos)
        self.payment_module.setup_ui(self.tab_pagos)
        self.expense_module.setup_ui(self.tab_gastos)
        self.report_module.setup_ui(self.tab_reportes)
        self.backup_module.setup_ui(self.tab_respaldos)
        self.notebook.select(self.tab_inquilinos)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Función llamada al cerrar la aplicación"""
        # Crear respaldo automático antes de cerrar
        if hasattr(self, 'backup_module'):
            self.backup_module.crear_respaldo_automatico()

        # Cerrar aplicación
        self.root.destroy()

# Función principal
def main():
    root = tk.Tk()
    app = ApartmentManager(root)
    root.mainloop()

# Llamada a la función principal
if __name__ == "__main__":
    main()