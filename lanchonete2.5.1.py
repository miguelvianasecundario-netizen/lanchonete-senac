import sqlite3

import os

import customtkinter as ctk

from tkinter import messagebox

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("blue")

# ==================================================

# BANCO DE DADOS

# ==================================================

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

caminho_banco = os.path.join(diretorio_atual, "sistema.db")

conexao = sqlite3.connect(caminho_banco)

cursor = conexao.cursor()

cursor.execute("""

    CREATE TABLE IF NOT EXISTS produtos (

        nome TEXT,

        preco REAL,

        quantidade INTEGER

    )

""")


conexao.commit()
# ==================================================

# CADASTRAR PRODUTO

# ==================================================

def limpar_campos():
    entry_nome.delete(0, "end")
    entry_preco.delete(0, "end")
    entry_quantidade.delete(0, "end")


def cadastrar_produto():

    nome = entry_nome.get()

    preco = entry_preco.get()

    quantidade = entry_quantidade.get()

    if nome == "" or preco == "" or quantidade == "":

        messagebox.showwarning(

            "Aviso",

            "Preencha todos os campos!"

        )

        return

    try:

        preco = float(preco)

        quantidade = int(quantidade)

        cursor.execute(

            "INSERT INTO produtos VALUES (?, ?, ?)",

            (nome, preco, quantidade)

        )

        conexao.commit()

        messagebox.showinfo(

            "Sucesso",

            f"Produto '{nome}' cadastrado!"

        )

        entry_nome.delete(0, "end")

        entry_preco.delete(0, "end")

        entry_quantidade.delete(0, "end")

        atualizar_lista_produtos()

    except ValueError:

        messagebox.showerror(

            "Erro",

            "Preço e quantidade devem ser números!"

        )

# ==================================================

# CONSULTAR PRODUTOS

# ==================================================

def atualizar_lista_produtos():

    caixa_resultados.configure(state="normal")

    caixa_resultados.delete("1.0", "end")

    cursor.execute("SELECT * FROM produtos")

    itens = cursor.fetchall()

    caixa_resultados._textbox.tag_configure(

        "estoque_baixo",

        foreground="red"

    )

    if not itens:

        caixa_resultados.insert(

            "end",

            "Nenhum produto cadastrado."

        )

    else:

        for linha in itens:

            texto = (

                f"Produto: {linha[0]}\n"

                f"Preço: R$ {linha[1]:.2f}\n"

                f"Quantidade: {linha[2]}\n"

                f"------------------------------\n"

            )

            if linha[2] <= 5:

                caixa_resultados.insert(

                    "end",

                    texto,

                    "estoque_baixo"

                )

            else:

                caixa_resultados.insert(

                    "end",

                    texto

                )

    caixa_resultados.configure(state="disabled")

# ==================================================

# VENDER PRODUTO

# ==================================================

def vender_produto():

    nome_produto = entry_venda.get()

    if nome_produto == "":

        messagebox.showwarning(

            "Aviso",

            "Digite o nome do produto!"

        )

        return

    cursor.execute(

        "SELECT quantidade FROM produtos WHERE nome = ?",

        (nome_produto,)

    )

    resultado = cursor.fetchone()

    if resultado is None:

        messagebox.showwarning(

            "Aviso",

            "Produto não encontrado!"

        )

        return

    qtd_atual = resultado[0]

    if qtd_atual > 0:

        nova_qtd = qtd_atual - 1

        cursor.execute(

            "UPDATE produtos SET quantidade = ? WHERE nome = ?",

            (nova_qtd, nome_produto)

        )

        conexao.commit()

        atualizar_lista_produtos()

        messagebox.showinfo(

            "Venda",

            f"Venda realizada!\n\n"

            f"Produto: {nome_produto}\n"

            f"Estoque anterior: {qtd_atual}\n"

            f"Estoque atual: {nova_qtd}"

        )

        entry_venda.delete(0, "end")

    else:

        messagebox.showwarning(

            "Aviso",

            "Produto Esgotado!"

        )

