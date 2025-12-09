from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException, Query
# APIRouter = Rotas API para o front,
# request = Requisição HTTP,
# Form = Formulário para criar e editar
# UploadFile = Upload da foto
# File = Função para gravar caminho da imagem
# Depends = Dependência do banco de dados sqlite #pip install python-multipart

from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
# HTMLResponse = Resposta do html, get, post, put, delete
# RedirectResponse = Redirecionar a resposta para o front

from fastapi.templating import Jinja2Templates
# Jinja2Templates = Responsável por renderizar o front-end

import os
import shutil
# os = funções de sistema operacional,
# shutil = salva e puxa diretórios do sistema 'caminho das imagens'
import requests
import math
from sqlalchemy.orm import Session
# Session = Modelgem do ORM models

from Model.conexaoDB import get_db, SessionLocal
# get_db = injeção do SessionLocal na API

from models import Produto, Usuario, ItemPedido, Pedido, Visita, Comentario

from Model.auth import gerar_hash_senha, verificar_senha, criar_token, verificar_token

# Produto = Modelagem, nome, preço, quantidade, imagem

router = APIRouter()  # Rotas
templates = Jinja2Templates(directory='./View/templates')  # Front-end

# Caminho da pasta de uploads
UPLOAD_DIR = "static/uploads"  # sem a barra inicial

os.makedirs(UPLOAD_DIR, exist_ok=True)  # cria a pasta se não existir)

# ---------- Verificar token para páginas protegidas ----------


def usuario_logado(request: Request, db: Session = Depends(get_db)):
    """
    Verifica se o usuário está logado (token válido).
    Retorna o objeto `Usuario` se estiver tudo certo.
    Caso contrário, redireciona para /login.
    """
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    # Retorna o usuário autenticado para uso nas rotas
    return usuario


def verificando_token(request: Request):
    token = request.cookies.get("token")
    if not token:
        return False

    payload = verificar_token(token)
    if not payload:
        return False

    return True

# Rota para mostrar página home


@router.get('/', response_class=HTMLResponse)
async def listar_home(request: Request, db: Session = Depends(get_db)):
    usuario = None
    token = request.cookies.get("token")

    if token:
        payload = verificar_token(token)
        if payload:
            email = payload.get("sub")
            usuario = db.query(Usuario).filter(Usuario.email == email).first()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "usuario": usuario
    })

# http://127.0.0.1:8000/produtos/?categoria=couro
# Rota para listar produtos na loja.html


@router.get('/produtos', response_class=HTMLResponse)
def listar(
    request: Request,
    categoria: str | None = Query(None),
    cor: str | None = Query(None),
    db: Session = Depends(get_db)
):
    usuario = None
    token = request.cookies.get("token")

    if token:
        payload = verificar_token(token)
        if payload:
            email = payload.get("sub")
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            return RedirectResponse(url="/me/produtos", status_code=303)
            

    query = db.query(Produto)

    if categoria:
        query = query.filter(Produto.categoria == categoria)
    if cor:
        query = query.filter(Produto.cor == cor)

    produtos = query.all()

    return templates.TemplateResponse("loja.html", {
        "request": request,
        "usuario": usuario,
        "produtos": produtos,
        "categoria_selecionada": categoria,
        "cor_selecionada": cor
    })

# ----- User Produtos -----


@router.get('/me/produtos', response_class=HTMLResponse)
def listar_user(
    request: Request,
    categoria: str | None = Query(None),
    cor: str | None = Query(None),
    db: Session = Depends(get_db)
):
    usuario = None
    token = request.cookies.get("token")

    if token:
        payload = verificar_token(token)
        if payload:
            email = payload.get("sub")
            usuario = db.query(Usuario).filter(Usuario.email == email).first()            

    query = db.query(Produto)

    if categoria:
        query = query.filter(Produto.categoria == categoria)
    if cor:
        query = query.filter(Produto.cor == cor)

    produtos = query.all()

    return templates.TemplateResponse("loja-user.html", {
        "request": request,
        "usuario": usuario,
        "produtos": produtos,
        "categoria_selecionada": categoria,
        "cor_selecionada": cor
    })

# Rota para listar único produto


@router.get('/produto/{id_produto}', response_class=HTMLResponse)
async def detalhe(request: Request, id_produto: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id_produto).first()
    usuario = None
    token = request.cookies.get("token")

    carrinho = []
    if token:
        payload = verificar_token(token)
        if payload:
            email = payload.get("sub")
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            carrinho = carrinhos.get(usuario.id, [])

    return templates.TemplateResponse('produto.html', {
        'request': request,
        'produto': produto,
        'carrinho': carrinho,
        'usuario': usuario
    })

