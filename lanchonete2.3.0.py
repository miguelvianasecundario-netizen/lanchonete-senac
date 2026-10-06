import customtkinter as ctk
import sqlite3
import os
from tkinter import messagebox

# ==============================
# CONFIGURAÇÕES
# ==============================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

USUARIO_CORRETO = "admin"
SENHA_CORRETA = "1234"


# ==============================
# BANCO DE DADOS
# ==============================

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_banco = os.path.join(diretorio_atual, "sistema.db")


def conectar():
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
    return conexao, cursor


# ==============================
# LOGIN
# ==============================

def autenticar():
    usuario = entry_usuario.get().strip()
    senha = entry_senha.get().strip()

    # TESTE DE LIMITE 1
    if usuario == "" or senha == "":
        messagebox.showwarning(
            "Aviso",
            "Preencha usuário e senha!"
        )
        return

    if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
        frame_login.pack_forget()
        frame_sistema.pack(
            fill="both",
            expand=True
        )

        atualizar_lista_produtos()

    else:
        messagebox.showerror(
            "Erro",
            "Usuário ou senha incorretos!"
        )


def voltar_login():
    frame_sistema.pack_forget()

    entry_usuario.delete(0, "end")
    entry_senha.delete(0, "end")

    frame_login.pack(
        fill="both",
        expand=True
    )


# ==============================
# CADASTRO
# ==============================

def cadastrar_produto():
    nome = entry_nome.get().strip()
    preco = entry_preco.get().strip()
    quantidade = entry_quantidade.get().strip()

    if nome == "" or preco == "" or quantidade == "":
        messagebox.showwarning(
            "Aviso",
            "Preencha todos os campos!"
        )
        return

    try:
        preco = float(
            preco.replace(",", ".")
        )

        quantidade = int(
            quantidade
        )

    except ValueError:
        messagebox.showerror(
            "Erro",
            "Preço e quantidade devem ser números!"
        )
        return

    if preco < 0:
        messagebox.showwarning(
            "Aviso",
            "O preço não pode ser negativo!"
        )
        return

    if quantidade < 0:
        messagebox.showwarning(
            "Aviso",
            "A quantidade não pode ser negativa!"
        )
        return

    conexao, cursor = conectar()

    cursor.execute(
        "SELECT nome FROM produtos WHERE nome = ?",
        (nome,)
    )

    produto_existente = cursor.fetchone()

    if produto_existente:
        conexao.close()

        messagebox.showwarning(
            "Aviso",
            "Esse produto já está cadastrado!"
        )

        return

    cursor.execute(
        """
        INSERT INTO produtos
        (nome, preco, quantidade)
        VALUES (?, ?, ?)
        """,
        (
            nome,
            preco,
            quantidade
        )
    )

    conexao.commit()
    conexao.close()

    messagebox.showinfo(
        "Sucesso",
        f"Produto '{nome}' cadastrado!"
    )

    entry_nome.delete(0, "end")
    entry_preco.delete(0, "end")
    entry_quantidade.delete(0, "end")

    atualizar_lista_produtos()


# ==============================
# VENDA
# ==============================

def vender_produto(nome_produto):
    conexao, cursor = conectar()

    cursor.execute(
        """
        SELECT quantidade
        FROM produtos
        WHERE nome = ?
        """,
        (nome_produto,)
    )

    resultado = cursor.fetchone()

    if resultado is None:
        conexao.close()

        messagebox.showerror(
            "Erro",
            "Produto não encontrado!"
        )
        return

    qtd_atual = resultado[0]

    # TESTE DE LIMITE 2
    # NÃO PERMITE ESTOQUE NEGATIVO

    if qtd_atual > 0:

        nova_qtd = qtd_atual - 1

        cursor.execute(
            """
            UPDATE produtos
            SET quantidade = ?
            WHERE nome = ?
            """,
            (
                nova_qtd,
                nome_produto
            )
        )

        conexao.commit()

        messagebox.showinfo(
            "Venda",
            f"Venda realizada!\n\n"
            f"Produto: {nome_produto}\n"
            f"Estoque anterior: {qtd_atual}\n"
            f"Estoque atual: {nova_qtd}"
        )

    else:

        messagebox.showwarning(
            "Aviso",
            "Produto esgotado!"
        )

    conexao.close()

    atualizar_lista_produtos()