# ==================================================

# MOSTRAR CADASTRO

# ==================================================

def mostrar_cadastro():

    frame_cadastro.pack(

        fill="both",

        expand=True,

        padx=20,

        pady=20

    )

    frame_consulta.pack_forget()

    frame_venda.pack_forget()

# ==================================================

# MOSTRAR CONSULTA

# ==================================================

def mostrar_consulta():

    frame_cadastro.pack_forget()

    frame_venda.pack_forget()

    frame_consulta.pack(

        fill="both",

        expand=True,

        padx=20,

        pady=20

    )

    atualizar_lista_produtos()

# ==================================================

# MOSTRAR VENDA

# ==================================================

def mostrar_venda():

    frame_cadastro.pack_forget()

    frame_consulta.pack_forget()

    frame_venda.pack(

        fill="both",

        expand=True,

        padx=20,

        pady=20

    )

# ==================================================

# ABRIR SISTEMA PRINCIPAL

# ==================================================

def abrir_sistema_principal():

    global janela

    global frame_cadastro

    global frame_consulta

    global frame_venda

    global entry_nome

    global entry_preco

    global entry_quantidade

    global entry_venda

    global caixa_resultados

    janela_login.destroy()

    janela = ctk.CTk()

    janela.geometry("900x600")

    janela.title(

        "Lanchonete Ennius Muniz - Senac DF"

    )

    # ==================================================

    # MENU LATERAL

    # ==================================================

    frame_menu = ctk.CTkFrame(

        janela,

        width=200

    )

    frame_menu.pack(

        side="left",

        fill="y",

        padx=10,

        pady=10

    )

    titulo = ctk.CTkLabel(

        frame_menu,

        text="Lanchonete\nEnnius Muniz",

        font=(

            "Arial",

            20,

            "bold"

        )

    )

    titulo.pack(

        pady=30

    )

    botao_cadastro = ctk.CTkButton(

        frame_menu,

        text="Cadastrar Produto",

        command=mostrar_cadastro

    )

    botao_cadastro.pack(

        pady=10,

        padx=20

    )

    botao_consulta = ctk.CTkButton(

        frame_menu,

        text="Consultar Produtos",

        command=mostrar_consulta

    )

    botao_consulta.pack(

        pady=10,

        padx=20

    )

    botao_venda = ctk.CTkButton(

        frame_menu,

        text="Realizar Venda",

        command=mostrar_venda

    )

    botao_venda.pack(

        pady=10,

        padx=20

    )

    botao_sair = ctk.CTkButton(

        frame_menu,

        text="Sair",

        command=janela.destroy

    )

    botao_sair.pack(

        pady=30,

        padx=20

    )

    # ==================================================

    # FRAME CADASTRO

    # ==================================================

    frame_cadastro = ctk.CTkFrame(

        janela

    )

    titulo_cadastro = ctk.CTkLabel(

        frame_cadastro,

        text="Cadastro de Produtos",

        font=(

            "Arial",

            24,

            "bold"

        )

    )

    titulo_cadastro.pack(

        pady=30

    )

    entry_nome = ctk.CTkEntry(

        frame_cadastro,

        width=350,

        placeholder_text="Nome do produto"

    )

    entry_nome.pack(

        pady=10

    )

    entry_preco = ctk.CTkEntry(

        frame_cadastro,

        width=350,

        placeholder_text="Preço"

    )

    entry_preco.pack(

        pady=10

    )

    entry_quantidade = ctk.CTkEntry(

        frame_cadastro,

        width=350,

        placeholder_text="Quantidade"

    )

    entry_quantidade.pack(

        pady=10

    )

    botao_salvar = ctk.CTkButton(

        frame_cadastro,

        text="Cadastrar Produto",

        command=cadastrar_produto

    )

    botao_salvar.pack(

        pady=20

    )

    botao_limpar = ctk.CTkButton(
        frame_cadastro,
        text="Limpar Campos",
        command=limpar_campos
    )

    # ==================================================

    # FRAME CONSULTA

    # ==================================================

    frame_consulta = ctk.CTkFrame(

        janela

    )

    titulo_consulta = ctk.CTkLabel(

        frame_consulta,

        text="Produtos Cadastrados",

        font=(

            "Arial",

            24,

            "bold"

        )

    )

    titulo_consulta.pack(

        pady=20

    )

    caixa_resultados = ctk.CTkTextbox(

        frame_consulta,

        width=550,

        height=380

    )

    caixa_resultados.pack(

        pady=10

    )

    botao_atualizar = ctk.CTkButton(

        frame_consulta,

        text="Atualizar Lista",

        command=atualizar_lista_produtos

    )

    botao_atualizar.pack(

        pady=15
    )


    botao_editar = ctk.CTkButton(
    frame_consulta,
    text="Editar Estoque",
    command=editar_estoque_dialog
)

    botao_editar.pack(pady=10)
    
    # ==================================================

    # FRAME VENDA

    # ==================================================

    frame_venda = ctk.CTkFrame(

        janela

    )

    titulo_venda = ctk.CTkLabel(

        frame_venda,

        text="Realizar Venda",

        font=(

            "Arial",

            24,

            "bold"

        )

    )

    titulo_venda.pack(

        pady=30

    )

    entry_venda = ctk.CTkEntry(

        frame_venda,

        width=350,

        placeholder_text="Nome do produto"

    )

    entry_venda.pack(

        pady=20

    )

    botao_vender = ctk.CTkButton(

        frame_venda,

        text="Vender Produto",

        command=vender_produto

    )

    botao_vender.pack(

        pady=20

    )

    mostrar_cadastro()

    janela.update_idletasks()
    botao_limpar.place(
        x=botao_salvar.winfo_x() + botao_salvar.winfo_width() + 10,
        y=botao_salvar.winfo_y()
    )

    janela.mainloop()

