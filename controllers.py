from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException, Query, status
# APIRouter = Rotas API para o front,
# request = Requisição HTTP,
# Form = Formulário para criar e editar
# UploadFile = Upload da foto
# File = Função para gravar caminho da imagem
# Depends = Dependência do banco de dados sqlite #pip install python-multipart

from pydantic import BaseModel, EmailStr

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

from models import Produto, Usuario, ItemPedido, Pedido, Visita, update

from Model.auth import gerar_hash_senha, verificar_senha, criar_token, verificar_token

# Produto = Modelagem, nome, preço, quantidade, imagem


# ==========================================================
# CONFIGURAÇÕES INICIAIS
# ==========================================================

router = APIRouter()  # Rotas
templates = Jinja2Templates(directory='./View/templates')  # Front-end

# Caminho da pasta de uploads
UPLOAD_DIR = "static/uploads"  # sem a barra inicial
os.makedirs(UPLOAD_DIR, exist_ok=True)  # cria a pasta se não existir)

# Carrinho simples em memória (Dicionário Global)
# Formato: { id_usuario: [{"id": 1, "nome": "...", "preco": 100, "quantidade": 1}] }
carrinhos = {}

# cep fixo da loja
CEP_LOJA = "03008020"  # cep SENAI FRANCISCO MATARAZZO


# ==========================================================
# MODELOS PYDANTIC
# ==========================================================

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str 
    
class CadastroSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str

# Modelo de dados esperado do front-end (JSON) para atualizar quantidades no carrinho
class AtualizarCarrinho(BaseModel):
    id_produto: int
    quantidade: int


# ==========================================================
# DEPENDÊNCIAS DE AUTENTICAÇÃO E PERMISSÃO
# ==========================================================

def usuario_logado(request: Request, db: Session = Depends(get_db)):
    """
    Verifica se o usuário está logado (token válido).
    Retorna o objeto `Usuario` se estiver tudo certo.
    Caso contrário, redireciona para /login disparando um HTTPException.
    """
    # Puxa o token salvo nos cookies do navegador
    token = request.cookies.get("token")
    
    # Se não tem token, redireciona pro login levantando um erro 303 com Location
    if not token:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})

    # Tenta decodificar e validar o token
    payload = verificar_token(token)

    # Se o token expirou ou é invalido
    if not payload:
        # Redireciona e apaga o cookie expirado (usando o cabeçalho Set-Cookie)
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            headers={"Location": "/login?expirado=true", "Set-Cookie": "token=; Max-Age=0; Path=/"}
        )

    # Extrai o email do payload e busca no banco de dados
    email = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    # Se por algum motivo o token existir mas o usuário foi deletado do banco
    if not usuario:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})

    # Se chegou até aqui, está tudo certo! Retorna o usuário.
    return usuario


# 1. Dependência para páginas públicas (Home, Sobre, Produto)
def obter_usuario_opcional(request: Request, db: Session = Depends(get_db)):
    """Busca o usuário logado, mas se não tiver, não tem problema (retorna None)."""
    token = request.cookies.get("token")
    if not token:
        return None  # Visitante anônimo
    
    payload = verificar_token(token)
    if not payload:
        return None  # Visitante com token expirado
        
    email = payload.get("sub")
    return db.query(Usuario).filter(Usuario.email == email).first()


# 2. Dependência para Admin (Painel de controle, Cadastro de produtos)
def admin_requerido(request: Request, db: Session = Depends(get_db)):
    """Verifica se o usuário está logado E se é administrador."""
    token = request.cookies.get("token")
    if not token:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado!")
         
    payload = verificar_token(token)
    if not payload:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado!")
         
    email = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    # Validação dupla: Verifica se o usuário existe E se a flag is_admin é verdadeira
    if not usuario or not usuario.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado!")
        
    return usuario


# ==========================================================
# ROTAS: AUTENTICAÇÃO E CADASTRO (LOGIN / REGISTER / LOGOUT)
# ==========================================================

# Rota para mostrar página login
@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    # Apenas renderiza o formulário de login para o usuário
    return templates.TemplateResponse('login.html', {
        'request': request
    })

