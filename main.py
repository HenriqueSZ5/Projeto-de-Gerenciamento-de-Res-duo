from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host="autorack.proxy.rlwy.net",  
            port=18583,                     
            user="root",                     
            password="LRGnqrjbhzlbkvyeWIuZLKzSVpGdgTGN", 
            database="railway"               
        )
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar ao banco de dados: {erro}") 
        return None


@app.route("/")
def index():
    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        username = request.form["username"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        
        if not (username and senha and confirmar_senha):
            flash("Todos os campos devem ser preenchidos!", "warning")
            return redirect(url_for("cadastro"))

        
        if senha != confirmar_senha:
            flash("As senhas não coincidem!", "danger")
            return redirect(url_for("cadastro"))

        
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro ao conectar ao banco de dados.", "danger")
            return redirect(url_for("cadastro"))

        try:
            cursor = conexao.cursor()

            
            cursor.execute("SELECT * FROM tabela_login WHERE username = %s", (username,))
            if cursor.fetchone():
                flash("Usuário já existe! Escolha outro nome.", "warning")
                return redirect(url_for("cadastro"))

           
            query = """
                INSERT INTO tabela_login (username, senha)
                VALUES (%s, %s)
            """
            valores = (username, senha)
            cursor.execute(query, valores)
            conexao.commit()

            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("index"))

        except Exception as e:
            print(f"Erro: {str(e)}")  # Adicione esta linha para debug
            flash(f"Erro ao realizar cadastro: {str(e)}", "danger")
            return redirect(url_for("cadastro"))

        finally:
            cursor.close()
            conexao.close()

  
    return render_template("cadastro.html")



@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    senha = request.form["senha"]

    if not username or not senha:
        flash("Nome de usuário e senha não podem estar vazios.", "warning")
        return redirect(url_for("index"))

    conexao = conectar_banco()
    if conexao is None:
        flash("Erro ao conectar ao banco de dados.", "danger")
        return redirect(url_for("index"))

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tabela_login WHERE username=%s AND senha=%s", (username, senha))
        result = cursor.fetchone()

        if result:
            flash(f"Login bem-sucedido como {username}!", "success")
            return redirect(url_for("dashboard", username=username))
        else:
            flash("Usuário ou senha incorretos.", "warning")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"Erro ao verificar login: {str(e)}", "danger")
        return redirect(url_for("index"))
    finally:
        cursor.close()
        conexao.close()

@app.route("/dashboard/<username>")
def dashboard(username):
    return render_template("dashboard.html", username=username)



@app.route("/add_separacao", methods=["GET", "POST"])
def add_separacao():
    if request.method == "POST":
        tipo = request.form.get("tipo").strip().lower()
        data_separacao = request.form.get("data_separacao")
        kg = request.form.get("kg")

        if not (tipo and data_separacao and kg):
            flash("Todos os campos devem ser preenchidos!", "warning")
            return redirect(url_for("add_separacao"))

        try:
            kg = float(kg)
        except ValueError:
            flash("O campo 'kg' deve ser um número!", "danger")
            return redirect(url_for("add_separacao"))

        tipo_cod_item_map = {
            "aluminio": 1,
            "cobre": 2,
            "aco": 3,
            "ferro": 4
        }
        cod_item = tipo_cod_item_map.get(tipo)

        if cod_item is None:
            flash("Tipo inválido! Use: Aluminio, Cobre, Aço ou Ferro.", "warning")
            return redirect(url_for("add_separacao"))

        conexao = conectar_banco()
        if conexao is None:
            flash("Erro ao conectar ao banco de dados.", "danger")
            return redirect(url_for("add_separacao"))

        try:
            cursor = conexao.cursor()
            query = """
                INSERT INTO tbl_separacao (tipo, data_separacao, kg, cod_item)
                VALUES (%s, %s, %s, %s)
            """
            valores = (tipo.capitalize(), data_separacao, kg, cod_item)
            cursor.execute(query, valores)
            conexao.commit()

            flash("Informações adicionadas com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao adicionar informações: {str(e)}", "danger")
        finally:
            cursor.close()
            conexao.close()

       
        return redirect(url_for("view_separacao"))

    return render_template("add_separacao.html")




@app.route("/view_separacao")
def view_separacao():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro ao conectar ao banco de dados.", "danger")
        return redirect(url_for("dashboard", username="user"))

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tbl_separacao")
        registros = cursor.fetchall()
        return render_template("view_separacao.html", registros=registros)
    except Exception as e:
        flash(f"Erro ao buscar dados: {str(e)}", "danger")
        return redirect(url_for("dashboard", username="user"))
    finally:
        cursor.close()
        conexao.close()