# ==================================================

# LOGIN

# ==================================================

def validar_login():

    usuario = entry_user.get()

    senha = entry_senha.get()

    if usuario == "admin" and senha == "1234":

        abrir_sistema_principal()

    else:

        messagebox.showwarning(

            "Aviso",

            "Usuário ou senha incorretos!"

        )

# ==================================================
# BOTÃO EDITAR
# ==================================================

def editar_estoque_dialog():

    cursor.execute("SELECT nome FROM produtos")

    produtos_cadastrados = [
        linha[0] for linha in cursor.fetchall()
    ]

    if not produtos_cadastrados:
        messagebox.showinfo(
            "Vazio",
            "Não há produtos cadastrados para editar."
        )
        return

    dialog = ctk.CTkToplevel(janela)
    dialog.title("Atualizar Saldo")
    dialog.geometry("350x250")

    dialog.attributes("-topmost", True)
    dialog.grab_set()

    combo_produtos = ctk.CTkOptionMenu(
        dialog,
        values=produtos_cadastrados,
        width=200
    )

    combo_produtos.pack(pady=15)


# ==================================================

# JANELA LOGIN

# ==================================================

janela_login = ctk.CTk()

janela_login.geometry(

    "350x400"

)

janela_login.title(

    "Login"

)

titulo_login = ctk.CTkLabel(

    janela_login,

    text="Lanchonete\nEnnius Muniz",

    font=(

        "Arial",

        25,

        "bold"

    )

)

titulo_login.pack(

    pady=40

)

entry_user = ctk.CTkEntry(

    janela_login,

    width=250,

    placeholder_text="Usuário"

)

entry_user.pack(

    pady=10

)

entry_senha = ctk.CTkEntry(

    janela_login,

    width=250,

    placeholder_text="Senha",

    show="*"

)

entry_senha.pack(

    pady=10

)

botao_login = ctk.CTkButton(

    janela_login,

    text="Autenticar",

    command=validar_login

)

botao_login.pack(

    pady=30

)

janela_login.mainloop()