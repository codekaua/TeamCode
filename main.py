from fastapi import FastAPI
from controllers import router
from fastapi.staticfiles import StaticFiles # Montar pasta de imagem

app = FastAPI(title='MVC Produtos')
app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(router)

# pip install -r requirements.txt -> instala todas as dependências do projeto