# Rota para processar o login (Ação do Formulário)
@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # Busca o usuário no banco de dados através do email informado
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return JSONResponse({"mensagem": "Usuário não encontrado."}, status_code=401)

    # Bloco try-except para evitar quebra caso o hash salvo esteja mal formatado
    try:
        # Compara a senha digitada em texto plano com o Hash armazenado no banco
        if not verificar_senha(senha, usuario.senha):
            return JSONResponse({"mensagem": "Senha incorreta."}, status_code=401)
    except Exception as e:
        print(f"Erro ao verificar senha para {email}: {e}")
        return JSONResponse({"mensagem": "Erro ao verificar senha. Tente redefinir sua senha."}, status_code=500)

    # Verifica o nível de permissão para gerar o token e definir a página de destino
    if usuario.is_admin:
        token = criar_token({"sub": usuario.email, "is_admin": True})
        destino = "/admin/dados"
    else:
        token = criar_token({"sub": usuario.email})
        # Se for usuário comum, registra o acesso na tabela de Visitas para estatísticas
        addVisita = Visita(visita=usuario.id)
        db.add(addVisita)
        db.commit()
        db.refresh(addVisita)
        destino = "/me/dados"

    # Cria o redirecionamento e injeta o Cookie do token protegido (httponly impede leitura via JavaScript)
    response = RedirectResponse(url=destino, status_code=302)
    response.set_cookie(key="token", value=token, httponly=True)
    return response

# Rota para mostrar página cadastro
@router.get('/register', response_class=HTMLResponse)
async def cadastro(request: Request):
    # Apenas renderiza o formulário de registro
    return templates.TemplateResponse('cadastro.html', {
        'request': request
    })

# Rota para processar o cadastro (Ação do Formulário)
@router.post('/register')
async def cadastrar_usuario(
        nome: str = Form(...),
        email: str = Form(...),
        senha: str = Form(...),
        db: Session = Depends(get_db)):
    
    # Verifica se já existe um usuário com esse email para não duplicar
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        return {'mensagem': 'E-mail já cadastrado'}
    else:
        # Gera o hash (versão criptografada) da senha digitada
        senha_hash = gerar_hash_senha(senha)
        
        # Cria a instância do novo usuário e salva no banco de dados
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        # Manda o recém-cadastrado direto para a página de login
        return RedirectResponse(url='/login', status_code=303)

# Rota para processar o logout
@router.get("/logout")
def logout():
    # Redireciona o usuário para a página pública de produtos
    response = RedirectResponse(url="/me/produtos", status_code=302)
    # Exclui o cookie "token", encerrando a sessão
    response.delete_cookie(key="token")
    return response


# ==========================================================
# ROTAS: PÁGINAS PÚBLICAS (HOME / SOBRE)
# ==========================================================

# Rota para mostrar página home
@router.get('/', response_class=HTMLResponse)
async def listar_home(request: Request, usuario: Usuario = Depends(obter_usuario_opcional)):
    # Renderiza a home passando o 'usuario' opcional para o Jinja mostrar/esconder botões de login
    return templates.TemplateResponse("home.html", {
        "request": request,
        "usuario": usuario
    })

# Rota para mostrar página sobre
@router.get('/sobre', response_class=HTMLResponse)
async def sobre(request: Request, usuario: Usuario = Depends(obter_usuario_opcional)):
    # Renderiza a página "Sobre a loja"
    return templates.TemplateResponse('sobre.html', {
        "request": request,
        "usuario": usuario
    })


# ==========================================================
# ROTAS: PRODUTOS (CATÁLOGO CLIENTE)
# ==========================================================

# Rota para listar produtos na loja.html (Catálogo Principal)
# Permite filtros por query params (ex: http://127.0.0.1:8000/produtos/?categoria=couro)
@router.get('/me/produtos', response_class=HTMLResponse)
def listar_user(
    request: Request,
    categoria: str | None = Query(None),
    cor: str | None = Query(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_opcional)):

    # Inicia a busca base (SELECT * FROM Produto)
    query = db.query(Produto)

    # Se o usuário passou uma categoria na URL, adiciona a cláusula WHERE categoria = ...
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    
    # Se o usuário passou uma cor na URL, adiciona a cláusula WHERE cor = ...
    if cor:
        query = query.filter(Produto.cor == cor)

    # Executa a busca com os filtros aplicados
    produtos = query.all()

    # Devolve a página com os produtos e as variáveis de controle de filtro para manter o menu selecionado
    return templates.TemplateResponse("loja-user.html", {
        "request": request,
        "usuario": usuario,
        "produtos": produtos,
        "categoria_selecionada": categoria,
        "cor_selecionada": cor
    })

