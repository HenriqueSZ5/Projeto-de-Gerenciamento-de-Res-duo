import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

def conectar_banco():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="db_coleta"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {str(err)}")
        return None

def login():
    username = entry_username.get().strip()
    senha = entry_senha.get().strip()

    if not (username and senha):
        messagebox.showwarning("Aviso", "Nome de usuário e senha não podem estar vazios.")
        return

    conexao = conectar_banco()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tabela_login WHERE username=%s AND senha=%s", (username, senha))
        result = cursor.fetchone()

        if result:
            messagebox.showinfo("Sucesso", f"Login bem-sucedido como {username}!")
            root.destroy()
            open_main_window(username)
        else:
            messagebox.showwarning("Aviso", "Usuário ou senha incorretos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao verificar login: {str(e)}")
    finally:
        cursor.close()
        conexao.close()

    def add_employee():
        new_username = entry_new_username.get().strip()
        new_password = entry_new_password.get().strip()

        if not (new_username and new_password):
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
            return

        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            sql = "INSERT INTO tabela_login (username, senha) VALUES (%s, %s)"
            cursor.execute(sql, (new_username, new_password))
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Funcionário {new_username} registrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar funcionário: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

        entry_new_username.delete(0, tk.END)
        entry_new_password.delete(0, tk.END)

    label_style = {
        "bg": "#a2d5ab",
        "fg": "#333333",
        "font": ("Helvetica", 10, "bold")
    }

    tk.Label(third_window, text="Nome de Usuário:", **label_style).grid(row=0, column=0, pady=5, padx=10, sticky="e")
    entry_new_username = tk.Entry(third_window, font=("Helvetica", 10))
    entry_new_username.grid(row=0, column=1, pady=5, padx=10, sticky="w")

    tk.Label(third_window, text="Senha:", **label_style).grid(row=1, column=0, pady=5, padx=10, sticky="e")
    entry_new_password = tk.Entry(third_window, font=("Helvetica", 10), show='*')
    entry_new_password.grid(row=1, column=1, pady=5, padx=10, sticky="w")

    ttk.Button(third_window, text="Adicionar Funcionário", command=add_employee).grid(row=3, column=0, columnspan=2, pady=10)

    ttk.Button(third_window, text="Visualizar Usuários", command=view_users).grid(row=4, column=0, columnspan=2, pady=5)
    ttk.Button(third_window, text="Deletar Usuário", command=delete_user).grid(row=6, column=0, columnspan=2, pady=5)

    tk.Label(third_window, text="Deletar Usuário:", **label_style).grid(row=5, column=0, pady=5, padx=10, sticky="e")
    entry_delete_username = tk.Entry(third_window, font=("Helvetica", 10))
    entry_delete_username.grid(row=5, column=1, pady=5, padx=10, sticky="w")

    ttk.Button(third_window, text="Voltar", command=third_window.destroy).grid(row=7, column=0, pady=10)
    ttk.Button(third_window, text="Sair", command=third_window.quit).grid(row=7, column=1, pady=10)

    third_window.grid_columnconfigure(0, weight=1)
    third_window.grid_columnconfigure(1, weight=1)

    third_window.grid_columnconfigure(0, weight=1)
    third_window.grid_columnconfigure(1, weight=1)
    
def open_main_window(username):
    main_window = tk.Tk()
    main_window.title("Coletin")
    main_window.geometry("600x400")
    main_window.configure(bg="#91bd8f")

    def view_data():
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM tbl_separacao")
            registros = cursor.fetchall()

            dados = "\n".join([f"ID: {row[0]}, Data de Separação: {row[1]}, Codigo do Item: {row[2]}, Tipo: {row[3]}, Kg: {row[4]}" for row in registros])
            if dados:
                messagebox.showinfo("Dados", dados)
            else:
                messagebox.showinfo("Dados", "Nenhum dado encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton",
                    background="#30833f",
                    foreground="white",
                    font=("Helvetica", 10, "bold"),
                    padding=5)

    ttk.Button(main_window, text="Estoque de Resíduos", command=view_data).grid(row=1, column=0, columnspan=2, pady=5)
    """ttk.Button(main_window, text="Banco de Coleta", command=insert_data1).grid(row=8, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Sepação de Resíduo", command=insert_data2).grid(row=2, column=0, columnspan=2, pady=5)
    
    ttk.Button(main_window, text="Remover Resíduo", command=delete_data).grid(row=4, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Venda de Resíduo", command=insert_data3).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Button(main_window, text="Sair", command=main_window.quit).grid(row=6, column=0, columnspan=2, pady=5)"""

    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_columnconfigure(1, weight=1)

    main_window.mainloop()

root = tk.Tk()
root.title("Login")
root.geometry("400x300")
root.configure(bg="#91bd8f")

label_style = {
    "bg": "#a2d5ab",
    "fg": "#333333",
    "font": ("Helvetica", 10, "bold")
}

tk.Label(root, text="Nome de Usuário:", **label_style).grid(row=0, column=0, pady=20, padx=20, sticky="e")
entry_username = tk.Entry(root, font=("Helvetica", 10))
entry_username.grid(row=0, column=1, pady=10, padx=20, sticky="w")

tk.Label(root, text="Senha:", **label_style).grid(row=1, column=0, pady=20, padx=20, sticky="e")
entry_senha = tk.Entry(root, font=("Helvetica", 10), show='*')
entry_senha.grid(row=1, column=1, pady=10, padx=20, sticky="w")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                background="#30833f",
                foreground="white",
                font=("Helvetica", 10, "bold"),
                padding=5)
style.map("TButton",
        background=[("active", "#45a049")],
        foreground=[("active", "white")])

btn_login = ttk.Button(root, text="Entrar", command=login)
btn_login.grid(row=2, column=0, columnspan=2, pady=20)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()