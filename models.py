from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy import text, DateTime, func
from Model.conexaoDB import SessionLocal, Base, engine
from Model.auth import gerar_hash_senha
import random
from Model.conexaoDB import SessionLocal

# ORM de produto
class Produto(Base):
    __tablename__ = "produtos"

    id = Column("id_produto", Integer, primary_key = True, nullable = False)
    nome = Column("nome_produto", String(100), nullable = False)
    preco = Column("preco", DECIMAL, nullable = False)
    quantidade = Column("quantidade", Integer, nullable=False)
    categoria = Column("categoria", String(100))
    cor = Column("cor", String(45))
    
    # --- Imagens ---
    imagem = Column(String)
    detalhe_1 = Column("detalhe_1", String)
    detalhe_2 = Column("detalhe_2", String)
    detalhe_3 = Column("detalhe_3", String)
    detalhe_4 = Column("detalhe_4", String)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column("id", Integer, primary_key=True, index=True)
    nome = Column("nome" ,String(50))
    email = Column("email", String(100), unique=True)
    senha = Column("senha", String(200))
    is_admin = Column("is_admin", Boolean, default=False)

    pedidos = relationship("Pedido", back_populates="usuario")
    carrinho = relationship("Carrinho", back_populates="usuario")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column("id", Integer, primary_key=True, index=True)
    id_usuario = Column("id_usuario", Integer, ForeignKey("usuarios.id")) # id do usuário que está fazendo o pedido
    total = Column("total", Float, default=0.0) # total de pedidos

    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")

class Carrinho(Base):
    __tablename__ = "carrinho"
    id = Column("id", Integer, primary_key=True, index=True)
    id_usuario = Column("id_usuario", Integer, ForeignKey("usuarios.id")) # id do usuário que está adicionando ao carrinho
    preco = Column("preco", Float)
    quantidade = Column("quantidade", Integer, default=1)
    
    usuario = relationship("Usuario", back_populates="carrinho")

class ItemPedido(Base):
    __tablename__ = "item_pedidos"
    id = Column("id", Integer, primary_key=True, index=True)
    id_pedido = Column("id_pedido", Integer, ForeignKey("pedidos.id"))
    id_produto = Column("id_produto", Integer, ForeignKey("produtos.id_produto"))
    quantidade = Column("quantidade", Integer, default=1) 
    preco_unitario = Column("preco_unitario", Float)

    pedido = relationship("Pedido", back_populates="itens")

class Visita(Base):
    __tablename__ = "visitas"

    id = Column(Integer, primary_key=True, index=True)
    visita = Column("visita", Integer, default=False)

class Comentario(Base):
    __tablename__ = "comentarios"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id_produto"))
    comentario = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    usuario = Column(String(100), nullable=False)

# CRUD PARA PRODUTOS
# CREATE
def create(nome:str, preco:float, quantidade:int, categoria:str, cor:str, imagem:str, detalhe1:str, detalhe2:str, detalhe3:str, detalhe4:str):
    session = SessionLocal()
    produto=Produto(nome=nome, preco=preco, quantidade=quantidade, categoria=categoria, cor=cor, imagem=imagem, detalhe_1=detalhe1, detalhe_2=detalhe2, detalhe_3=detalhe3, detalhe_4=detalhe4)
    session.add(produto)
    session.commit()
    session.close()

# READ
def read():
    session = SessionLocal()
    produtos = session.query(Produto).all()
    session.close()
    return produtos

# UPDATE
def update(id_produto:int, novo_nome:str, novo_preco:float, nova_categoria:str, nova_cor:str, nova_imagem:str, novo_detalhe1:str, novo_detalhe2:str, novo_detalhe3:str, novo_detalhe4:str):
    session = SessionLocal()
    produto = session.query(Produto).filter(Produto.id==id_produto).first()
    if produto:
        produto.nome = novo_nome
        produto.preco = novo_preco
        produto.categoria = nova_categoria
        produto.cor = nova_cor
        produto.imagem = nova_imagem
        produto.detalhe_1 = novo_detalhe1
        produto.detalhe_2 = novo_detalhe2
        produto.detalhe_3 = novo_detalhe3
        produto.detalhe_4 = novo_detalhe4
        session.commit()
    session.close()

