"""
🌙 Extractor de Extractos Bancarios - UI Moderna Dark Mode
Diseño minimalista y moderno con tema oscuro
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import os
import sys
from config_segura import ConfigSegura


# 🎨 Paleta de colores moderna
COLORS = {
    'bg_dark': '#1a1a2e',           # Fondo principal oscuro
    'bg_darker': '#16213e',         # Fondo más oscuro
    'bg_card': '#0f3460',           # Fondo de tarjetas
    'accent': '#00d4ff',            # Azul cyan brillante
    'accent_hover': '#00b8e6',      # Azul hover
    'success': '#00ff88',           # Verde éxito
    'warning': '#ffa500',           # Naranja advertencia
    'text': '#e8e8e8',              # Texto principal
    'text_dim': '#a0a0a0',          # Texto secundario
    'border': '#2d3748',            # Bordes
    'input_bg': '#1f2937',          # Fondo de inputs
    'input_border': '#374151'       # Borde de inputs
}


class ModernButton(tk.Canvas):
    """Botón moderno personalizado con efectos hover"""
    
    def __init__(self, parent, text, command, bg_color, fg_color, width=200, height=50):
        super().__init__(parent, width=width, height=height, 
                        bg=COLORS['bg_dark'], highlightthickness=0)
        
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = COLORS['accent_hover']
        
        # Crear rectángulo con bordes redondeados
        self.rect = self.create_rounded_rect(0, 0, width, height, 
                                             radius=10, fill=bg_color)
        self.text_id = self.create_text(width/2, height/2, 
                                       text=text, fill=fg_color, 
                                       font=('SF Pro Display', 14, 'bold'))
        
        # Eventos
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
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
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor='hand2')
    
    def on_leave(self, e):
        """Quitar hover"""
        self.itemconfig(self.rect, fill=self.bg_color)
        self.config(cursor='')
    
    def on_click(self, e):
        """Ejecutar comando"""
        if self.command:
            self.command()


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
        
        # 🎨 HEADER CON GRADIENTE
        header = tk.Canvas(self.root, height=120, bg=COLORS['bg_darker'], 
                          highlightthickness=0)
        header.pack(fill='x')
        
        # Título grande
        header.create_text(450, 45, 
                          text="🤖 Extractor Bancario IA", 
                          font=('SF Pro Display', 32, 'bold'),
                          fill=COLORS['text'])
        
        # Subtítulo
        header.create_text(450, 85, 
                          text="Procesa tus extractos con Inteligencia Artificial", 
                          font=('SF Pro Text', 13),
                          fill=COLORS['text_dim'])
        
        # Container principal con padding
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=40, pady=30)
        
        # 📦 CARD DE CONFIGURACIÓN
        config_card = tk.Frame(main, bg=COLORS['bg_card'], relief='flat')
        config_card.pack(fill='x', pady=(0, 20))
        
        config_inner = tk.Frame(config_card, bg=COLORS['bg_card'])
        config_inner.pack(fill='x', padx=25, pady=25)
        
        # Estado
        estado_frame = tk.Frame(config_inner, bg=COLORS['bg_card'])
        estado_frame.pack(fill='x', pady=(0, 20))
        
        self.label_estado = tk.Label(
            estado_frame,
            text="",
            font=('SF Pro Text', 11),
            fg=COLORS['text_dim'],
            bg=COLORS['bg_card']
        )
        self.label_estado.pack(side='left')
        
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
        
        self.btn_carpeta = tk.Button(
            carpeta_frame,
            text="Buscar",
            font=('SF Pro Text', 11),
            bg=COLORS['bg_darker'],
            fg=COLORS['text'],
            activebackground=COLORS['border'],
            activeforeground=COLORS['text'],
            relief='flat',
            cursor='hand2',
            padx=20,
            command=self.seleccionar_carpeta
        )
        self.btn_carpeta.pack(side='right')
        
        # Botón guardar config
        self.btn_guardar_config = tk.Button(
            config_inner,
            text="💾  Guardar Configuración",
            font=('SF Pro Text', 12, 'bold'),
            bg=COLORS['accent'],
            fg=COLORS['bg_dark'],
            activebackground=COLORS['accent_hover'],
            activeforeground=COLORS['bg_dark'],
            relief='flat',
            cursor='hand2',
            pady=12,
            command=self.guardar_configuracion
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
        
        log_frame = tk.Frame(main, bg=COLORS['input_border'])
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
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main, mode='indeterminate')
        
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
        
        if es_password:
            # Botón toggle password
            toggle_btn = tk.Button(
                entry_frame,
                text="👁",
                font=('SF Pro Text', 12),
                bg=COLORS['bg_darker'],
                fg=COLORS['text'],
                activebackground=COLORS['border'],
                activeforeground=COLORS['text'],
                relief='flat',
                cursor='hand2',
                width=3,
                command=lambda e=entry: self.toggle_password(e)
            )
            toggle_btn.pack(side='right', padx=(10, 0))
        
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
                bg=COLORS['warning'],
                fg=COLORS['bg_dark'],
                activebackground=COLORS['accent_hover'],
                activeforeground=COLORS['bg_dark'],
                relief='flat',
                cursor='hand2',
                padx=15,
                pady=5,
                command=self.toggle_edicion
            )
            btn_edit.pack()
            
            self.api_entry.config(state='disabled')
            self.pwd_entry.config(state='disabled')
            self.btn_carpeta.config(state='disabled')
            self.btn_guardar_config.pack_forget()
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
    
    def seleccionar_carpeta(self):
        """Selecciona carpeta"""
        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta con PDFs",
            initialdir=self.carpeta.get() if self.carpeta.get() else os.path.expanduser("~")
        )
        if carpeta:
            self.carpeta.set(carpeta)
            self.log(f"📁 Carpeta: {carpeta}\n")
    
    def log(self, mensaje):
        """Agrega al log"""
        self.log_text.insert('end', mensaje)
        self.log_text.see('end')
        self.root.update()
    
    def validar_inputs(self):
        """Valida inputs"""
        if not self.api_key.get():
            messagebox.showerror("Error", "Falta API Key")
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
        self.btn_procesar.itemconfig(self.btn_procesar.rect, fill='#4a5568')
        self.btn_procesar.itemconfig(self.btn_procesar.text_id, text='⏳ PROCESANDO...')
        
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
        
        finally:
            self.root.after(0, self.finalizar_procesamiento)
    
    def finalizar_procesamiento(self):
        """Finaliza procesamiento"""
        self.procesando = False
        self.btn_procesar.itemconfig(self.btn_procesar.rect, fill=COLORS['success'])
        self.btn_procesar.itemconfig(self.btn_procesar.text_id, text='🚀  PROCESAR EXTRACTOS')
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


def main():
    root = tk.Tk()
    app = ExtractorModerno(root)
    root.mainloop()


if __name__ == "__main__":
    main()

