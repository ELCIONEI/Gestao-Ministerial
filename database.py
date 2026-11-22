import os
import json
from datetime import datetime
from dotenv import load_dotenv
from neo4j import GraphDatabase
from werkzeug.security import generate_password_hash
from utils import resource_path

load_dotenv()

CAMPOS_DATA = {'data_evento', 'data_conversao', 'data_nascimento', 'data_cadastro', 'data'}

def _converter_datas(registro):
    for k, v in registro.items():
        if k in CAMPOS_DATA and isinstance(v, str) and v.strip():
            texto = v.strip()[:10]
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    registro[k] = datetime.strptime(texto, fmt).date()
                    break
                except ValueError:
                    continue
        elif isinstance(v, dict):
            _converter_datas(v)
    return registro

class ConexaoNeo4j:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def executar(self, query, params=None):
        with self.driver.session() as session_db:
            resultado = session_db.run(query, params or {})
            return [_converter_datas(r.data()) for r in resultado]

    def executar_um(self, query, params=None):
        with self.driver.session() as session_db:
            resultado = session_db.run(query, params or {})
            registro = resultado.single()
            return _converter_datas(registro.data()) if registro else None

    def setup_initial_admin(self):
        json_path = resource_path('setup_admin.json')
        if not os.path.exists(json_path):
            return
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)

            query = """
            MERGE (u:Usuario {username: $username})
            ON CREATE SET 
                u.nome = $nome,
                u.email = $email,
                u.senha = $senha,
                u.perfil = $perfil,
                u.force_password_change = false
            RETURN u
            """
            self.executar(query, {
                "username": admin_data['admin_username'],
                "nome": admin_data['admin_nome'],
                "email": admin_data['admin_email'],
                "senha": generate_password_hash(admin_data['admin_senha']),
                "perfil": admin_data['admin_perfil']
            })
            print(f"Administrador ({admin_data['admin_username']}) verificado no Neo4j.")
        except Exception as e:
            print(f"Erro ao configurar administrador inicial: {e}")

db = ConexaoNeo4j()