# DELETE
def delete(id_produto:int):
    session=SessionLocal()
    produto=session.query(Produto).filter(Produto.id==id_produto).first()
    if produto:
        session.delete(produto)
        session.commit()
    session.close()

# CRUD PARA USUARIOS 
# create
def create_usuario(nome:str, email:str, senha:str, is_admin:bool):
    session = SessionLocal()
    usuario=Usuario(nome=nome, email=email, senha=senha, is_admin=is_admin)
    session.add(usuario)
    session.commit()
    session.close()

# Criação das tabelas
# Base.metadata.create_all(bind=engine)

# teste criar
# create("Bolsa Auxiliar", 7600.000, 10, "Tote", "marrom", "louis-vuitton-bolsa-carryall-vibe-mm-1.avif", "louis-vuitton-bolsa-carryall-vibe3.avif", "louis-vuitton-bolsa-carryall-vibe3.avif", "louis-vuitton-bolsa-carryall-vibe3.avif", "louis-vuitton-bolsa-carryall-vibe3.avif")
# create_usuario("kaua", "kaua@gmail.com", gerar_hash_senha("123"), is_admin=True) 
# create_usuario("kaua", "kauarp.rodrigues@gmail.com", gerar_hash_senha("123"), is_admin=False)
# Carrinho.__table__.create(bind=engine, checkfirst=True)

# Carrinho.__table__.drop(engine)  # apaga a tabela

# Lembre-se de importar a sua classe Produto!

def popular_banco_por_categoria():
    session = SessionLocal()
    
    cores_lista = ["Preto", "Marrom", "Vermelho", "Azul", "Branco", "Bege", "Verde", "Rosa"]
    
    # Criamos os "Kits" focados no FORMATO da bolsa (Categoria)
    kits_de_imagens = {
        "Tote": [ 
            # Imagens focadas em bolsas grandes de ombro
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/2021/23-11/foto-1.png", # Principal
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/2021/23-11/foto-1.png", # Detalhe1
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/2021/23-11/foto-2.png",    # Detalhe2
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/2021/23-11/foto-3.png", # Detalhe3
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/17.20251106144441.png"  # Detalhe4
        ],
        "Clutch": [ 
            # Imagens focadas em bolsas pequenas/de mão
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/2024/25-06/bolsa-feminina-pequena-transversal.jpeg", # Principal
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/2024/25-06/bolsa-feminina-pequena-transversal.jpeg", # Detalhe: Base
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/dua-5775.JPG",    # Detalhe: Fecho
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/dua-5759.JPG", # Ângulo 2
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/24.png"  # Ângulo 3
        ],
        "Crossbody": [ 
            # Imagens focadas em bolsas transversais
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/produtos/bolsas/2020/28-08/link7/screenshot-1.png", # Principal
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/produtos/bolsas/2020/28-08/link7/screenshot-1.png", # Detalhe
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/img-6953.JPG",    # Detalhe
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/20.20251106144442.png", # Ângulo 2
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/img-6951.JPG"  # Ângulo 3
        ],
        "Bucket": [ 
            # Imagens focadas em bolsas estilo saco
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/img-5435.JPG", # Principal
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(transparent):quality(80)/daniella/catalog/19.20251106144442.png", 
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/img-6953.JPG",    
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/jar-9754.JPG", 
            "https://img.irroba.com.br/fit-in/600x600/filters:format(webp):fill(fff):quality(80)/daniella/catalog/img-0760.JPG"  
        ]
    }
    
    # As categorias agora são as chaves do nosso dicionário
    categorias_disponiveis = list(kits_de_imagens.keys())
    
    produtos_para_inserir = []
    print("Gerando 1000 produtos alinhados perfeitamente por CATEGORIA...")
    
    for i in range(1, 1001):
        # Sorteia uma das 4 categorias que configuramos
        categoria_escolhida = random.choice(categorias_disponiveis)
        # Sorteia a cor (texto aleatório)
        cor_escolhida = random.choice(cores_lista)
        
        # Pega a lista de 5 imagens correspondente à categoria sorteada
        imagens_da_categoria = kits_de_imagens[categoria_escolhida]
        
        produto = Produto(
            nome=f"Bolsa {categoria_escolhida} {cor_escolhida} Luxo {i}",
            preco=round(random.uniform(250.0, 5500.0), 2),
            quantidade=random.randint(1, 20),
            categoria=categoria_escolhida,
            cor=cor_escolhida,
            # Distribui as imagens no banco de dados respeitando a categoria:
            imagem=imagens_da_categoria[0],
            detalhe_1=imagens_da_categoria[1],
            detalhe_2=imagens_da_categoria[2],
            detalhe_3=imagens_da_categoria[3],
            detalhe_4=imagens_da_categoria[4]
        )
        
        produtos_para_inserir.append(produto)
    
    try:
        session.bulk_save_objects(produtos_para_inserir)
        session.commit()
        print("Sucesso! 1000 produtos inseridos com imagens focadas no formato (Categoria).")
    except Exception as e:
        session.rollback()
        print(f"Erro ao inserir: {e}")
    finally:
        session.close()

