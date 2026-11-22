import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask
from utils import resource_path
from database import db
from routes import auth, cadastros, relatorios, analises, api

load_dotenv()

app = Flask(
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static')
)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_padrao_dev')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Registra todos os módulos de rotas
auth.registrar_rotas(app)
cadastros.registrar_rotas(app)
relatorios.registrar_rotas(app)
analises.registrar_rotas(app)
api.registrar_rotas(app)

if __name__ == '__main__':
    db.setup_initial_admin()
    app.run(debug=True)