# Rota para listar único produto (Detalhes do produto)
@router.get('/produto/{id_produto}', response_class=HTMLResponse)
async def detalhe(request: Request, id_produto: int, db: Session = Depends(get_db), usuario: Usuario = Depends(obter_usuario_opcional)):
    # Busca especificamente o produto clicado pelo ID (Primary Key)
    produto = db.query(Produto).filter(Produto.id == id_produto).first()

    if produto.quantidade == 0:
        return RedirectResponse(url=f"/carrinho?erro=estoque_insuficiente&id={produto.id}", status_code=303)

    # Variável auxiliar vazia enviada para o front-end evitar erros no Jinja2
    carrinho = []

    return templates.TemplateResponse('produto.html', {
        'request': request,
        'produto': produto,
        'carrinho': carrinho,
        'usuario': usuario
    })


# ==========================================================
# ROTAS: ÁREA LOGADA DO USUÁRIO (PERFIL E PEDIDOS)
# ==========================================================

# ----- Dados do Usuário (Minha Conta) -----
@router.get("/me/dados", response_class=HTMLResponse)
def listar_dados(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):
    # Como a dependência 'usuario_logado' já barrou não-logados, basta renderizar a página
    return templates.TemplateResponse('perfil_user.html', {
        'request': request,
        'usuario': usuario
    })

# ----- Listar pedidos do usuário (Histórico de Compras) -----
@router.get("/meus-pedidos", response_class=HTMLResponse)
def meus_pedidos(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):
    
    # Extração e checagem manual extra do token (para redundância)
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    payload = verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=303)

    else:
        # Busca no banco apenas os pedidos que pertecem ao ID do usuário atual
        pedidos = db.query(Pedido).filter_by(id_usuario=usuario.id).all()

        # Faz um laço rápido para somar o valor total de todas as compras já feitas
        total_geral = sum(p.total for p in pedidos)

    return templates.TemplateResponse("checkout.html",
                                      {"request": request, 
                                       "pedidos": pedidos,
                                        "total_geral": total_geral,
                                        "usuario": usuario})


# ==========================================================
# ROTAS: CARRINHO DE COMPRAS
# ==========================================================

# Rota para visualizar a página do carrinho
@router.get("/carrinho", response_class=HTMLResponse)
async def ver_carrinho(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):
    # Pega a lista de produtos do carrinho daquele ID no dicionário. Se não existir, retorna lista vazia [].
    carrinho = carrinhos.get(usuario.id, [])

    return templates.TemplateResponse("carrinho.html", {
        "request": request,
        "carrinho": carrinho,
        "usuario": usuario
    })

# Rota para adicionar produto específico ao carrinho
@router.post("/carrinho/adicionar/{id_produto}")
async def adicionar_carrinho(
    request: Request,
    id_produto: int,
    quantidade: int = Form(1), # Recebe a quantidade por form, padrão é 1
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_logado)
):
    # Procura se o produto que ele quer adicionar realmente existe no banco
    produto = db.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        return RedirectResponse(url="/", status_code=303)

    # Recupera o carrinho atual
    carrinho = carrinhos.get(usuario.id, [])

    # Adiciona um novo dicionário com as informações estáticas do produto na lista do carrinho
    carrinho.append({
        "id": produto.id,
        "nome": produto.nome,
        "preco": float(produto.preco),
        "quantidade": quantidade,
        "imagem": produto.imagem,
        "categoria": produto.categoria
    })
    
    # Salva a lista atualizada de volta no dicionário global de carrinhos
    carrinhos[usuario.id] = carrinho  
    
    return RedirectResponse(url="/carrinho", status_code=303)