# 1. Rode a função limpar_todos_os_produtos() primeiro
# 2. Descomente a linha abaixo e rode para inserir os novos
# popular_banco_por_categoria()

# Certifique-se de que SessionLocal e os modelos (Produto, ItemPedido, etc.) estão importados no topo do arquivo.

def limpar_todos_os_produtos():
    session = SessionLocal()
    try:
        print("Iniciando a limpeza do banco de dados...")
        
        # 1. Primeiro, apagamos as relações (para evitar erro de Foreign Key)
        # Se você não tiver alguma dessas tabelas, pode apagar ou comentar a linha dela
        session.query(ItemPedido).delete()
        session.query(Comentario).delete()
        session.query(Carrinho).delete() 
        
        # 2. Agora apagamos todos os produtos
        produtos_eliminados = session.query(Produto).delete()
        
        # 3. Confirmamos a exclusão
        session.commit()
        
        print(f"Faxina concluída! {produtos_eliminados} produtos foram apagados.")
    except Exception as e:
        session.rollback()
        print(f"Ocorreu um erro ao limpar: {e}")
    finally:
        session.close()

# Descomente a linha abaixo para executar a limpeza
# limpar_todos_os_produtos()


# ==========================================================
# FUNÇÃO PARA ZERAR TODOS OS PEDIDOS DO SISTEMA
# ==========================================================

def zerar_pedidos_e_itens():
    session = SessionLocal()
    try:
        print("Iniciando a limpeza do histórico de pedidos...")
        
        # 1. Primeiro apagamos as tabelas filhas (ItemPedido)
        itens_apagados = session.query(ItemPedido).delete()
        
        # 2. Agora que os itens sumiram, podemos apagar a tabela pai (Pedido)
        pedidos_apagados = session.query(Pedido).delete()
        
        # 3. Confirmamos a exclusão no banco de dados
        session.commit()
        
        print(f"Faxina de vendas concluída! {pedidos_apagados} pedidos e {itens_apagados} itens foram apagados do banco.")
    except Exception as e:
        # Se der algum erro (ex: banco travado), desfaz tudo para não corromper
        session.rollback()
        print(f"Ocorreu um erro ao limpar os pedidos: {e}")
    finally:
        # Fecha a conexão para não deixar o banco sobrecarregado
        session.close()

# Descomente a linha abaixo e rode o arquivo UMA VEZ para limpar o banco. 
# Depois, comente novamente para não apagar as vendas novas toda vez que reiniciar o servidor!

# zerar_pedidos_e_itens()