# Rota para mostrar página sobre


@router.get('/sobre', response_class=HTMLResponse)
async def sobre(request: Request, db: Session = Depends(get_db)):
    usuario = None
    token = request.cookies.get("token")

    if token:
        payload = verificar_token(token)
        if payload:
            email = payload.get("sub")
            usuario = db.query(Usuario).filter(Usuario.email == email).first()

    return templates.TemplateResponse('sobre.html', {
        "request": request,
        "usuario": usuario
    })

# Rota para mostrar página login


@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('login.html', {
        'request': request
    })

# ----- Login -----


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return JSONResponse({"mensagem": "Usuário não encontrado."}, status_code=401)

    try:
        if not verificar_senha(senha, usuario.senha):
            return JSONResponse({"mensagem": "Senha incorreta."}, status_code=401)
    except Exception as e:
        print(f"Erro ao verificar senha para {email}: {e}")
        return JSONResponse({"mensagem": "Erro ao verificar senha. Tente redefinir sua senha."}, status_code=500)

    if usuario.is_admin:
        token = criar_token({"sub": usuario.email, "is_admin": True})
        destino = "/admin/dados"
    else:
        token = criar_token({"sub": usuario.email})
        addVisita = Visita(visita=usuario.id)
        db.add(addVisita)
        db.commit()
        db.refresh(addVisita)
        destino = "/me/dados"

    response = RedirectResponse(url=destino, status_code=302)
    response.set_cookie(key="token", value=token, httponly=True)
    return response


# -----   -----

# ----- Dados user -----


