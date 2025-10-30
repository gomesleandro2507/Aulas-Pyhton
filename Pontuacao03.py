import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Configuração do banco MySQL
DB_CONFIG = {
    "host": "localhost",      
    "user": "root",           
    "password": "sua_senha",  
    "database": "vendas_db"   
}

# Função para conectar ao banco
def conectar():
    return mysql.connector.connect(**DB_CONFIG)

# Validação de data
def validar_data(data_texto):
    try:
        datetime.strptime(data_texto, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Salvar dados no banco
def salvar_dados(usuario):
    data = entry_data.get()
    if not validar_data(data):
        messagebox.showerror("Erro", "Data inválida. Use AAAA-MM-DD.")
        return

    try:
        venda = int(entry_venda.get())
        venda_cadastro = int(entry_venda_cadastro.get())
        cadastros = int(entry_cadastros.get())
        conversoes = int(entry_conversoes.get())
        conversao_cadastro = int(entry_conversao_cadastro.get())
        declaracoes = int(entry_declaracoes.get())
    except ValueError:
        messagebox.showerror("Erro", "Todos os campos devem conter números inteiros.")
        return

    pontos = venda_cadastro * 4 + cadastros * 2 + conversoes * 2 + conversao_cadastro * 7 + declaracoes * 2

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vendas (usuario, data, venda, venda_cadastro, cadastros, conversoes, conversao_cadastro, declaracoes, pontos)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (usuario, data, venda, venda_cadastro, cadastros, conversoes, conversao_cadastro, declaracoes, pontos))
    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", f"Registro salvo com {pontos} pontos!")
    limpar_campos()

# Limpar campos
def limpar_campos():
    for entrada in entries:
        entrada.delete(0, tk.END)

# Gerar gráfico
def gerar_grafico(usuario):
    conn = conectar()
    query = "SELECT data, pontos FROM vendas WHERE usuario = %s ORDER BY data"
    df = pd.read_sql(query, conn, params=(usuario,))
    conn.close()

    if df.empty:
        messagebox.showerror("Erro", "Usuário sem registros.")
        return

    df["data"] = pd.to_datetime(df["data"])
    plt.figure(figsize=(8, 5))
    plt.plot(df["data"], df["pontos"], marker="o", color="blue")
    plt.title(f"Desempenho de {usuario}")
    plt.xlabel("Data")
    plt.ylabel("Pontuação")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Cadastro de usuário
def cadastrar_usuario():
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    if usuario.strip() == "" or senha.strip() == "":
        messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM usuarios WHERE usuario = %s", (usuario,))
    if cursor.fetchone():
        messagebox.showerror("Erro", "Usuário já cadastrado.")
        conn.close()
        return

    cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", (usuario, senha))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")

# Login
def fazer_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM usuarios WHERE usuario = %s AND senha = %s", (usuario, senha))
    if cursor.fetchone():
        conn.close()
        janela_login.destroy()
        abrir_interface(usuario)
    else:
        conn.close()
        messagebox.showerror("Erro", "Usuário ou senha inválidos.")

# Interface principal
def abrir_interface(usuario):
    global janela, entries, entry_data, entry_venda, entry_venda_cadastro, entry_cadastros, entry_conversoes, entry_conversao_cadastro, entry_declaracoes

    janela = tk.Tk()
    janela.title(f"Controle de Vendas - Usuário: {usuario}")

    labels = [
        ("Data (AAAA-MM-DD):", 0),
        ("Cartões vendidos:", 1),
        ("Vendas com cadastro:", 2),
        ("Cadastros (sem venda):", 3),
        ("Conversões (sem cadastro):", 4),
        ("Conversões com cadastro:", 5),
        ("Declarações de renda:", 6)
    ]

    entries = []
    for texto, linha in labels:
        tk.Label(janela, text=texto).grid(row=linha, column=0, sticky="e")
        entrada = tk.Entry(janela)
        entrada.grid(row=linha, column=1)
        entries.append(entrada)

    entry_data, entry_venda, entry_venda_cadastro, entry_cadastros, entry_conversoes, entry_conversao_cadastro, entry_declaracoes = entries

    tk.Button(janela, text="Salvar Registro", command=lambda: salvar_dados(usuario)).grid(row=7, column=0, columnspan=2, pady=10)
    tk.Button(janela, text="Ver Gráfico", command=lambda: gerar_grafico(usuario)).grid(row=8, column=0, columnspan=2, pady=10)

    janela.mainloop()

# Tela de login
janela_login = tk.Tk()
janela_login.title("Login")

tk.Label(janela_login, text="Usuário:").grid(row=0, column=0)
entry_usuario = tk.Entry(janela_login)
entry_usuario.grid(row=0, column=1)

tk.Label(janela_login, text="Senha:").grid(row=1, column=0)
entry_senha = tk.Entry(janela_login, show="*")
entry_senha.grid(row=1, column=1)

tk.Button(janela_login, text="Entrar", command=fazer_login).grid(row=2, column=0, pady=10)
tk.Button(janela_login, text="Cadastrar", command=cadastrar_usuario).grid(row=2, column=1, pady=10)

janela_login.mainloop()
