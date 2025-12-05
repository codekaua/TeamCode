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
# Visita.__table__.create(bind=engine, checkfirst=True)

# Visita.__table__.drop(engine)  apaga a tabela

# Criar produtos

# create("Clutch Elegance", 2450.00, 28, "Clutch", "Preto", "clutch-elegance-principal.png", "clutch-elegance-detalhe1.png", "clutch-elegance-detalhe2.png", "clutch-elegance-detalhe3.png", "clutch-elegance-detalhe4.png")
# create("Tote Classic", 3850.00, 17, "Tote", "Preto", "tote-classic-principal.png", "tote-classic-detalhe1.png", "tote-classic-detalhe2.png", "tote-classic-detalhe3.png", "tote-classic-detalhe4.png")
# create("Crossbody Mini", 1850.00, 42, "Crossbody", "Preto", "crossbody-mini-principal.png", "crossbody-mini-detalhe1.png", "crossbody-mini-principal.png", "crossbody-mini-principal.png", "crossbody-mini-detalhe1.png")
# create("Bucket Drawstring", 2450.00, 29, "Bucket", "Preto", "bucket-drawstring-principal.png", "bucket-drawstring-detalhe1.png", "bucket-drawstring-detalhe2.png", "bucket-drawstring-detalhe3.png", "bucket-drawstring-detalhe4.png")
# create("Baguette Classic", 4550.00, 13, "Baguette", "Preto", "baguette-classic-principal.png", "baguette-classic-detalhe1.png", "baguette-classic-detalhe2.png", "baguette-classic-detalhe3.png", "baguette-classic-detalhe4.png")
# create("Shoulder Bag Classic", 2850.00, 25, "Shoulder bag", "Preto", "shoulder-bag-classic-principal.png", "shoulder-bag-classic-detalhe1.png", "shoulder-bag-classic-detalhe2.png", "shoulder-bag-classic-detalhe3.png", "shoulder-bag-classic-detalhe4.png")
# create("Clutch Minimalist", 1250.00, 33, "Clutch", "Azul", "clutch-minimalist-principal.png", "clutch-minimalist-detalhe1.png", "clutch-minimalist-detalhe2.png", "clutch-minimalist-detalhe3.png", "clutch-minimalist-detalhe4.png")
# create("Default Clutch", 1350.00, 10, "Clutch", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1275.50, 10, "Crossbody", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1420.00, 10, "Baguette", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1180.00, 10, "Shoulder bag", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1550.00, 10, "Bucket", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1320.00, 10, "Tote", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1250.00, 10, "Clutch", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1480.00, 10, "Crossbody", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1190.00, 10, "Baguette", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1650.00, 10, "Shoulder bag", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1380.00, 10, "Bucket", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1220.00, 10, "Tote", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1570.00, 10, "Clutch", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1290.00, 10, "Crossbody", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1440.00, 10, "Baguette", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1160.00, 10, "Shoulder bag", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1520.00, 10, "Bucket", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1340.00, 10, "Tote", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1260.00, 10, "Clutch", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1410.00, 10, "Crossbody", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1180.00, 10, "Baguette", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1630.00, 10, "Shoulder bag", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1370.00, 10, "Bucket", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1210.00, 10, "Tote", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1590.00, 10, "Clutch", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1310.00, 10, "Crossbody", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1460.00, 10, "Baguette", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1140.00, 10, "Shoulder bag", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1540.00, 10, "Bucket", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1360.00, 10, "Tote", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1240.00, 10, "Clutch", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1430.00, 10, "Crossbody", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1170.00, 10, "Baguette", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1610.00, 10, "Shoulder bag", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1390.00, 10, "Bucket", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1230.00, 10, "Tote", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1560.00, 10, "Clutch", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1280.00, 10, "Crossbody", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1450.00, 10, "Baguette", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1150.00, 10, "Shoulder bag", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1530.00, 10, "Bucket", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1330.00, 10, "Tote", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1255.00, 10, "Clutch", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1425.00, 10, "Crossbody", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1195.00, 10, "Baguette", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1645.00, 10, "Shoulder bag", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1385.00, 10, "Bucket", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1225.00, 10, "Tote", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1585.00, 10, "Clutch", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1305.00, 10, "Crossbody", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1475.00, 10, "Baguette", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1135.00, 10, "Shoulder bag", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1555.00, 10, "Bucket", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1355.00, 10, "Tote", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1275.00, 10, "Clutch", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1445.00, 10, "Crossbody", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1205.00, 10, "Baguette", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1625.00, 10, "Shoulder bag", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1405.00, 10, "Bucket", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1245.00, 10, "Tote", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1575.00, 10, "Clutch", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1295.00, 10, "Crossbody", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1465.00, 10, "Baguette", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1145.00, 10, "Shoulder bag", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1545.00, 10, "Bucket", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1365.00, 10, "Tote", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1265.00, 10, "Clutch", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1435.00, 10, "Crossbody", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1215.00, 10, "Baguette", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1635.00, 10, "Shoulder bag", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1415.00, 10, "Bucket", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1255.00, 10, "Tote", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1595.00, 10, "Clutch", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1315.00, 10, "Crossbody", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1485.00, 10, "Baguette", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1155.00, 10, "Shoulder bag", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1565.00, 10, "Bucket", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1375.00, 10, "Tote", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1285.00, 10, "Clutch", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1455.00, 10, "Crossbody", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1225.00, 10, "Baguette", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1645.00, 10, "Shoulder bag", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1425.00, 10, "Bucket", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1265.00, 10, "Tote", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1605.00, 10, "Clutch", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1325.00, 10, "Crossbody", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1495.00, 10, "Baguette", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1165.00, 10, "Shoulder bag", "Cinza", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1575.00, 10, "Bucket", "Preto", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1385.00, 10, "Tote", "Roxo", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1295.00, 10, "Clutch", "Marrom", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1465.00, 10, "Crossbody", "Branco", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1235.00, 10, "Baguette", "Natural", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Shoulder bag", 1655.00, 10, "Shoulder bag", "Bege", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Bucket", 1435.00, 10, "Bucket", "Vermelho", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Tote", 1275.00, 10, "Tote", "Prata", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Clutch", 1615.00, 10, "Clutch", "Verde", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Crossbody", 1335.00, 10, "Crossbody", "Azul", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")
# create("Default Baguette", 1505.00, 10, "Baguette", "Rosa", "img-principal-default.png", "img-detalhe1-default.png", "img-detalhe2-default.png", "img-detalhe3-default.png", "img-detalhe4-default.png")