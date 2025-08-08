import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database.connection import get_connection
from ui.main_window import MainApp

class LoginWindow:
    def __init__(self, root):
        try:
            self.root = root
            self.root.configure(bg="#2A5C8A")  # Fondo azul oscuro para la ventana principal
            self.root.geometry("400x300")  # Tamaño de la ventana principal (opcional)
            self.create_login_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar la ventana de login: {e}")

    def create_login_window(self):
        try:
            # Crear un marco de recuadro con borde para el login
            self.login_frame = tk.Frame(self.root, bg="#1E4D6B", padx=20, pady=20, bd=2, relief="groove")
            self.login_frame.place(relx=0.5, rely=0.5, anchor="center")  # Centrar el cuadro de login

            # Crear widgets de login en el cuadro
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la ventana de login: {e}")

    def create_widgets(self):
        try:
            # Título
            title_label = tk.Label(self.login_frame, text="Bienvenido", font=("Helvetica", 18, "bold"), 
                                   fg="white", bg="#1E4D6B")
            title_label.pack(pady=(0, 20))

            # Campo de Usuario
            username_label = tk.Label(self.login_frame, text="Usuario:", font=("Helvetica", 10), 
                                      fg="white", bg="#1E4D6B")
            username_label.pack(anchor="w")
            self.username_entry = ttk.Entry(self.login_frame, font=("Helvetica", 12))
            self.username_entry.pack(fill="x", pady=(0, 10))

            # Campo de Contraseña
            password_label = tk.Label(self.login_frame, text="Contraseña:", font=("Helvetica", 10), 
                                      fg="white", bg="#1E4D6B")
            password_label.pack(anchor="w")
            self.password_entry = ttk.Entry(self.login_frame, show="*", font=("Helvetica", 12))
            self.password_entry.pack(fill="x", pady=(0, 20))

            # Botón de Login
            login_button = tk.Button(self.login_frame, text="Login", command=self.attempt_login, 
                                     font=("Helvetica", 12), bg="#4C90C3", fg="white", bd=0, padx=10, pady=5)
            login_button.pack(fill="x", pady=(0, 10))

            # Texto para recuperar contraseña y registrarse
            lost_password_label = tk.Label(self.login_frame, text="¿Perdiste tu contraseña?", font=("Helvetica", 10), 
                                           fg="white", bg="#1E4D6B", cursor="hand2")
            lost_password_label.pack()
            lost_password_label.bind("<Button-1>", lambda e: self.admin_message())
            
            register_label = tk.Label(self.login_frame, text="¿No tienes Cuenta? Regístrate", font=("Helvetica", 10), 
                                      fg="white", bg="#1E4D6B", cursor="hand2")
            register_label.pack(pady=(0, 20))
            register_label.bind("<Button-1>", lambda e: self.admin_message())
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear los widgets de la ventana de login: {e}")

    def toggle_password(self):
        try:
            if self.password_entry.cget('show') == '*':
                self.password_entry.config(show='')
            else:
                self.password_entry.config(show='*')
        except Exception as e:
            messagebox.showerror("Error", f"Error al alternar la visibilidad de la contraseña: {e}")

    def attempt_login(self):
        try:
            username = self.username_entry.get()
            password = self.password_entry.get()
            role = self.verify_credentials(username, password)
            if role:
                MainApp(self.root, role)
            else:
                messagebox.showerror("Inicio de Sesión Fallido", "Usuario o contraseña incorrecta.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al intentar iniciar sesión: {e}")

    def admin_message(self):
        try:
            messagebox.showinfo("Info", "Comunícate con el administrador, únicamente este puede agregar o editar un usuario.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el mensaje del administrador: {e}")
    
    @staticmethod
    def hash_password(password):
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el hash de la contraseña: {e}")

    @staticmethod
    def verify_credentials(username, password):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            hashed_password = LoginWindow.hash_password(password)
            cursor.execute("SELECT role FROM CS_USERS WHERE username = :username AND password_hash = :password_hash",
                           {"username": username, "password_hash": hashed_password})
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar las credenciales: {e}")
            return None
