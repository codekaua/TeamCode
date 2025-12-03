from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql+psycopg2://postgres:dev1t%4024@db.gpszbdtzifhrvejsxvsi.supabase.co:5432/postgres"

def get_engine_session():
    try:
        # Cria engine para PostgreSQL remoto (Supabase)
        engine = create_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True  # evita erros de conexão fechada
        )

        # Testa conexão
        conn = engine.connect()
        conn.close()

        SessionLocal = sessionmaker(
            bind=engine, autoflush=False, autocommit=False
        )
        return engine, SessionLocal
    except SQLAlchemyError as e:
        print("Falha ao conectar ao banco de dados PostgreSQL!")
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
