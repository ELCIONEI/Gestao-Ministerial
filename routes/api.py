from flask import render_template, request, redirect, url_for, session, jsonify, flash
from database import db
from utils import login_required

LABELS_PERMITIDAS = {
    'supervisor': ('Supervisor', 'nome'),
    'lider': ('Lider', 'nome'),
    'colider': ('Colider', 'nome'),
    'membro': ('Membro', 'nome'),
    'grm': ('GRM', 'nome_grm')
}

def registrar_rotas(app):
    @app.route('/excluir_registro')
    @login_required
    def excluir_registro():
        if session['perfil'] not in ['SUPERVISOR', 'DEVELOPER']:
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect(url_for('dashboard'))
        return render_template('excluir_registro.html')

    @app.route('/api/search/<string:tipo_registro>')
    @login_required
    def api_search(tipo_registro):
        termo = request.args.get('q', '').strip()
        if not termo:
            return jsonify([])
        info = LABELS_PERMITIDAS.get(tipo_registro)
        if not info:
            return jsonify({'error': 'Tipo de registro inválido'}), 400
        label, campo = info
        try:
            resultados = db.executar(f"""
                MATCH (n:{label})
                WHERE toLower(n.{campo}) CONTAINS toLower($q)
                RETURN COALESCE(n.id, n.id_mysql, elementId(n)) AS id, n.{campo} AS nome
                ORDER BY nome LIMIT 20
            """, {"q": termo})
            return jsonify(resultados)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/details/<string:tipo_registro>/<item_id>')
    @login_required
    def api_details(tipo_registro, item_id):
        info = LABELS_PERMITIDAS.get(tipo_registro)
        if not info:
            return jsonify({'error': 'Tipo de registro inválido'}), 400
        label, _ = info
        try:
            res = db.executar_um(f"""
                MATCH (n:{label})
                WHERE toString(n.id) = $id OR toString(n.id_mysql) = $id OR elementId(n) = $id
                RETURN properties(n) AS props
            """, {"id": str(item_id)})
            return jsonify(res['props'] if res else {})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/delete/<string:tipo_registro>/<item_id>', methods=['DELETE'])
    @login_required
    def api_delete(tipo_registro, item_id):
        if session['perfil'] not in ['SUPERVISOR', 'DEVELOPER']:
            return jsonify({'error': 'Permissão negada'}), 403
        info = LABELS_PERMITIDAS.get(tipo_registro)
        if not info:
            return jsonify({'error': 'Tipo de registro inválido'}), 400
        label, _ = info
        try:
            db.executar(f"""
                MATCH (n:{label})
                WHERE toString(n.id) = $id OR toString(n.id_mysql) = $id OR elementId(n) = $id
                DETACH DELETE n
            """, {"id": str(item_id)})
            return jsonify({'success': True, 'message': 'Registro excluído com sucesso!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao excluir: {e}'}), 500
