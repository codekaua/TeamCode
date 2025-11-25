#pip install python-jose passlib
# pip install bcrypt==4.0.1
from datetime import datetime, timedelta
#datetime = ano, mês, dia, hora, minuto, segundo
#timedelta = adição ou subtração de tempo ou data
from jose import JWSError, jwt, ExpiredSignatureError
#JWTError = erro de criptografia
#jwt = JSON web token = Assinatura criptografada entre duas partes
from passlib.context import CryptContext
#implementação de contexto de criptografia, verificar o hash da senha

#criar a chave secreta do token(em produção guardar em uma variável de ambiente)
SECRET_KEY = 'chave-secreta'
ALGORITHM = 'HS256' #Algoritmo de criptografia de 256 bits que vai criar um hash, a mesma chave é usada para assinar o jwt e verificaar a assinatura do cliente
ACCESS_TOKEN_MINUTES = 30 #Token de 30 minutos

#Criptografia de senha
pwd_context = CryptContext(schemes=['argon2'], deprecated = 'auto')

#Função criar o hash da senha
def gerar_hash_senha(senha:str):
    return pwd_context.hash(senha)

#Verificar senha
def verificar_senha(senha:str, senha_hash:str):
    return pwd_context.verify(senha, senha_hash)

#Criar token
def criar_token(dados:dict):
    dados_token = dados.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    dados_token.update({'exp':expira})
    token_jwt = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

#Verificar token payload = carga útil
def verificar_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWSError:
        return None