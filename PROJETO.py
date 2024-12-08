import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
def formatar_data(data_iso):
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_iso
    
def conectar_banco():
    try:
        return mysql.connector.connect(
            host="localhost",
            port= "3306",
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
    
def open_main_window(username):
    main_window = tk.Tk()
    main_window.title("Coletin")
    main_window.geometry("600x400")
    main_window.configure(bg="#91bd8f")

    def update_capacity_chart():
 
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT SUM(quantidade) FROM tb_crioprotetores")
            total = cursor.fetchone()[0] or 0

            cursor.close()
            conexao.close()

            ocupado = min(total, 1000)
            livre = max(0, 1000 - ocupado)

            ax.clear()
            ax.pie(
                [ocupado, livre],
                labels=["Ocupado", "Disponível"],
                autopct='%1.1f%%',
                colors=["#ff9999", "#99ff99"],
                startangle=90,
            )
            ax.set_title("Capacidade do Biodigestor (Máx: 1000)")
            canvas.draw()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {str(e)}")
    
    def insert_data():
    
        crioprotetores = entry_crioprotetor.get().strip().lower()
        temperatura = entry_temperatura.get().strip().capitalize()
        quantidade = entry_quantidade.get()

        if not (crioprotetores and temperatura and quantidade.isdigit()):
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos corretamente.")
            return

        quantidade = int(quantidade)
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT SUM(quantidade) FROM tb_crioprotetores")
            total_atual = cursor.fetchone()[0] or 0

            if total_atual + quantidade > 1000:
                messagebox.showwarning("Aviso", "A quantidade excederia o limite máximo de 1000 unidades no biodigestor.")
                return

            sql = "INSERT INTO tb_crioprotetores (crioprotetores, temperatura, quantidade, usuario_id) VALUES (%s, %s, %s, (SELECT id FROM tb_usuarios WHERE username = %s))"
            valores = (crioprotetores, temperatura, quantidade, username)
            cursor.execute(sql, valores)
            conexao.commit()
            messagebox.showinfo("Sucesso", "Dados inseridos com sucesso!")

            update_capacity_chart()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inserir dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

        clear_entries()

    def delete_data():
        crioprotetores = entry_crioprotetor.get().strip().lower()

        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            sql = "DELETE FROM tb_crioprotetores WHERE crioprotetores = %s"
            valores = (crioprotetores,)
            cursor.execute(sql, valores)
            conexao.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Sucesso", f"Dados deletados com sucesso para {crioprotetores}")
            else:
                messagebox.showwarning("Aviso", f"Nenhum crioprotetor encontrado com o nome {crioprotetores}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

        clear_entries()

    def view_data():
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM tbl_separacao")
            registros = cursor.fetchall()

            dados = "\n".join([
    f"ID: {row[0]}, Data de Separação: {formatar_data(row[1])}, Codigo do Item: {row[2]}, Tipo: {row[3]}, Kg: {row[4]}"
    for row in registros])
            if dados:
                messagebox.showinfo("Dados", dados)
            else:
                messagebox.showinfo("Dados", "Nenhum dado encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

    def insert_data1():
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM tbl_coleta")
            registros = cursor.fetchall()


            dados = "\n".join([f"ID: {row[0]}, Data de Coleta: {formatar_data(row[1])}, Quantidade de Caçamba: {row[2]}, Kg de Resíduos Coletos: {row[3]}"
    for row in registros])
            if dados:
                messagebox.showinfo("Dados", dados)
            else:
                messagebox.showinfo("Dados", "Nenhum dado encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

    ttk.Button(main_window, text="Atualizar Gráfico", command=update_capacity_chart).grid(row=8, column=2, pady=5)
    tk.Label(main_window, text="Crioprotetor:", bg="#a2d5ab", font=("Helvetica", 10, "bold")).grid(row=0, column=0, pady=5, padx=10, sticky="e")
    entry_crioprotetor = tk.Entry(main_window, font=("Helvetica", 10))
    entry_crioprotetor.grid(row=0, column=1, pady=5, padx=10, sticky="w")


    def insert_data2():
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM tbl_separacao")
            registros = cursor.fetchall()

            dados = "\n".join([f"ID: {row[0]}, Data de Separação: {formatar_data(row[1])}, Código do Item: {row[2]}, Tipo do Resíduo: {row[3]}, Kg: {row[4]}"
            for row in registros])
            if dados:
                messagebox.showinfo("Dados", dados)
            else:
                messagebox.showinfo("Dados", "Nenhum dado encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

    def insert_data3():
        conexao = conectar_banco()
        if conexao is None:
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM tbl_venda")
            registros = cursor.fetchall()

            dados = "\n".join([
            f"ID: {row[0]}, Data da Venda: {formatar_data(row[1])}, Código do Item: {row[2]}, Tipo do Resíduo: {row[3]}, Kg: {row[4]}"
            for row in registros])
            if dados:
                messagebox.showinfo("Dados", dados)
            else:
                messagebox.showinfo("Dados", "Nenhum dado encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {str(e)}")
        finally:
            cursor.close()
            conexao.close()

    def delete_data():
        def confirmar_remocao():
        
            nome = entry_nome.get()
            data = entry_data.get()
            quantidade = entry_quantidade.get()

            if not nome or not data or not quantidade:
                messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
                return

            try:
                quantidade = float(quantidade)  
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número!")
                return

            conexao = conectar_banco()
            if conexao is None:
                return

            try:
                cursor = conexao.cursor()
                query = """
                DELETE FROM tbl_separacao
                WHERE tipo = %s AND data_separacao = %s AND kg = %s
                """
                valores = (nome, data, quantidade)
                cursor.execute(query, valores)
                conexao.commit()

                if cursor.rowcount > 0:
                    messagebox.showinfo("Sucesso", "Resíduo removido com sucesso!")
                else:
                    messagebox.showinfo("Aviso", "Nenhum resíduo encontrado com os critérios informados.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover resíduo: {str(e)}")
            finally:
                cursor.close()
                conexao.close()
                janela_remocao.destroy()  

    
    janela_remocao = tk.Toplevel(main_window)
    janela_remocao.title("Remover Resíduo")

    ttk.Label(janela_remocao, text="Nome do Resíduo:").grid(row=0, column=0, pady=5, padx=5, sticky="e")
    entry_nome = ttk.Entry(janela_remocao)
    entry_nome.grid(row=0, column=1, pady=5, padx=5)

    ttk.Label(janela_remocao, text="Data da Separação (YYYY-MM-DD):").grid(row=1, column=0, pady=5, padx=5, sticky="e")
    entry_data = ttk.Entry(janela_remocao)
    entry_data.grid(row=1, column=1, pady=5, padx=5)


    ttk.Label(janela_remocao, text="Quantidade (kg):").grid(row=2, column=0, pady=5, padx=5, sticky="e")
    entry_quantidade = ttk.Entry(janela_remocao)
    entry_quantidade.grid(row=2, column=1, pady=5, padx=5)

    ttk.Button(janela_remocao, text="Confirmar", command=confirmar_remocao).grid(row=3, column=0, columnspan=2, pady=10)
        

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton",
                    background="#4c3254",
                    foreground="white",
                    font=("Times New Roman", 12, "bold"),
                    padding=5)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton",
                    background="#4c3254",
                    foreground="white",
                    font=("Times New Roman", 12, "bold"),
                    padding=5)
    

    ttk.Button(main_window, text="Estoque de Resíduos", command=view_data).grid(row=1, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Banco de Coleta", command=insert_data1).grid(row=2, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Sepação de Resíduo", command=insert_data2).grid(row=3, column=0, columnspan=2, pady=5)
    
    ttk.Button(main_window, text="Remover Resíduo", command=delete_data).grid(row=4, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Venda de Resíduo", command=insert_data3).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Button(main_window, text="Sair", command=main_window.quit).grid(row=6, column=0, columnspan=2, pady=5)

    tk.Label(main_window, text="Crioprotetor:", bg="#a2d5ab", font=("Helvetica", 10, "bold")).grid(row=0, column=0, pady=5, padx=10, sticky="e")
    entry_crioprotetor = tk.Entry(main_window, font=("Helvetica", 10))
    entry_crioprotetor.grid(row=0, column=1, pady=5, padx=10, sticky="w")

    tk.Label(main_window, text="Temperatura:", bg="#a2d5ab", font=("Helvetica", 10, "bold")).grid(row=1, column=0, pady=5, padx=10, sticky="e")
    entry_temperatura = tk.Entry(main_window, font=("Helvetica", 10))
    entry_temperatura.grid(row=1, column=1, pady=5, padx=10, sticky="w")

    tk.Label(main_window, text="Quantidade:", bg="#a2d5ab", font=("Helvetica", 10, "bold")).grid(row=2, column=0, pady=5, padx=10, sticky="e")
    entry_quantidade = tk.Entry(main_window, font=("Helvetica", 10))
    entry_quantidade.grid(row=2, column=1, pady=5, padx=10, sticky="w")

    ttk.Button(main_window, text="Adicionar bactéria", command=insert_data).grid(row=3, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Visualizar Status", command=view_data).grid(row=5, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Remover bactéria", command=delete_data).grid(row=4, column=0, columnspan=2, pady=5)
    if role == 'admin':
        ttk.Button(main_window, text="Registro", command=open_third_window).grid(row=6, column=0, columnspan=2, pady=5)
    ttk.Button(main_window, text="Sair", command=main_window.quit).grid(row=7, column=0, columnspan=2, pady=5)

    
    fig = Figure(figsize=(3, 3), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, main_window)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=8, padx=20, pady=10)

    
    ttk.Button(main_window, text="Atualizar Gráfico", command=update_capacity_chart).grid(row=8, column=2, pady=5)

  
    update_capacity_chart()


    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_columnconfigure(1, weight=1)
    main_window.grid_columnconfigure(2, weight=1)

    main_window.mainloop()

root = tk.Tk()
root.title("Login")
root.geometry("400x300")
root.configure(bg="#91bd8f")

label_style = {
    "bg": "#c8a1ff",
    "fg": "#000000",
    "font": ("Times New Roman", 12, "bold")
}

tk.Label(root, text="Nome de Usuário:", **label_style).grid(row=0, column=0, pady=20, padx=20, sticky="e")
entry_username = tk.Entry(root, font=("Times New Roman", 12))
entry_username.grid(row=0, column=1, pady=10, padx=20, sticky="w")

tk.Label(root, text="Senha:", **label_style).grid(row=1, column=0, pady=20, padx=20, sticky="e")
entry_senha = tk.Entry(root, font=("Times New Roman", 12), show='*')
entry_senha.grid(row=1, column=1, pady=10, padx=20, sticky="w")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                background="#4c3254",
                foreground="white",
                font=("Times New Roman", 12, "bold"),
                padding=5)
style.map("TButton",
        background=[("active", "#4c3254")],
        foreground=[("active", "white")])

btn_login = ttk.Button(root, text="Entrar", command=login)
btn_login.grid(row=2, column=0, columnspan=2, pady=20)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()