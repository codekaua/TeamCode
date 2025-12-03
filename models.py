from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy import text, DateTime, func
from Model.conexaoDB import SessionLocal, Base, engine
from Model.auth import gerar_hash_senha

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
    detalhe_1 = Column(String)
    detalhe_2 = Column(String)
    detalhe_3 = Column(String)
    detalhe_4 = Column(String)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column("id", Integer, primary_key=True, index=True)
    nome = Column("nome" ,String(50))
    email = Column("email", String(100), unique=True)
    senha = Column("senha", String(200))
    is_admin = Column("is_admin", Boolean, default=False)

    pedidos = relationship("Pedido", back_populates="usuario")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column("id", Integer, primary_key=True, index=True)
    id_usuario = Column("id_usuario", Integer, ForeignKey("usuarios.id")) # id do usuário que está fazendo o pedido
    total = Column("total", Float, default=0.0) # total de pedidos

    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")

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
    produto=Produto(nome=nome, preco=preco, quantidade=quantidade, categoria=categoria, cor=cor, imagem=imagem, detalhe1=detalhe1, detalhe2=detalhe2, detalhe3=detalhe3, detalhe4=detalhe4)
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
        produto.detalhe1 = novo_detalhe1
        produto.detalhe2 = novo_detalhe2
        produto.detalhe3 = novo_detalhe3
        produto.detalhe4 = novo_detalhe4
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
Base.metadata.create_all(bind=engine)  

# teste criar
# create("Bolsa Auxiliar", 7600.000, 10, "Tote", "marrom", "louis-vuitton-bolsa-carryall-vibe-mm-1.avif", "louis-vuitton-bolsa-carryall-vibe3.avif", "louis-vuitton-bolsa-carryall-vibe3.avif", "louis-vuitton-bolsa-carryall-vibe3.avif", "louis-vuitton-bolsa-carryall-vibe3.avif")
# create_usuario("kaua", "kaua@gmail.com", gerar_hash_senha("123"), is_admin=True) 
# create_usuario("kaua", "kauarp.rodrigues@gmail.com", gerar_hash_senha("123"), is_admin=False)
# Visita.__table__.create(bind=engine, checkfirst=True)

# Visita.__table__.drop(engine)  apaga a tabela