# Rota assíncrona para atualizar a quantidade (usada por requisições JS via Fetch/Axios)
@router.post("/carrinho/atualizar")
async def atualizar_quantidade(
    data: AtualizarCarrinho,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_logado)
):
    # Puxa o carrinho do usuário
    carrinho = carrinhos.get(usuario.id, [])

    # Procura na lista qual é o item correspondente e atualiza o valor "quantidade"
    for item in carrinho:
        if item["id"] == data.id_produto:
            item["quantidade"] = data.quantidade
            break # Encontrou, interrompe o loop por performance

    # Grava a mudança
    carrinhos[usuario.id] = carrinho

    # Retorna JSON confirmando a ação
    return {"status": "ok"}

# Rota para deletar o produto do carrinho
@router.post("/carrinho/remover/{id_produto}")
async def remover_carrinho(request: Request, id_produto: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):
    produto = db.query(Produto).filter(Produto.id == id_produto).first()

    carrinho = carrinhos.get(usuario.id, [])

    # List Comprehension: Recria a lista do carrinho, mantendo APENAS os itens cujo ID seja diferente do removido
    carrinho = [item for item in carrinho if item["id"] != id_produto]
    
    # Atualiza o dicionário global
    carrinhos[usuario.id] = carrinho
    
    return RedirectResponse(url="/carrinho", status_code=303)


# ==========================================================
# ROTAS: CHECKOUT E PAGAMENTO
# ==========================================================

# Rota para renderizar a página final antes da compra (Resumo financeiro)
@router.get("/pagamento", response_class=HTMLResponse)
async def pagamento(request: Request, db: Session = Depends(get_db), usuario: Usuario= Depends(usuario_logado)):
    
    # Busca o carrinho usando o ID do usuário validado
    carrinho = carrinhos.get(usuario.id, [])

    for item in carrinho:
        # puxa o produto no banco de dados pelo id
        produto_banco = db.query(Produto).filter(Produto.id == item['id']).first()

        # verifica se tem produto no banco de dados 
        # e se a quantidade do carrinho é maior do que tem no banco de dados    
        if not produto_banco or item['quantidade'] > produto_banco.quantidade:
            # Se deu ruim, manda o cliente de volta pro carrinho com um aviso na URL!
            return RedirectResponse(url=f"/carrinho?erro=estoque_insuficiente&id={item['id']}", status_code=303)

    # Faz o cálculo de subtotal: (Quantidade x Preço) de cada produto e soma tudo
    total_geral = sum(item['quantidade'] * item['preco'] for item in carrinho)

    return templates.TemplateResponse("pagamento.html", {
        "request": request,
        "carrinho": carrinho,
        "total": total_geral, 
        "usuario": usuario
    })

# Rota final para processar a "compra" de fato e gravar no banco
@router.post("/checkout")
async def checkout(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_logado)):

    carrinho = carrinhos.get(usuario.id, [])

    # Trava de segurança: Se tentar bater nessa rota com carrinho vazio, volta pra lá.
    if not carrinho:
        return RedirectResponse(url="/carrinho?erro=vazio", status_code=303)

    # Calcula o total 
    total = round(sum(item["preco"] * item["quantidade"] for item in carrinho), 2)

    # 1. Cria o registro principal do Pedido
    pedido = Pedido(id_usuario=usuario.id, total=total, prazo_entrega=15) # Prazo de 15 dias inserido!
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    # 2. Varre o carrinho e salva cada linha como um ItemPedido
    for item in carrinho:
        novo_item = ItemPedido(
            id_pedido=pedido.id,
            id_produto=item["id"],
            quantidade=item["quantidade"],
            preco_unitario=item["preco"]
        )
        db.add(novo_item)

        # --- BAIXA NO ESTOQUE AQUI ---
        # Busca o produto original no banco de dados para atualizar a prateleira
        produto_no_banco = db.query(Produto).filter(Produto.id == item["id"]).first()
        
        if produto_no_banco:
            # Subtrai a quantidade comprada da quantidade em estoque
            produto_no_banco.quantidade -= item["quantidade"]
            
            # (Opcional) Garante que o estoque não fique negativo caso dê algum bug
            if produto_no_banco.quantidade < 0:
                produto_no_banco.quantidade = 0
        # -----------------------------
        
    # Commita todos os itens e as alterações de estoque juntos!
    db.commit()
    
    # 3. Limpa o carrinho da memória
    carrinhos[usuario.id] = []
    
    # Redireciona o cliente
    return RedirectResponse(url="/meus-pedidos", status_code=303)


