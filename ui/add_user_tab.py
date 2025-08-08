import cx_Oracle
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database.connection import get_connection


class AddUserWindow:
    def __init__(self, root):
        self.root = root
        self.create_window()

    def create_window(self):
        # Configuración de la ventana principal
        self.window = Toplevel(self.root)
        self.window.title("Administrar Usuario")
        self.window.geometry("400x500")
        self.window.configure(bg="#2A5C8A")  # Fondo azul oscuro

        # Marco de recuadro con estilo
        self.frame = tk.Frame(self.window, bg="#1E4D6B", padx=20, pady=20, bd=2, relief="groove")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")  # Centrado del marco

        # Crear los widgets dentro del marco
        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = tk.Label(self.frame, text="Administrar Usuario", font=("Helvetica", 18, "bold"),
                               fg="white", bg="#1E4D6B")
        title_label.pack(pady=(0, 20))

        # Campos de entrada
        self.add_label_and_entry("Nuevo Usuario:", "username")
        self.add_label_and_entry("Contraseña:", "password", show="*")
        self.add_label_and_entry("Repetir Contraseña:", "confirm_password", show="*")

        # Combobox para el rol
        role_label = tk.Label(self.frame, text="Rol:", font=("Helvetica", 12), fg="white", bg="#1E4D6B")
        role_label.pack(anchor="w", pady=(10, 0))
        self.role_combobox = ttk.Combobox(self.frame, values=["admin", "usuario"], state="readonly", font=("Helvetica", 12))
        self.role_combobox.pack(fill="x", pady=(0, 20))

        # Botón para guardar usuario
        save_button = tk.Button(self.frame, text="Guardar Usuario", command=self.add_user,
                                font=("Helvetica", 12), bg="#4C90C3", fg="white", bd=0, padx=10, pady=5)
        save_button.pack(fill="x", pady=(0, 10))

        # Botón para cambiar contraseña
        change_password_button = tk.Button(self.frame, text="Cambiar Contraseña", command=self.change_password,
                                           font=("Helvetica", 12), bg="#4C90C3", fg="white", bd=0, padx=10, pady=5)
        change_password_button.pack(fill="x", pady=(0, 10))

    def add_label_and_entry(self, label_text, var_name, **kwargs):
        """Añade un label y un campo de entrada al marco."""
        label = tk.Label(self.frame, text=label_text, font=("Helvetica", 12), fg="white", bg="#1E4D6B")
        label.pack(anchor="w", pady=(10, 0))
        entry = ttk.Entry(self.frame, font=("Helvetica", 12), **kwargs)
        entry.pack(fill="x", pady=(0, 10))
        setattr(self, f"{var_name}_entry", entry)

    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        role = self.role_combobox.get().strip()

        if not username or not password or not confirm_password or not role:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        if password != confirm_password:
            messagebox.showwarning("Advertencia", "Las contraseñas no coinciden.")
            return

        hashed_password = self.hash_password(password)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CS_USERS (username, password_hash, role) VALUES (:username, :password_hash, :role)",
                {"username": username, "password_hash": hashed_password, "role": role}
            )
            conn.commit()
            messagebox.showinfo("Éxito", f"Usuario {username} agregado correctamente.")
            self.window.destroy()
        except cx_Oracle.IntegrityError:
            messagebox.showerror("Error", f"El usuario '{username}' ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar el usuario: {e}")
        finally:
            if conn:
                conn.close()

    def change_password(self):
        username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()
        confirm_new_password = self.confirm_password_entry.get().strip()

        if not username or not new_password or not confirm_new_password:
            messagebox.showwarning("Advertencia", "Usuario y contraseñas son obligatorios para cambiar la contraseña.")
            return

        if new_password != confirm_new_password:
            messagebox.showwarning("Advertencia", "Las contraseñas no coinciden.")
            return

        hashed_password = self.hash_password(new_password)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE CS_USERS SET password_hash = :password_hash WHERE username = :username",
                {"password_hash": hashed_password, "username": username}
            )
            if cursor.rowcount == 0:
                messagebox.showwarning("Advertencia", f"No se encontró el usuario '{username}'.")
            else:
                conn.commit()
                messagebox.showinfo("Éxito", f"Contraseña del usuario '{username}' actualizada correctamente.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cambiar la contraseña: {e}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