# ==============================
# EXCLUIR PRODUTO
# ==============================

def excluir_produto(nome_produto):
    resposta = messagebox.askyesno(
        "Excluir",
        f"Deseja excluir '{nome_produto}'?"
    )

    if not resposta:
        return

    conexao, cursor = conectar()

    cursor.execute(
        """
        DELETE FROM produtos
        WHERE nome = ?
        """,
        (nome_produto,)
    )

    conexao.commit()
    conexao.close()

    atualizar_lista_produtos()


# ==============================
# LISTAR PRODUTOS
# ==============================

def atualizar_lista_produtos():

    # Apaga os produtos da lista atual
    for widget in frame_lista.winfo_children():
        widget.destroy()

    conexao, cursor = conectar()

    cursor.execute(
        """
        SELECT nome, preco, quantidade
        FROM produtos
        ORDER BY nome
        """
    )

    produtos = cursor.fetchall()

    conexao.close()

    if not produtos:

        label_vazio = ctk.CTkLabel(
            frame_lista,
            text="Nenhum produto cadastrado.",
            font=(
                "Arial",
                16
            )
        )

        label_vazio.pack(
            pady=30
        )

        return

    for nome, preco, quantidade in produtos:

        frame_produto = ctk.CTkFrame(
            frame_lista
        )

        frame_produto.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # ==========================
        # TESTE VISUAL
        # ==========================

        if quantidade <= 5:
            cor_estoque = "red"
        else:
            cor_estoque = "white"

        label_nome = ctk.CTkLabel(
            frame_produto,
            text=nome,
            width=180,
            anchor="w",
            font=(
                "Arial",
                15,
                "bold"
            ),
            text_color=cor_estoque
        )

        label_nome.grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )

        label_preco = ctk.CTkLabel(
            frame_produto,
            text=f"R$ {preco:.2f}",
            width=120
        )

        label_preco.grid(
            row=0,
            column=1,
            padx=10
        )

        label_quantidade = ctk.CTkLabel(
            frame_produto,
            text=f"Estoque: {quantidade}",
            width=120,
            text_color=cor_estoque
        )

        label_quantidade.grid(
            row=0,
            column=2,
            padx=10
        )

        botao_vender = ctk.CTkButton(
            frame_produto,
            text="Vender",
            width=100,
            command=lambda n=nome:
            vender_produto(n)
        )

        botao_vender.grid(
            row=0,
            column=3,
            padx=5
        )

        botao_excluir = ctk.CTkButton(
            frame_produto,
            text="Excluir",
            width=80,
            fg_color="#8B0000",
            hover_color="#B22222",
            command=lambda n=nome:
            excluir_produto(n)
        )

        botao_excluir.grid(
            row=0,
            column=4,
            padx=5
        )


# ==============================
# JANELA
# ==============================

janela = ctk.CTk()

janela.title(
    "Lanchonete Ennius Muniz - Senac DF"
)

janela.geometry(
    "900x650"
)

janela.minsize(
    800,
    600
)


# ==============================
# FRAME LOGIN
# ==============================

frame_login = ctk.CTkFrame(
    janela
)

frame_login.pack(
    fill="both",
    expand=True
)


titulo_login = ctk.CTkLabel(
    frame_login,
    text="Lanchonete Ennius Muniz",
    font=(
        "Arial",
        28,
        "bold"
    )
)

titulo_login.pack(
    pady=50
)


subtitulo_login = ctk.CTkLabel(
    frame_login,
    text="Sistema de Controle de Estoque",
    font=(
        "Arial",
        18
    )
)

subtitulo_login.pack(
    pady=10
)


entry_usuario = ctk.CTkEntry(
    frame_login,
    width=300,
    height=40,
    placeholder_text="Usuário"
)

entry_usuario.pack(
    pady=10
)


entry_senha = ctk.CTkEntry(
    frame_login,
    width=300,
    height=40,
    placeholder_text="Senha",
    show="*"
)

entry_senha.pack(
    pady=10
)


botao_entrar = ctk.CTkButton(
    frame_login,
    text="Entrar",
    width=300,
    height=40,
    command=autenticar
)

botao_entrar.pack(
    pady=20
)