@router.get("/me/dados", response_class=HTMLResponse)
def listar_dados(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    admin = db.query(Usuario).filter(Usuario.is_admin)

    return templates.TemplateResponse('perfil_user.html', {
        'request': request,
        'usuario': usuario,
        'admin': admin
    })
# loja-user.html
# ----- User Pedidos -----


@router.get('/me/pedidos', response_class=HTMLResponse)
def listar_pedidos(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    email_usuario = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email_usuario).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    # Busca apenas os pedidos desse usuário
    pedidos = db.query(Pedido).filter(Pedido.id_usuario == usuario.id).all()

    return RedirectResponse(url="/meus-pedidos", status_code=303)

    # return templates.TemplateResponse(
    #     'checkout.html',
    #     {'request': request, 'pedidos': pedidos}
    # )

# -----   -----

# Rota para mostrar página cadastro


@router.get('/register', response_class=HTMLResponse)
async def cadastro(request: Request):
    return templates.TemplateResponse('cadastro.html', {
        'request': request
    })


@router.post('/register')
async def cadastrar_usuario(
        nome: str = Form(...),
        email: str = Form(...),
        senha: str = Form(...),
        db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        return {'mensagem': 'E-mail já cadastrado'}
    else:
        senha_hash = gerar_hash_senha(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return RedirectResponse(url='/login', status_code=303)

# carrinho simples em memória
# adicionar itens ao carrinho
carrinhos = {}
# rotas para carrinho

@router.post("/carrinho/adicionar/{id_produto}")
async def adicionar_carrinho(
    request: Request,
    id_produto: int,
    quantidade: int = Form(1),
    db: Session = Depends(get_db)
):
    # para funcionar o usuário tem que estar logado
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    # caso contrário pega o email dele
    email_usuario = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email_usuario).first()
    produto = db.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        return RedirectResponse(url="/", status_code=303)

    carrinho = carrinhos.get(usuario.id, [])
    if len(carrinho) >= 1:
        # se já houver item, redireciona direto para o carrinho
        return RedirectResponse(url="/carrinho", status_code=303)

    carrinho.append({
        "id": produto.id,
        "nome": produto.nome,
        "preco": float(produto.preco),
        "quantidade": quantidade
    })
    carrinhos[usuario.id] = carrinho  # o id... fez tal pedido
    return RedirectResponse(url="/carrinho", status_code=303)

    # item_existente = db.query(Carrinho).filter(
    #     Carrinho.id_usuario == usuario.id,
    #     Carrinho.id_produto == produto.id
    # ).first()

    # if item_existente:
    #     item_existente.quantidade += quantidade
    # else:
    #     novo_item = Carrinho(id_usuario=usuario.id, id_produto=produto.id, quantidade=quantidade)
    #     db.add(novo_item)

    # db.commit()

# rota para visualizar o carrinho


@router.get("/carrinho", response_class=HTMLResponse)
async def ver_carrinho(request: Request, db: Session = Depends(get_db)):
    usuario = None
    token = request.cookies.get("token")

    if token:
        payload = verificar_token(token)
        if payload:
            email = payload.get("sub")
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
    carrinho = carrinhos.get(usuario.id, [])
    # itens = db.query(Carrinho).filter(Carrinho.id_usuario == usuario.id).all()

    return templates.TemplateResponse("carrinho.html", {
        "request": request,
        "carrinho": carrinho,
        "usuario": usuario
    })


@router.post("/checkout")
async def checkout(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):

    carrinho = carrinhos.get(usuario.id, [])

    if not carrinho:
        return {"mensagem": "Carrinho vazio"}

    # calcula o total
    total = round(sum(item["preco"] * item["quantidade"]
                  for item in carrinho), 2)

    # cria o pedido
    pedido = Pedido(id_usuario=usuario.id, total=total)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)  # para ter acesso ao pedido.id

    # adiciona os itens do carrinho na tabela ItemPedido
    for item in carrinho:
        novo_item = ItemPedido(
            id_pedido=pedido.id,
            id_produto=item["id"],
            quantidade=item["quantidade"],
            preco_unitario=item["preco"]
        )
        db.add(novo_item)
    db.commit()
    # limpa o carrinho
    carrinhos[usuario.id] = []
    return RedirectResponse(url="/meus-pedidos", status_code=303)

# listar pedidos do usuário


@router.get("/meus-pedidos", response_class=HTMLResponse)
def meus_pedidos(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    else:
        pedidos = db.query(Pedido).filter_by(id_usuario=usuario.id).all()

        total_geral = sum(p.total for p in pedidos)

    return templates.TemplateResponse("checkout.html",
                                      {"request": request, "pedidos": pedidos, "total_geral": total_geral, "usuario": usuario})


@router.get("/api/contador-carrinho")
def contador_carrinho(db: Session = Depends(get_db), request: Request = None):
    token = request.cookies.get("token")

    if not token:
        return {"quantidade": 0}

    payload = verificar_token(token)

    if not payload:
        return {"quantidade": 0}

    if not payload:
        return {"quantidade": 0}

    email = payload.get("sub")
    usuario = db.query(Usuario).filter_by(email=email).first()
    if not usuario:
        return {"quantidade": 0}

    # Contar todos os produtos nos pedidos desse usuário
    pedidos = db.query(Pedido).filter_by(id_usuario=usuario.id).all()

    quantidade_total = 0
    for pedido in pedidos:
        itens = db.query(ItemPedido).filter_by(id_pedido=pedido.id).all()
        quantidade_total += sum(i.quantidade for i in itens)

    return {"quantidade": quantidade_total}

# #rota para deletar o produto do carrinho


@router.post("/carrinho/remover/{id_item}")
async def remover_carrinho(request: Request, id_item: int, db: Session = Depends(get_db)):
    item = db.query(Pedido).filter(Pedido.id == id_item).first()
    if item:
        db.delete(item)
        db.commit()
        return RedirectResponse(url="/produtos", status_code=303)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/produtos", status_code=302)
    response.delete_cookie(key="token")
    return response


# imports HTTPException,Query no from fastapi
# import requests,math
# rota frete simulado
# cep fixo da loja
CEP_LOJA = "03008020"  # cep SENAI FRANCISCO MATARAZZO


@router.get("/api/frete")
def calcular_frete(
    request: Request, cep_destino: str = Query(...)
):
    # token login obrigatório
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401,
                            detail="Usuário não autenticado")
    # validação simples do cep
    if not cep_destino.isdigit() or len(cep_destino) != 8:
        raise HTTPException(status_code=400,
                            detail="CEP inválido")
    # consulta no viacep
    via_cep_url = f"https://viacep.com.br/ws/{cep_destino}/json/"
    resposta = requests.get(via_cep_url)
    if resposta.status_code != 200:
        raise HTTPException(status_code=400,
                            detail="Erro ao consultar o CEP")
    dados = resposta.json()
    if "erro" in dados:
        raise HTTPException(status_code=400,
                            detail="CEP não encontrado")
    # simulação do frete
    valor_frete = 15.00
    prazo_estimado = 5
    # retorno estruturado
    return {
        "endereco": f"{dados.get('logradouro')} - {dados.get('bairro')} - {dados.get('localidade')} - {dados.get('uf')}",
        "cep": cep_destino,
        "valor_frete": valor_frete,
        "prazo_estimado_dias": prazo_estimado,
        "status": "Simulação concluída"
    }

#########################


# ----- Rotas Admin -----------------------------------------------------------

def verificarUser(token, db):
    if not token:
        return None, None, None

    payload = verificar_token(token)
    if not payload:
        return None, None, None

    email = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    admin = db.query(Usuario).filter(Usuario.is_admin)

    # Se não é admin → retorna None
    if not usuario or not usuario.is_admin:
        return None, None, None

    return email, usuario, admin


# ----- Dados do admin  -----
@router.get("/admin/dados", response_class=HTMLResponse)
def listar_dados(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        return JSONResponse(status_code=403, content={"mensagem": "Acesso negado!"})

    return templates.TemplateResponse('perfil_admin.html', {
        'request': request,
        'usuario': usuario,
        'admin': admin
    })

# ----- Página home admin -----


@router.get("/admin")
def admin(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        return JSONResponse(status_code=403, content={"mensagem": "Acesso negado!"})

    usuarios = db.query(Usuario).all()
    numerosUsuarios = len(usuarios)

    produtos = db.query(Produto).all()
    numeroProdutos = len(produtos)

    total_acessos = db.query(Visita).count()

    return templates.TemplateResponse("admin.html", {"request": request, "usuario": usuario, "usuarios": numerosUsuarios, "produtos": numeroProdutos, "acessos": total_acessos})

# ----- Página Admin Produto -----


@router.get('/admin/produto', response_class=HTMLResponse)
async def listar_admin(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        return JSONResponse(status_code=403, content={"mensagem": "Acesso negado!"})

    return templates.TemplateResponse('admin-produto.html', {'request': request})


# ----- Página Admin Produto Deletar -----

@router.get('/admin/delete', response_class=HTMLResponse)
async def listar_admin_produto_deletar(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        return JSONResponse(status_code=403, content={"mensagem": "Acesso negado!"})

    produtos = db.query(Produto).all()
    return templates.TemplateResponse('admin-produto-deletar.html', {
        'request': request,
        'produtos': produtos
    })


@router.post("/admin/produto")
def criar_produto(
    request: Request,
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    categoria: str = Form(...),
    cor: str = Form(...),
    imagem: UploadFile = File(...),
    detalhe1: UploadFile | None = File(None),
    detalhe2: UploadFile | None = File(None),
    detalhe3: UploadFile | None = File(None),
    detalhe4: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        return JSONResponse(status_code=403, content={"mensagem": "Acesso negado!"})

    # Gera caminho completo para salvar a imagem principal
    caminho_arquivo = os.path.join(UPLOAD_DIR, imagem.filename)

    # Salva o arquivo
    with open(caminho_arquivo, "wb") as arquivo:
        shutil.copyfileobj(imagem.file, arquivo)

    novo_produto = Produto(
        nome=nome,
        preco=preco,
        quantidade=quantidade,
        categoria=categoria,
        cor=cor,
        imagem=imagem.filename,
        detalhe_1=detalhe1.filename if detalhe1 else "",
        detalhe_2=detalhe2.filename if detalhe2 else "",
        detalhe_3=detalhe3.filename if detalhe3 else "",
        detalhe_4=detalhe4.filename if detalhe4 else ""
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return RedirectResponse(url="/admin/produto", status_code=303)


@router.post("/admin/delete/{id}")
def deletar_produto(request: Request, id: int, db: Session = Depends(get_db)):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        return JSONResponse(status_code=403, content={"mensagem": "Acesso negado!"})

    produto = db.query(Produto).filter(Produto.id == id).first()
    if produto:
        db.delete(produto)
        db.commit()
    return RedirectResponse(url="/admin/delete", status_code=303)


@router.post("/comentarios")
def criar_comentario(
    request: Request,
    rating: int = Form(...),
    comentario: str = Form(...),
    produto_id: int = Form(...),
    db: Session = Depends(get_db)
):

    token = request.cookies.get("token")
    email, usuario, admin = verificarUser(token, db)

    if not usuario:
        usuario_nome = "Anônimo"
    else:
        usuario_nome = usuario.nome

    novo_comentario = Comentario(
        produto_id=produto_id,
        rating=rating,
        comentario=comentario,
        usuario=usuario_nome
    )
    db.add(novo_comentario)
    db.commit()
    db.refresh(novo_comentario)

    # Redireciona para a página do produto
    return RedirectResponse(url=f"/produto/{produto_id}", status_code=303)


@router.get("/produto/{produto_id}")
def ver_produto(produto_id: int, request: Request, db: Session = Depends(get_db)):

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    comentarios = db.query(Comentario).filter(
        Comentario.produto_id == produto_id).all()

    return templates.TemplateResponse("produto.html", {
        "request": request,
        "produto": produto,
        "comentarios": comentarios,
    })
