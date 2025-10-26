"""Interfaz moderna y reforzada para el extractor bancario."""

import math
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from config_segura import ConfigSegura
from logging_utils import configurar_logger


# 🎨 Paleta de colores moderna (mejorada para legibilidad)
COLORS = {
    'bg_dark': '#0a0e1a',            # Fondo principal (más claro)
    'bg_darker': '#060913',          # Fondo más oscuro
    'bg_card': '#121829',            # Contenedores (más contraste)
    'accent': '#38bdf8',             # Azul cyan brillante
    'accent_hover': '#0ea5e9',       # Hover para acento
    'success': '#06b6d4',            # Botón principal (cyan más oscuro, mejor contraste)
    'warning': '#facc15',            # Advertencias
    'text': '#ffffff',               # Texto principal (blanco puro)
    'text_dim': '#cbd5e1',           # Texto secundario (más claro)
    'border': '#2d3748',             # Bordes más visibles
    'input_bg': '#1e293b',           # Fondo de inputs (más claro)
    'input_border': '#334155',       # Borde inputs (más visible)
    'shadow': '#020617',             # Sombra suave
    'gradient_start': '#1e293b',     # Gradiente header (más claro)
    'gradient_end': '#0a0e1a',       # Gradiente header (fin)
    'button_disabled': '#334155',    # Botón deshabilitado (más visible)
    'button_secondary': '#475569',   # Botones secundarios
    'button_secondary_hover': '#64748b'  # Hover secundario
}