# ==========================================================
# ROTAS: PAINEL ADMINISTRATIVO
# ==========================================================

# ----- Dashboard Inicial de Estatísticas -----
@router.get("/admin/dados", response_class=HTMLResponse)
def listar_dados_admin(request: Request, db: Session = Depends(get_db), admin_user: Usuario = Depends(admin_requerido)):

    return templates.TemplateResponse('perfil_admin.html', {
        'request': request,
        'usuario': admin_user
    })

# ----- Página Estatísticas Administrativas (Admin.html) -----
@router.get("/admin")
def admin(request: Request, db: Session = Depends(get_db), admin_user: Usuario = Depends(admin_requerido)):

    # Realiza agregações no banco para popular os cards indicadores do painel
    numerosUsuarios = db.query(Usuario).count()
    numeroProdutos = db.query(Produto).count()
    total_acessos = db.query(Visita).count()

    return templates.TemplateResponse("admin.html", {"request": request, "usuario": admin_user, "usuarios": numerosUsuarios, "produtos": numeroProdutos, "acessos": total_acessos})

# ----- Página Editar Produto -----
@router.get('/admin/editar', response_class=HTMLResponse)
async def listar_produto_editar(request: Request, admin_user: Usuario = Depends(admin_requerido), db: Session = Depends(get_db)):

    # Busca a listagem de todos os produtos para mostrar na tabela
    produtos = db.query(Produto).all()

    return templates.TemplateResponse('admin_editar.html', {'request': request, 'usuario':admin_user, "produtos":produtos})

# ----- Página Formulário Editar Produto por ID -----
@router.get('/admin/editar/{id_produto}', response_class=HTMLResponse)
async def editar_id(request: Request, id_produto: int, admin_user: Usuario = Depends(admin_requerido), db:Session=Depends(get_db)):
    produto_selecionado = db.query(Produto).filter(Produto.id == id_produto).first()
    
    return templates.TemplateResponse('admin_editar_id.html', {'request': request, 'usuario':admin_user, "produto_existente":produto_selecionado})
    
# ----- Rota POST para Editar novo Produto no Banco e Discos -----
@router.post("/admin/editar/{id}")
def editar_produto(
    request: Request,
    id: int,
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    categoria: str = Form(...),
    cor: str = Form(...),
    imagem: UploadFile | None = File(None),   # Na edição imagens são sempre opcionais
    detalhe1: UploadFile | None = File(None),    
    detalhe2: UploadFile | None = File(None),
    detalhe3: UploadFile | None = File(None),
    detalhe4: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    # Buscar o produto no Banco de Dados
    produto_existente = db.query(Produto).filter(Produto.id == id).first()
    
    # Se alguém tentar editar um ID que não existe, manda de volta
    if not produto_existente:
        return RedirectResponse(url="/admin/produto?erro=produto_nao_encontrado", status_code=303)
    
    # Atualiza os dados de texto e números
    produto_existente.nome = nome
    produto_existente.preco = preco
    produto_existente.quantidade = quantidade
    produto_existente.categoria = categoria
    produto_existente.cor = cor
    
    # Função auxiliar para salvar somente a imagem se o admin tiver enviado uma nova
    def salvar_imagem_nova(arquivo_upload: UploadFile):
        if arquivo_upload and arquivo_upload.filename: # Se enviou um arquivo de verdade
            caminho = os.path.join(UPLOAD_DIR, arquivo_upload.filename)
            with open(caminho, "wb") as f:
                shutil.copyfileobj(arquivo_upload.file, f)
            return arquivo_upload.filename
        return None # Retorna None se não enviou nada 
    
    # Checa e atualiza cada imagem individualmente
    nova_imagem = salvar_imagem_nova(imagem)
    if nova_imagem:
        produto_existente.imagem = nova_imagem # Só substitui se mandou imagem nova

    nova_det1 = salvar_imagem_nova(detalhe1)
    if nova_det1:
        produto_existente.detalhe_1 = nova_det1

    nova_det2 = salvar_imagem_nova(detalhe2)
    if nova_det2:
        produto_existente.detalhe_2 = nova_det2

    nova_det3 = salvar_imagem_nova(detalhe3)
    if nova_det3:
        produto_existente.detalhe_3 = nova_det3

    nova_det4 = salvar_imagem_nova(detalhe4)
    if nova_det4:
        produto_existente.detalhe_4 = nova_det4
        
    # Salva as alterações (Como já buscamos no banco, só fazer commit)
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)