label_dica = ctk.CTkLabel(
    frame_login,
    text="Usuário: admin | Senha: 1234",
    text_color="gray"
)

label_dica.pack(
    pady=10
)


# ==============================
# FRAME SISTEMA
# ==============================

frame_sistema = ctk.CTkFrame(
    janela
)


titulo = ctk.CTkLabel(
    frame_sistema,
    text="Controle de Produtos",
    font=(
        "Arial",
        26,
        "bold"
    )
)

titulo.pack(
    pady=20
)


# ==============================
# CADASTRO DE PRODUTOS
# ==============================

frame_cadastro = ctk.CTkFrame(
    frame_sistema
)

frame_cadastro.pack(
    fill="x",
    padx=20,
    pady=10
)


label_cadastro = ctk.CTkLabel(
    frame_cadastro,
    text="Cadastrar novo produto",
    font=(
        "Arial",
        18,
        "bold"
    )
)

label_cadastro.grid(
    row=0,
    column=0,
    columnspan=4,
    pady=15
)


entry_nome = ctk.CTkEntry(
    frame_cadastro,
    width=200,
    placeholder_text="Nome do produto"
)

entry_nome.grid(
    row=1,
    column=0,
    padx=10,
    pady=15
)


entry_preco = ctk.CTkEntry(
    frame_cadastro,
    width=150,
    placeholder_text="Preço"
)

entry_preco.grid(
    row=1,
    column=1,
    padx=10,
    pady=15
)


entry_quantidade = ctk.CTkEntry(
    frame_cadastro,
    width=150,
    placeholder_text="Quantidade"
)

entry_quantidade.grid(
    row=1,
    column=2,
    padx=10,
    pady=15
)


botao_cadastrar = ctk.CTkButton(
    frame_cadastro,
    text="Cadastrar",
    command=cadastrar_produto
)

botao_cadastrar.grid(
    row=1,
    column=3,
    padx=10,
    pady=15
)


frame_cadastro.grid_columnconfigure(
    0,
    weight=1
)

frame_cadastro.grid_columnconfigure(
    1,
    weight=1
)

frame_cadastro.grid_columnconfigure(
    2,
    weight=1
)

frame_cadastro.grid_columnconfigure(
    3,
    weight=1
)


# ==============================
# CABEÇALHO DA LISTA
# ==============================

frame_cabecalho = ctk.CTkFrame(
    frame_sistema
)

frame_cabecalho.pack(
    fill="x",
    padx=20,
    pady=5
)


ctk.CTkLabel(
    frame_cabecalho,
    text="Produto",
    width=180,
    font=(
        "Arial",
        14,
        "bold"
    )
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10
)


ctk.CTkLabel(
    frame_cabecalho,
    text="Preço",
    width=120,
    font=(
        "Arial",
        14,
        "bold"
    )
).grid(
    row=0,
    column=1,
    padx=10
)


ctk.CTkLabel(
    frame_cabecalho,
    text="Quantidade",
    width=120,
    font=(
        "Arial",
        14,
        "bold"
    )
).grid(
    row=0,
    column=2,
    padx=10
)


ctk.CTkLabel(
    frame_cabecalho,
    text="Ações",
    width=190,
    font=(
        "Arial",
        14,
        "bold"
    )
).grid(
    row=0,
    column=3,
    columnspan=2,
    padx=10
)


# ==============================
# LISTA COM SCROLL
# ==============================

frame_lista = ctk.CTkScrollableFrame(
    frame_sistema
)

frame_lista.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


# ==============================
# BOTÕES INFERIORES
# ==============================

frame_botoes = ctk.CTkFrame(
    frame_sistema,
    fg_color="transparent"
)

frame_botoes.pack(
    fill="x",
    padx=20,
    pady=10
)


botao_atualizar = ctk.CTkButton(
    frame_botoes,
    text="Atualizar",
    command=atualizar_lista_produtos
)

botao_atualizar.pack(
    side="left",
    padx=5
)


botao_logout = ctk.CTkButton(
    frame_botoes,
    text="Voltar ao Login",
    fg_color="#555555",
    hover_color="#333333",
    command=voltar_login
)

botao_logout.pack(
    side="right",
    padx=5
)


# ==============================
# EXECUTAR
# ==============================

janela.mainloop()