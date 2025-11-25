from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Criar engine e session para SQLite
def get_engine_session():
    try:
        database = "ecommerce.db"  # arquivo do banco SQLite

        # Cria engine para SQLite
        engine = create_engine(f"sqlite:///{database}", echo=True)

        # Testa conexão
        conn = engine.connect()
        conn.close()

        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        return engine, SessionLocal
    except SQLAlchemyError as e:
        print("Falha ao conectar ao banco de dados SQLite!")
        print(f"Erro: {e}")
        return None, None

# Obter engine e SessionLocal
engine, SessionLocal = get_engine_session()

# Classe base para os models
Base = declarative_base()

# Função para dependência no FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# criar banco de dados 
# Base.metadata.create_all(engine)