# ----- Página Formulário Criar Produto -----
@router.get('/admin/produto', response_class=HTMLResponse)
async def listar_admin(request: Request, admin_user: Usuario = Depends(admin_requerido)):

    return templates.TemplateResponse('admin-produto.html', {'request': request, 'usuario':admin_user})

# ----- Rota POST para Salvar novo Produto no Banco e Discos -----
@router.post("/admin/produto")
def criar_produto(
    request: Request,
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    categoria: str = Form(...),
    cor: str = Form(...),
    imagem: UploadFile = File(...),              # Imagem Principal (Obrigatória)
    detalhe1: UploadFile | None = File(None),    # Imagens Secundárias (Opcionais)
    detalhe2: UploadFile | None = File(None),
    detalhe3: UploadFile | None = File(None),
    detalhe4: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(admin_requerido)
):
        # Gera caminho completo no servidor para salvar a imagem principal com o nome original
        caminho_arquivo = os.path.join(UPLOAD_DIR, imagem.filename)

        # Escreve ("wb" -> write binary) fisicamente o arquivo na pasta "static/uploads"
        with open(caminho_arquivo, "wb") as arquivo:
            shutil.copyfileobj(imagem.file, arquivo)

        # Monta a estrutura no banco, passando os nomes das imagens (faz ternário se a opcional não existir)
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
        # Salva o produto
        db.add(novo_produto)
        db.commit()
        db.refresh(novo_produto)
        
        return RedirectResponse(url="/admin/produto", status_code=303)

# ----- Página Listagem de Produtos para Exclusão -----
@router.get('/admin/delete', response_class=HTMLResponse)
async def listar_admin_produto_deletar(request: Request, db: Session = Depends(get_db), admin_user: Usuario = Depends(admin_requerido)):
    # Busca a listagem de todos os produtos para mostrar na tabela
    produtos = db.query(Produto).all()

    return templates.TemplateResponse('admin-produto-deletar.html', {
        'request': request,
        'produtos': produtos,
        'usuario': admin_user
    })

# ----- Rota POST para Deletar Produto -----
@router.post("/admin/delete/{id}")
def deletar_produto(request: Request, id: int, db: Session = Depends(get_db), admin_user: Usuario = Depends(admin_requerido)):
        # Procura o produto específico pelo ID
        produto = db.query(Produto).filter(Produto.id == id).first()
        
        # Se ele existir, deleta e commita a alteração
        if produto:
            db.delete(produto)
            db.commit()
        return RedirectResponse(url="/admin/delete", status_code=303)           


# ==========================================================
# ROTAS: APIs EXTRAS E UTILITÁRIOS (FRETE / CONTADOR)
# ==========================================================

# Rota usada pelo JS para mostrar aquele balãozinho de "3 itens" no ícone do carrinho
@router.get("/api/contador-carrinho")
def contador_carrinho(db: Session = Depends(get_db), usuario: Usuario = Depends(obter_usuario_opcional)):
    
    # Se o usuário não está logado, ele tem 0 itens no carrinho logicamente
    if not usuario:
        return {"quantidade": 0}

    # Pegamos o carrinho atual do usuário no dicionário 'carrinhos'
    # Se não existir nada, retorna uma lista vazia []
    carrinho_atual = carrinhos.get(usuario.id, [])

    # Somamos a 'quantidade' estrita de cada item (se ele tiver 2 itens x 3 quantidades = 6 total)
    quantidade_total = sum(item["quantidade"] for item in carrinho_atual)

    return {"quantidade": quantidade_total}