def hex_to_rgb(value):
    """Convierte un color hex a tupla RGB."""
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Convierte RGB a color hexadecimal."""
    return '#%02x%02x%02x' % rgb


def blend_colors(color_a, color_b, factor):
    """Mezcla dos colores hex con un factor [0-1]."""
    factor = max(0.0, min(1.0, factor))
    ra, ga, ba = hex_to_rgb(color_a)
    rb, gb, bb = hex_to_rgb(color_b)
    rc = int(ra + (rb - ra) * factor)
    gc = int(ga + (gb - ga) * factor)
    bc = int(ba + (bb - ba) * factor)
    return rgb_to_hex((rc, gc, bc))


class ModernButton(tk.Canvas):
    """Botón moderno personalizado con efectos hover y brillo sutil."""

    def __init__(self, parent, text, command, bg_color, fg_color, width=200, height=50):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS['bg_dark'], highlightthickness=0, bd=0)

        self.command = command
        self.base_color = bg_color
        self.fg_color = fg_color
        self.hover_color = COLORS['accent_hover']
        self.is_hover = False
        self.pulse_enabled = True
        self.glow_phase = 0.0

        # Sombra suave
        self.shadow = self.create_rounded_rect(6, 8, width - 2, height + 6,
                                               radius=14, fill=COLORS['shadow'])

        # Crear rectángulo con bordes redondeados
        self.rect = self.create_rounded_rect(0, 0, width, height,
                                             radius=12, fill=self.base_color)
        self.text_id = self.create_text(width / 2, height / 2,
                                        text=text, fill=fg_color,
                                        font=('SF Pro Display', 14, 'bold'))

        self.tag_lower(self.shadow)

        # Eventos
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)

        self.after(40, self.animate_glow)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Crea rectángulo con bordes redondeados"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        """Efecto hover"""
        self.is_hover = True
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor='hand2')

    def on_leave(self, e):
        """Quitar hover"""
        self.is_hover = False
        self.itemconfig(self.rect, fill=self.base_color)
        self.config(cursor='')

    def on_click(self, e):
        """Ejecutar comando"""
        if self.command:
            self.command()

    def set_base_color(self, color):
        """Actualiza el color base del botón."""
        self.base_color = color
        if not self.is_hover:
            self.itemconfig(self.rect, fill=self.base_color)

    def set_text(self, text):
        """Actualiza el texto del botón."""
        self.itemconfig(self.text_id, text=text)

    def set_text_color(self, color):
        """Actualiza el color del texto del botón."""
        self.fg_color = color
        self.itemconfig(self.text_id, fill=color)

    def set_pulse(self, enabled):
        """Activa o desactiva la animación de brillo."""
        self.pulse_enabled = enabled
        if not enabled and not self.is_hover:
            self.itemconfig(self.rect, fill=self.base_color)

    def animate_glow(self):
        """Animación de brillo sutil."""
        if self.pulse_enabled and not self.is_hover:
            pulse = (math.sin(self.glow_phase) + 1) / 2  # 0-1
            blend_factor = 0.08 + pulse * 0.10
            glow_color = blend_colors(self.base_color, COLORS['accent'], blend_factor)
            self.itemconfig(self.rect, fill=glow_color)
            self.glow_phase += 0.12
        elif not self.is_hover:
            self.itemconfig(self.rect, fill=self.base_color)

        self.after(45, self.animate_glow)


logger, LOG_PATH = configurar_logger("app.ui")


class ExtractorModerno:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractor de Extractos Bancarios")
        
        # Configurar ventana
        window_width = 900
        window_height = 750
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(False, False)
        
        # Configuración segura
        self.config_segura = ConfigSegura()
        self.logger = logger
        self.log_file_path = LOG_PATH
        self.secure_dir = Path(self.config_segura.get_ubicacion())

        # Variables
        self.api_key = tk.StringVar()
        self.password = tk.StringVar()
        self.carpeta = tk.StringVar()
        self.procesando = False
        self.modo_edicion = tk.BooleanVar(value=False)
        
        # Cargar configuración
        self.cargar_configuracion()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Atajos de teclado
        self.root.bind_all("<Command-v>", self.pegar)
        self.root.bind_all("<Control-v>", self.pegar)

        self.logger.info("Aplicación inicializada")

    def pegar(self, event=None):
        """Maneja pegado desde portapapeles"""
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Entry):
                texto = self.root.clipboard_get()
                widget.insert(tk.INSERT, texto)
                return "break"
        except:
            pass
    
    def cargar_configuracion(self):
        """Carga configuración guardada"""
        if self.config_segura.existe_config():
            config = self.config_segura.cargar()
            if config:
                self.api_key.set(config.get('api_key', ''))
                self.password.set(config.get('password', ''))
                self.carpeta.set(config.get('carpeta', ''))
                if config.get('api_key'):
                    self.modo_edicion.set(False)
    
    def crear_interfaz(self):
        """Crea la interfaz moderna"""
        
        self.wave_offset = -240

        # 🎨 HEADER CON GRADIENTE
        self.header_canvas = tk.Canvas(
            self.root,
            height=120,
            bg=COLORS['bg_darker'],
            highlightthickness=0,
            bd=0
        )
        self.header_canvas.pack(fill='x')

        # Línea de acento animada
        self.header_wave = self.header_canvas.create_rectangle(
            -240, 116, -20, 120,
            fill=COLORS['accent'],
            outline='',
            width=0,
            tags='accent_wave'
        )

        # Título grande
        self.header_canvas.create_text(
            450,
            45,
            text="🤖 Extractor Bancario IA",
            font=('SF Pro Display', 32, 'bold'),
            fill=COLORS['text'],
            tags='header_title'
        )

        # Subtítulo
        self.header_canvas.create_text(
            450,
            85,
            text="Procesa tus extractos con Inteligencia Artificial",
            font=('SF Pro Text', 13),
            fill=COLORS['text_dim'],
            tags='header_subtitle'
        )

        # Botones de acción del header
        header_buttons = tk.Frame(self.header_canvas, bg=COLORS['bg_darker'], highlightthickness=0)
        self.header_canvas.create_window(820, 60, window=header_buttons)

        btn_seguridad = tk.Button(
            header_buttons,
            text="🔒 Seguridad",
            font=('SF Pro Text', 10, 'bold'),
            command=self.mostrar_info_seguridad
        )
        btn_seguridad.pack(side='left', padx=5)
        self.estilizar_boton_flat(btn_seguridad, COLORS['bg_card'], COLORS['accent_hover'], padding_y=6, padding_x=12)

        btn_logs = tk.Button(
            header_buttons,
            text="📁 Logs",
            font=('SF Pro Text', 10, 'bold'),
            command=self.abrir_logs
        )
        btn_logs.pack(side='left', padx=5)
        self.estilizar_boton_flat(btn_logs, COLORS['bg_card'], COLORS['accent_hover'], padding_y=6, padding_x=12)

        # Container principal con padding
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=40, pady=30)

        # 📦 CARD DE CONFIGURACIÓN
        config_card = tk.Frame(
            main,
            bg=COLORS['bg_card'],
            relief='flat',
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS['border']
        )
        config_card.pack(fill='x', pady=(0, 20))

        config_inner = tk.Frame(config_card, bg=COLORS['bg_card'], bd=0)
        config_inner.pack(fill='x', padx=25, pady=25)

        # Estado
        estado_frame = tk.Frame(config_inner, bg=COLORS['bg_card'])
        estado_frame.pack(fill='x', pady=(0, 20))

        self.label_estado = tk.Label(
            estado_frame,
            text="",
            font=('SF Pro Text', 11),
            fg=COLORS['text'],
            bg=COLORS['bg_card']
        )
        self.label_estado.pack(side='left')

        self.badge_seguridad = tk.Label(
            estado_frame,
            text=f"🔐 Directorio seguro: {self.secure_dir}",
            font=('SF Pro Text', 9),
            fg=COLORS['accent'],
            bg=COLORS['bg_card']
        )
        self.badge_seguridad.pack(side='left', padx=(10, 0))

        # Botón editar moderno
        self.btn_editar_frame = tk.Frame(estado_frame, bg=COLORS['bg_card'])
        self.btn_editar_frame.pack(side='right')
        
        # API Key
        self.crear_campo(config_inner, "🔑  API Key de Gemini", self.api_key, 
                        es_password=True, link="makersuite.google.com/app/apikey")
        
        # Password
        self.crear_campo(config_inner, "🔐  Contraseña de PDFs", self.password, 
                        es_password=True)
        
        # Carpeta
        tk.Label(
            config_inner,
            text="📁  Carpeta con PDFs",
            font=('SF Pro Text', 12, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['bg_card']
        ).pack(anchor='w', pady=(15, 8))
        
        carpeta_frame = tk.Frame(config_inner, bg=COLORS['bg_card'])
        carpeta_frame.pack(fill='x')
        
        self.carpeta_entry = tk.Entry(
            carpeta_frame,
            textvariable=self.carpeta,
            font=('SF Pro Mono', 11),
            bg=COLORS['input_bg'],
            fg=COLORS['text'],
            relief='flat',
            insertbackground=COLORS['accent'],
            state='readonly',
            readonlybackground=COLORS['input_bg']
        )
        self.carpeta_entry.pack(side='left', fill='x', expand=True,
                               ipady=10, padx=(0, 10))
        self.estilizar_entry(self.carpeta_entry)

        self.btn_carpeta = tk.Button(
            carpeta_frame,
            text="Buscar",
            font=('SF Pro Text', 11),
            padx=20,
            command=self.seleccionar_carpeta
        )
        self.btn_carpeta.pack(side='right')
        self.estilizar_boton_flat(
            self.btn_carpeta,
            COLORS['accent'],
            COLORS['accent_hover'],
            fg=COLORS['bg_dark'],
            padding_y=8,
            padding_x=None
        )

        # Botón guardar config
        self.btn_guardar_config = tk.Button(
            config_inner,
            text="💾  Guardar Configuración",
            font=('SF Pro Text', 12, 'bold'),
            command=self.guardar_configuracion
        )
        self.estilizar_boton_flat(
            self.btn_guardar_config,
            COLORS['accent'],
            COLORS['accent_hover'],
            fg=COLORS['bg_dark'],
            padding_y=12,
            padding_x=None
        )

        acciones_frame = tk.Frame(config_inner, bg=COLORS['bg_card'])
        acciones_frame.pack(fill='x', pady=(15, 0))

        self.btn_rotar_clave = tk.Button(
            acciones_frame,
            text="🔁 Rotar clave de cifrado",
            font=('SF Pro Text', 10, 'bold'),
            command=self.rotar_clave
        )
        self.btn_rotar_clave.pack(side='left')
        self.estilizar_boton_flat(
            self.btn_rotar_clave,
            COLORS['button_secondary'],
            COLORS['button_secondary_hover'],
            fg=COLORS['text'],
            padding_y=8,
            padding_x=14
        )

        self.btn_borrar_config = tk.Button(
            acciones_frame,
            text="🧹 Borrar configuración",
            font=('SF Pro Text', 10, 'bold'),
            command=self.eliminar_configuracion
        )
        self.btn_borrar_config.pack(side='left', padx=(10, 0))
        self.estilizar_boton_flat(
            self.btn_borrar_config,
            COLORS['button_secondary'],
            COLORS['button_secondary_hover'],
            fg=COLORS['text'],
            padding_y=8,
            padding_x=14
        )

        # 🚀 BOTÓN PRINCIPAL GRANDE
        btn_container = tk.Frame(main, bg=COLORS['bg_dark'])
        btn_container.pack(fill='x', pady=(0, 20))
        
        self.btn_procesar = ModernButton(
            btn_container,
            text="🚀  PROCESAR EXTRACTOS",
            command=self.iniciar_procesamiento,
            bg_color=COLORS['success'],
            fg_color=COLORS['bg_dark'],
            width=820,
            height=60
        )
        self.btn_procesar.pack()
        
        # 📋 LOG MODERNO
        tk.Label(
            main,
            text="📋  Log del Proceso",
            font=('SF Pro Text', 13, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['bg_dark']
        ).pack(anchor='w', pady=(0, 10))
        
        log_frame = tk.Frame(
            main,
            bg=COLORS['bg_card'],
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            bd=0
        )
        log_frame.pack(fill='both', expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('SF Pro Mono', 10),
            bg=COLORS['input_bg'],
            fg=COLORS['text'],
            insertbackground=COLORS['accent'],
            relief='flat',
            wrap='word',
            padx=15,
            pady=15
        )
        self.log_text.pack(fill='both', expand=True, padx=2, pady=2)
        self.log_text.configure(highlightthickness=1, highlightbackground=COLORS['input_border'])

        # Barra de progreso
        self.progress = ttk.Progressbar(main, mode='indeterminate', style='Accent.Horizontal.TProgressbar')

        # Configurar estilo de progreso para un look más moderno
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Accent.Horizontal.TProgressbar',
            troughcolor=COLORS['bg_dark'],
            bordercolor=COLORS['bg_dark'],
            background=COLORS['accent'],
            lightcolor=COLORS['accent'],
            darkcolor=COLORS['accent_hover']
        )

        # 🔒 FOOTER
        footer = tk.Frame(self.root, bg=COLORS['bg_darker'], height=50)
        footer.pack(fill='x', side='bottom')
        
        tk.Label(
            footer,
            text="💡 Gemini 2.0 Flash • Encriptación AES-256 • 100% Gratuito",
            font=('SF Pro Text', 9),
            fg=COLORS['text_dim'],
            bg=COLORS['bg_darker']
        ).pack(pady=15)

        # Actualizar estado
        self.actualizar_estado_ui()
        self.root.after(150, self.iniciar_animaciones_ui)

    def iniciar_animaciones_ui(self):
        """Inicializa animaciones sutiles de la interfaz."""
        if not hasattr(self, 'header_canvas'):
            return
        self.render_header_gradient(self.header_canvas)
        self.animar_header_wave()

    def render_header_gradient(self, canvas):
        """Dibuja un gradiente en el encabezado."""
        width = canvas.winfo_width()
        if width <= 1:
            self.root.after(120, lambda: self.render_header_gradient(canvas))
            return

        canvas.delete('gradient')
        steps = 50
        for i in range(steps):
            ratio = i / (steps - 1)
            color = blend_colors(COLORS['gradient_start'], COLORS['gradient_end'], ratio)
            x1 = int(width / steps * i)
            x2 = int(width / steps * (i + 1))
            canvas.create_rectangle(x1, 0, x2, 120, fill=color, outline='', tags='gradient')

        canvas.tag_lower('gradient')
        canvas.tag_raise('accent_wave')
        canvas.tag_raise('header_title')
        canvas.tag_raise('header_subtitle')

    def animar_header_wave(self):
        """Crea una animación leve en la barra inferior del header."""
        if not hasattr(self, 'header_canvas'):
            return

        canvas = self.header_canvas
        width = canvas.winfo_width()
        if width <= 1:
            canvas.after(120, self.animar_header_wave)
            return

        self.wave_offset += 6
        if self.wave_offset > width + 200:
            self.wave_offset = -200

        canvas.coords(self.header_wave, self.wave_offset - 120, 116, self.wave_offset, 120)
        canvas.tag_raise('header_title')
        canvas.tag_raise('header_subtitle')
        canvas.after(60, self.animar_header_wave)

    def estilizar_boton_flat(self, boton, base_color, hover_color, fg=COLORS['text'], padding_y=8, padding_x=16):
        """Aplica estilo plano y animación hover a un botón estándar."""
        boton.configure(
            bg=base_color,
            fg=fg,
            activebackground=hover_color,
            activeforeground=fg,
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            cursor='hand2'
        )

        if padding_x is not None:
            boton.configure(padx=padding_x)
        if padding_y is not None:
            boton.configure(pady=padding_y)

        boton.bind('<Enter>', lambda e, color=hover_color: boton.config(bg=color))
        boton.bind('<Leave>', lambda e, color=base_color: boton.config(bg=color))

    def estilizar_entry(self, entry):
        """Aplica estilo de borde iluminado a un entry."""
        entry.configure(
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS['input_border'],
            highlightcolor=COLORS['accent'],
            insertwidth=2
        )

        entry.bind('<FocusIn>', lambda e, widget=entry: widget.config(highlightbackground=COLORS['accent']))
        entry.bind('<FocusOut>', lambda e, widget=entry: widget.config(highlightbackground=COLORS['input_border']))

    def crear_campo(self, parent, label, variable, es_password=False, link=None):
        """Crea un campo de entrada moderno"""
        # Label
        label_frame = tk.Frame(parent, bg=COLORS['bg_card'])
        label_frame.pack(fill='x', pady=(15, 8))
        
        tk.Label(
            label_frame,
            text=label,
            font=('SF Pro Text', 12, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['bg_card']
        ).pack(side='left')
        
        if link:
            link_label = tk.Label(
                label_frame,
                text=f"  →  {link}",
                font=('SF Pro Text', 9),
                fg=COLORS['accent'],
                bg=COLORS['bg_card'],
                cursor='hand2'
            )
            link_label.pack(side='left')
            link_label.bind("<Button-1>", lambda e: self.abrir_url(f"https://{link}"))
        
        # Entry frame
        entry_frame = tk.Frame(parent, bg=COLORS['bg_card'])
        entry_frame.pack(fill='x')
        
        entry = tk.Entry(
            entry_frame,
            textvariable=variable,
            font=('SF Pro Mono', 11),
            bg=COLORS['input_bg'],
            fg=COLORS['text'],
            relief='flat',
            insertbackground=COLORS['accent'],
            show='•' if es_password else ''
        )
        entry.pack(side='left', fill='x', expand=True, ipady=10)
        self.estilizar_entry(entry)

        if es_password:
            # Botón toggle password
            toggle_btn = tk.Button(
                entry_frame,
                text="👁",
                font=('SF Pro Text', 12),
                command=lambda e=entry: self.toggle_password(e)
            )
            toggle_btn.pack(side='right', padx=(10, 0))
            self.estilizar_boton_flat(toggle_btn, COLORS['bg_darker'], COLORS['border'], padding_y=6, padding_x=10)

        # Guardar referencia
        if 'api' in label.lower():
            self.api_entry = entry
        elif 'contraseña' in label.lower():
            self.pwd_entry = entry
    
    def toggle_password(self, entry):
        """Alterna visibilidad de password"""
        if entry.cget('show') == '•':
            entry.config(show='')
        else:
            entry.config(show='•')
    
    def actualizar_estado_ui(self):
        """Actualiza UI según modo"""
        tiene_config = self.config_segura.existe_config() and self.api_key.get()
        en_edicion = self.modo_edicion.get()
        
        # Limpiar frame de botón editar
        for widget in self.btn_editar_frame.winfo_children():
            widget.destroy()
        
        if tiene_config and not en_edicion:
            # Modo lectura
            self.label_estado.config(
                text="✅  Configuración guardada de forma segura",
                fg=COLORS['success']
            )
            
            # Botón editar
            btn_edit = tk.Button(
                self.btn_editar_frame,
                text="✏️  Editar",
                font=('SF Pro Text', 10, 'bold'),
                command=self.toggle_edicion
            )
            btn_edit.pack()
            hover_color = blend_colors(COLORS['warning'], COLORS['accent'], 0.35)
            self.estilizar_boton_flat(
                btn_edit,
                COLORS['warning'],
                hover_color,
                fg=COLORS['bg_dark'],
                padding_y=6,
                padding_x=18
            )

            self.api_entry.config(state='disabled')
            self.pwd_entry.config(state='disabled')
            self.btn_carpeta.config(state='disabled')
            self.btn_guardar_config.pack_forget()
            self.btn_rotar_clave.config(state='normal')
            self.btn_borrar_config.config(state='normal')
        else:
            # Modo edición
            self.label_estado.config(
                text="⚠️  Configura y guarda tus credenciales",
                fg=COLORS['warning']
            )

            self.api_entry.config(state='normal')
            self.pwd_entry.config(state='normal')
            self.btn_carpeta.config(state='normal')
            self.btn_guardar_config.pack(fill='x', pady=(20, 0))
            self.btn_rotar_clave.config(state='disabled')
            self.btn_borrar_config.config(state='disabled')

    def toggle_edicion(self):
        """Toggle modo edición"""
        self.modo_edicion.set(not self.modo_edicion.get())
        self.actualizar_estado_ui()
    
    def abrir_url(self, url):
        """Abre URL"""
        import webbrowser
        webbrowser.open(url)
    
    def guardar_configuracion(self):
        """Guarda configuración"""
        if not self.api_key.get() or not self.password.get() or not self.carpeta.get():
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
        
        try:
            self.config_segura.guardar(
                self.api_key.get(),
                self.password.get(),
                self.carpeta.get()
            )
            
            messagebox.showinfo(
                "✅ Guardado",
                "Configuración guardada de forma segura y encriptada"
            )
            
            self.modo_edicion.set(False)
            self.actualizar_estado_ui()
            self.log("✅ Configuración guardada\n")
            self.logger.info("Configuración protegida actualizada")

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            self.logger.exception("Error al guardar la configuración")

    def seleccionar_carpeta(self):
        """Selecciona carpeta"""
        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta con PDFs",
            initialdir=self.carpeta.get() if self.carpeta.get() else os.path.expanduser("~")
        )
        if carpeta:
            self.carpeta.set(carpeta)
            self.log(f"📁 Carpeta: {carpeta}\n")
            self.logger.info("Carpeta de procesamiento establecida en %s", carpeta)

    def log(self, mensaje):
        """Agrega al log"""
        self.log_text.insert('end', mensaje)
        self.log_text.see('end')
        self.root.update()
        mensaje_linea = mensaje.strip()
        if mensaje_linea:
            self.logger.info(mensaje_linea)
    
    def validar_inputs(self):
        """Valida inputs"""
        if not self.api_key.get():
            messagebox.showerror("Error", "Falta API Key")
            return False
        if len(self.api_key.get().strip()) < 20:
            messagebox.showerror("Error", "La API Key parece inválida")
            return False
        if not self.password.get():
            messagebox.showerror("Error", "Falta contraseña")
            return False
        if not self.carpeta.get():
            messagebox.showerror("Error", "Falta carpeta")
            return False
        
        carpeta_path = Path(self.carpeta.get())
        if not carpeta_path.exists():
            messagebox.showerror("Error", "La carpeta no existe")
            return False
        
        pdfs = [p for p in carpeta_path.glob("*.pdf") if not p.name.endswith('.temp.pdf')]
        if not pdfs:
            messagebox.showerror("Error", "No hay PDFs en la carpeta")
            return False
        
        return True
    
    def iniciar_procesamiento(self):
        """Inicia procesamiento"""
        if self.procesando or not self.validar_inputs():
            return
        
        self.log_text.delete('1.0', 'end')
        self.procesando = True

        # Deshabilitar botón
        self.btn_procesar.set_pulse(False)
        self.btn_procesar.set_base_color(COLORS['button_disabled'])
        self.btn_procesar.set_text('⏳ PROCESANDO...')
        self.btn_procesar.set_text_color(COLORS['text'])

        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.start(10)
        
        thread = threading.Thread(target=self.procesar_pdfs, daemon=True)
        thread.start()

    def procesar_pdfs(self):
        """Procesa PDFs"""
        try:
            from procesador_gemini import ProcesadorGemini
            
            procesador = ProcesadorGemini(
                api_key=self.api_key.get(),
                password=self.password.get(),
                carpeta=self.carpeta.get(),
                log_callback=self.log
            )
            
            excel_path = procesador.procesar()
            
            if excel_path:
                self.log("\n" + "="*60 + "\n")
                self.log("🎉 ¡COMPLETADO!\n")
                self.log(f"📊 {excel_path.name}\n")
                self.log(f"📁 {excel_path}\n")
                self.root.after(0, lambda: self.preguntar_abrir(excel_path))
            else:
                self.log("\n❌ Error al generar Excel\n")

        except Exception as e:
            self.log(f"\n❌ Error: {str(e)}\n")
            self.logger.exception("Error inesperado durante el procesamiento")

        finally:
            self.root.after(0, self.finalizar_procesamiento)

    def finalizar_procesamiento(self):
        """Finaliza procesamiento"""
        self.procesando = False
        self.btn_procesar.set_base_color(COLORS['success'])
        self.btn_procesar.set_text('🚀  PROCESAR EXTRACTOS')
        self.btn_procesar.set_text_color(COLORS['bg_dark'])
        self.btn_procesar.set_pulse(True)
        self.progress.stop()
        self.progress.pack_forget()
    
    def preguntar_abrir(self, excel_path):
        """Pregunta si abrir Excel"""
        if messagebox.askyesno("Completado", f"¿Abrir {excel_path.name}?"):
            try:
                if sys.platform == 'darwin':
                    os.system(f'open "{excel_path}"')
                elif sys.platform == 'win32':
                    os.startfile(excel_path)
                else:
                    os.system(f'xdg-open "{excel_path}"')
            except:
                pass

    def mostrar_info_seguridad(self):
        mensaje = (
            "Tus credenciales se cifran con AES-256 usando llaves únicas por "
            "equipo. Cuando es posible se almacena la clave maestra en el "
            "llavero del sistema; de lo contrario se protege con permisos 600 "
            "dentro de la carpeta segura. Puedes rotar la clave o eliminar los "
            "datos desde el panel de configuración."
        )
        messagebox.showinfo("Seguridad", mensaje)

    def abrir_logs(self):
        try:
            if sys.platform == 'darwin':
                os.system(f'open "{self.log_file_path}"')
            elif sys.platform == 'win32':
                os.startfile(self.log_file_path)
            else:
                os.system(f'xdg-open "{self.log_file_path}"')
        except Exception:
            messagebox.showinfo("Logs", f"Archivo de logs: {self.log_file_path}")

    def rotar_clave(self):
        if messagebox.askyesno("Rotar clave", "¿Deseas generar una nueva clave de cifrado?" ):
            self.config_segura.rotar_clave()
            self.log("🔁 Clave de cifrado rotada\n")
            self.logger.info("El usuario rotó la clave de cifrado")

    def eliminar_configuracion(self):
        if messagebox.askyesno("Eliminar configuración", "¿Eliminar configuración cifrada? Esta acción no se puede deshacer."):
            self.config_segura.eliminar()
            self.api_key.set("")
            self.password.set("")
            self.carpeta.set("")
            self.modo_edicion.set(True)
            self.actualizar_estado_ui()
            self.log("🧹 Configuración eliminada\n")
            self.logger.warning("Configuración cifrada eliminada por el usuario")


def main():
    root = tk.Tk()
    app = ExtractorModerno(root)
    root.mainloop()


if __name__ == "__main__":
    main()

