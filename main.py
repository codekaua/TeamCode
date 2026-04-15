from fastapi import FastAPI, Request
# from Model.conexaoDB import SessionLocal
# from models import Visita
from controllers import router
from fastapi.staticfiles import StaticFiles # Montar pasta de imagem
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='MVC Produtos')
app.mount('/static', StaticFiles(directory='static'), name='static')

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://team-code-7jpa-kauarprodrigues-5332s-projects.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# pip install -r requirements.txt -> instala todas as dependências do projeto