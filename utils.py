import os
import sys
import io
import pandas as pd
from functools import wraps
from flask import session, redirect, url_for, send_file

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

PERFIS = {
    'DEVELOPER': {'full_access'},
    'SUPERVISOR': {
        'ver_dashboard', 'ver_menu_cadastros', 'ver_menu_relatorios',
        'conceder_acesso', 'excluir_registro', 'registrar_frequencia',
        'cadastrar_grm', 'registrar_evento', 'registrar_convertido',
        'cadastrar_supervisor', 'cadastrar_lider', 'cadastrar_colider',
        'cadastrar_lider_treinamento', 'cadastrar_membro', 'cadastrar_visitante',
        'analise_frequencia', 'ver_historico_ofertas', 'analise_menu'
    },
    'LIDER': {
        'ver_dashboard', 'ver_menu_cadastros', 'ver_menu_relatorios', 'registrar_frequencia',
        'cadastrar_colider', 'cadastrar_lider_treinamento', 'cadastrar_membro',
        'cadastrar_visitante', 'registrar_evento', 'registrar_convertido',
    },
    'COLIDER': {
        'ver_dashboard', 'ver_menu_relatorios', 'cadastrar_visitante',
        'registrar_evento', 'registrar_convertido', 'registrar_frequencia',
    },
    'MEMBRO': {
        'ver_dashboard', 'ver_menu_relatorios', 'cadastrar_visitante',
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def exportar_dataframe_excel(df, nome_aba, nome_arquivo):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nome_aba, index=False)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=nome_arquivo
    )