# Rota de frete simulado consumindo a API Externa dos Correios (ViaCEP)
@router.get("/api/frete")
def calcular_frete(
    request: Request, cep_destino: str = Query(...)
):
    # token login obrigatório - Valida se a requisição está autorizada a usar a cota da API
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401,
                            detail="Usuário não autenticado")
                            
    # validação simples do cep (tem que ser número e ter exatamente 8 dígitos)
    if not cep_destino.isdigit() or len(cep_destino) != 8:
        raise HTTPException(status_code=400,
                            detail="CEP inválido")
                            
    # consulta externa no viacep usando f-string
    via_cep_url = f"https://viacep.com.br/ws/{cep_destino}/json/"
    resposta = requests.get(via_cep_url)
    
    # Caso a API Externa caia ou rejeite o acesso
    if resposta.status_code != 200:
        raise HTTPException(status_code=400,
                            detail="Erro ao consultar o CEP")
    
    dados = resposta.json()
    
    # O ViaCEP retorna um JSON com key "erro" caso o formato seja certo mas não exista no Brasil
    if "erro" in dados:
        raise HTTPException(status_code=400,
                            detail="CEP não encontrado")
                            
    # Simulação do frete (Atualmente com valores hardcoded/fixos para projeto escola)
    valor_frete = 15.00
    prazo_estimado = 5
    
    # Retorno estruturado JSON pronto para o front-end ler e imprimir na tela
    return {
        "endereco": f"{dados.get('logradouro')} - {dados.get('bairro')} - {dados.get('localidade')} - {dados.get('uf')}",
        "cep": cep_destino,
        "valor_frete": valor_frete,
        "prazo_estimado_dias": prazo_estimado,
        "status": "Simulação concluída"
    }

# ==========================================================
# ROTAS EM JSON (para o react Native)
# ==========================================================

#API Listar Produtos
@router.get("/api/produtos")
def listar_produtos(
    categoria: str | None = Query(None),
    cor: str | None = Query(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_opcional)
):

    query = db.query(Produto)

    if categoria:
        query = query.filter(Produto.categoria == categoria)

    if cor:
        query = query.filter(Produto.cor == cor)

    produtos = query.all()

    return [
        {
            "id": p.id,
            "nome": p.nome,
            "categoria": p.categoria,
            "cor": p.cor,
            "preco": p.preco,
            "imagem": p.imagem
        }
        for p in produtos
    ]
    
# Login
@router.post("/api/login")
async def api_login(dados: LoginSchema, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    
    if not usuario: 
        return JSONResponse({"mensagem": "Usuário não encontrado"}, status_code=401)
    
    try:
        if not verificar_senha(dados.senha, usuario.senha):
            return JSONResponse({"mensagem": "Senha incorreta."}, status_code=401)
    except Exception as e:
        return JSONResponse({"mensagem": "Erro interno."}, status_code=500)
    
    # Gera o token
    token_data = {"sub": usuario.email}
    if usuario.is_admin:
        token_data["is_admin"] = True
        
    token = criar_token(token_data)

    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": usuario.is_admin
    }
    
# Cadastro
@router.post('/api/register')
async def api_cadastrar(dados: CadastroSchema, db: Session = Depends(get_db)):
    try:
        usuario_existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
        if usuario_existente:
            return JSONResponse({'mensagem': 'E-mail já cadastrado'}, status_code=400)
        
        senha_hash = gerar_hash_senha(dados.senha)
        
        novo_usuario = Usuario(nome=dados.nome, email=dados.email, senha=senha_hash)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        return {"mensagem": "Usuário cadastrado com sucesso!"}
    
    except Exception as e:
        print("ERRO BACKEND:", e)
        return JSONResponse({'mensagem': 'Erro interno', 'erro': str(e)}, status_code=500)
# @router.post('/api/register')
# async def api_cadastrar(dados: CadastroSchema, db: Session = Depends(get_db)):
#     # Verifica se já existe
#     usuario_existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
#     if usuario_existente:
#         return JSONResponse({'mensagem': 'E-mail já cadastrado'}, status_code=400)
    
#     senha_hash = gerar_hash_senha(dados.senha)
    
#     novo_usuario = Usuario(nome=dados.nome, email=dados.email, senha=senha_hash)
#     db.add(novo_usuario)
#     db.commit()
#     db.refresh(novo_usuario)
    
#     # Retorna sucesso para o app saber que pode ir para a tela de login
#     return {"mensagem": "Usuário cadastrado com sucesso!"}