@app.route("/add_coleta", methods=["GET", "POST"])
def add_coleta():
    if request.method == "POST":
       
        data_coleta = request.form.get("data_coleta")
        kg = request.form.get("kg")

      
        if not (data_coleta and kg):
            flash("Todos os campos devem ser preenchidos!", "warning")
            return redirect(url_for("add_coleta"))

        
        try:
            kg = float(kg)
        except ValueError:
            flash("A kg deve ser um número!", "danger")
            return redirect(url_for("add_coleta"))

       
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro ao conectar ao banco de dados.", "danger")
            return redirect(url_for("add_coleta"))

        try:
            
            cursor = conexao.cursor()
            query = """
                INSERT INTO tbl_coleta (data_coleta, kg)
                VALUES (%s, %s)
            """
            valores = (data_coleta, kg)
            cursor.execute(query, valores)
            conexao.commit()

            flash("Informações adicionadas com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao adicionar informações: {str(e)}", "danger")
        finally:
            cursor.close()
            conexao.close()

        return redirect(url_for("view_coleta"))  

   
    return render_template("add_coleta.html")

@app.route("/add_venda", methods=["GET", "POST"])
def add_venda():
    if request.method == "POST":
        tipo = request.form.get("tipo").strip().lower()
        data_venda = request.form.get("data_venda")
        kg = request.form.get("kg")
        valor_total = request.form.get("valor_total")

        # Validações básicas
        if not (tipo and data_venda and kg and valor_total):
            flash("Todos os campos devem ser preenchidos!", "warning")
            return redirect(url_for("add_venda"))

        try:
            kg = float(kg)
            valor_total = float(valor_total)
        except ValueError:
            flash("Os campos 'kg' e 'valor_total' devem ser números!", "danger")
            return redirect(url_for("add_venda"))

        tipo_cod_item_map = {
            "aluminio": 1,
            "cobre": 2,
            "aco": 3,
            "ferro": 4
        }
        cod_item = tipo_cod_item_map.get(tipo)

        if cod_item is None:
            flash("Tipo inválido! Use: Aluminio, Cobre, Aço ou Ferro.", "warning")
            return redirect(url_for("add_venda"))

        conexao = conectar_banco()
        if conexao is None:
            flash("Erro ao conectar ao banco de dados.", "danger")
            return redirect(url_for("add_venda"))

        try:
            cursor = conexao.cursor()
            query = """
                INSERT INTO tbl_venda (tipo, data_venda, kg, valor_total, cod_item)
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (tipo.capitalize(), data_venda, kg, valor_total, cod_item)
            cursor.execute(query, valores)
            conexao.commit()

            flash("Venda adicionada com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao adicionar venda: {str(e)}", "danger")
        finally:
            cursor.close()
            conexao.close()

        # Redireciona para view_venda após sucesso
        return redirect(url_for("view_venda"))

    return render_template("add_venda.html")


@app.route("/view_coleta")
def view_coleta():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro ao conectar ao banco de dados.", "danger")
        return redirect(url_for("dashboard", username="user"))

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tbl_coleta")
        registros = cursor.fetchall()
        return render_template("view_coleta.html", registros=registros)
    except Exception as e:
        flash(f"Erro ao buscar dados: {str(e)}", "danger")
        return redirect(url_for("dashboard", username="user"))
    finally:
        cursor.close()
        conexao.close()


@app.route("/view_venda")
def view_venda():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro ao conectar ao banco de dados.", "danger")
        return redirect(url_for("dashboard", username="user"))

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tbl_venda")
        registros = cursor.fetchall()
        return render_template("view_venda.html", registros=registros)
    except Exception as e:
        flash(f"Erro ao buscar dados: {str(e)}", "danger")
        return redirect(url_for("dashboard", username="user"))
    finally:
        cursor.close()
        conexao.close()


@app.route("/delete_residuo", methods=["GET", "POST"])
def delete_residuo():
    if request.method == "POST":
        tipo = request.form["tipo"]
        data = request.form["data"]
        quantidade = request.form["quantidade"]

        if not (tipo and data and quantidade):
            flash("Todos os campos devem ser preenchidos!", "warning")
            return redirect(url_for("delete_residuo"))

        try:
            quantidade = float(quantidade)  
        except ValueError:
            flash("A quantidade deve ser um número!", "danger")
            return redirect(url_for("delete_residuo"))

        conexao = conectar_banco()
        if conexao is None:
            flash("Erro ao conectar ao banco de dados.", "danger")
            return redirect(url_for("delete_residuo"))

        try:
            cursor = conexao.cursor()
            query = """
                DELETE FROM tbl_separacao
                WHERE tipo = %s AND data_separacao = %s AND kg = %s
            """
            valores = (tipo, data, quantidade)
            cursor.execute(query, valores)
            conexao.commit()

            if cursor.rowcount > 0:
                flash("Resíduo removido com sucesso!", "success")
            else:
                flash("Nenhum resíduo encontrado com os critérios informados.", "info")
        except Exception as e:
            flash(f"Erro ao remover resíduo: {str(e)}", "danger")
        finally:
            cursor.close()
            conexao.close()
        return redirect(url_for("dashboard", username="user"))

    return render_template("delete_residuo.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use a porta definida pelo Render ou 5000 como fallback
    app.run(host="0.0.0.0", port=port)
