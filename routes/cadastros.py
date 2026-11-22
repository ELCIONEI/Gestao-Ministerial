import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for
from database import db
from utils import login_required

def _novo_id():
    return str(uuid.uuid4())[:8]

def registrar_rotas(app):
    @app.route('/cad_supervisor', methods=['GET', 'POST'])
    @login_required
    def cad_supervisor():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (s:Supervisor {
                        id: $id, nome: $nome, endereco: $endereco, email: $email,
                        data_nascimento: $data_nascimento, telefone: $telefone,
                        funcao_ministerial: $funcao_ministerial, data_cadastro: $data_cadastro
                    })
                    WITH s
                    OPTIONAL MATCH (m:Ministerio)
                    FOREACH (_ IN CASE WHEN m IS NOT NULL THEN [1] ELSE [] END | MERGE (m)-[:SUPERVISIONADO_POR]->(s))
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "endereco": request.form['endereco'],
                    "email": request.form['email'], "data_nascimento": request.form['data_nascimento'],
                    "telefone": request.form['telefone'], "funcao_ministerial": request.form['funcao_ministerial'],
                    "data_cadastro": datetime.now().strftime('%Y-%m-%d')
                })
                return redirect(url_for('cad_supervisor', success=True))
            except Exception as e:
                return f"Erro ao inserir supervisor: {e}"
        return render_template('cad_supervisor.html')

    @app.route('/cad_lider', methods=['GET', 'POST'])
    @login_required
    def cad_lider():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (l:Lider {
                        id: $id, nome: $nome, endereco: $endereco, email: $email,
                        data_nascimento: $data_nascimento, telefone: $telefone,
                        funcao_ministerial: $funcao_ministerial, data_cadastro: $data_cadastro
                    })
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "endereco": request.form['endereco'],
                    "email": request.form['email'], "data_nascimento": request.form['data_nascimento'],
                    "telefone": request.form['telefone'], "funcao_ministerial": request.form['funcao_ministerial'],
                    "data_cadastro": datetime.now().strftime('%Y-%m-%d')
                })
                return redirect(url_for('cad_lider', success=True))
            except Exception as e:
                return f"Erro ao inserir líder: {e}"
        return render_template('cad_lider.html')

    @app.route('/cad_colider', methods=['GET', 'POST'])
    @login_required
    def cad_colider():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (c:Colider {
                        id: $id, nome: $nome, endereco: $endereco, email: $email,
                        data_nascimento: $data_nascimento, telefone: $telefone,
                        funcao_ministerial: $funcao_ministerial, data_cadastro: $data_cadastro
                    })
                    WITH c
                    OPTIONAL MATCH (l:Lider)
                    WHERE toString(l.id) = $id_lider OR toString(l.id_mysql) = $id_lider
                    FOREACH (_ IN CASE WHEN l IS NOT NULL THEN [1] ELSE [] END | MERGE (c)-[:AUXILIA]->(l))
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "endereco": request.form['endereco'],
                    "email": request.form['email'], "data_nascimento": request.form['data_nascimento'],
                    "telefone": request.form['telefone'], "id_lider": str(request.form['id_lider_imediato']),
                    "funcao_ministerial": request.form['funcao_ministerial'],
                    "data_cadastro": datetime.now().strftime('%Y-%m-%d')
                })
                return redirect(url_for('cad_colider', success=True))
            except Exception as e:
                return f"Erro ao inserir co-líder: {e}"

        lideres = db.executar("MATCH (l:Lider) RETURN COALESCE(l.id, l.id_mysql) AS id, l.nome AS nome ORDER BY l.nome")
        return render_template('cad_colider.html', lideres=lideres)

    @app.route('/cad_lider_treinamento', methods=['GET', 'POST'])
    @login_required
    def cad_lider_treinamento():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (lt:LiderTreinamento {
                        id: $id, nome: $nome, email: $email, data_nascimento: $data_nascimento,
                        telefone: $telefone, funcao_ministerial: $funcao_ministerial
                    })
                    WITH lt
                    OPTIONAL MATCH (l:Lider) WHERE toString(l.id) = $id_lider OR toString(l.id_mysql) = $id_lider
                    OPTIONAL MATCH (c:Colider) WHERE toString(c.id) = $id_colider OR toString(c.id_mysql) = $id_colider
                    FOREACH (_ IN CASE WHEN l IS NOT NULL THEN [1] ELSE [] END | MERGE (lt)-[:TREINADO_POR]->(l))
                    FOREACH (_ IN CASE WHEN c IS NOT NULL THEN [1] ELSE [] END | MERGE (lt)-[:AUXILIADO_POR]->(c))
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "email": request.form['email'],
                    "data_nascimento": request.form['data_nascimento'], "telefone": request.form['telefone'],
                    "id_lider": str(request.form['id_lider']), "id_colider": str(request.form['id_colider']),
                    "funcao_ministerial": request.form['funcao_ministerial']
                })
                return redirect(url_for('cad_lider_treinamento', success=True))
            except Exception as e:
                return f"Erro ao inserir líder em treinamento: {e}"

        lideres = db.executar("MATCH (l:Lider) RETURN COALESCE(l.id, l.id_mysql) AS id, l.nome AS nome ORDER BY l.nome")
        colideres = db.executar("MATCH (c:Colider) RETURN COALESCE(c.id, c.id_mysql) AS id, c.nome AS nome ORDER BY c.nome")
        return render_template('cad_lider_treinamento.html', lideres=lideres, colideres=colideres)

    @app.route('/cad_membro', methods=['GET', 'POST'])
    @login_required
    def cad_membro():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (m:Membro {
                        id: $id, nome: $nome, endereco: $endereco, email: $email,
                        data_nascimento: $data_nascimento, telefone: $telefone,
                        novo_convertido: toInteger($novo_convertido),
                        membro_outro_ministerio: toInteger($membro_outro_ministerio),
                        outra_religiao: toInteger($outra_religiao),
                        nao_professa_fe: toInteger($nao_professa_fe),
                        data_cadastro: $data_cadastro
                    })
                    WITH m
                    OPTIONAL MATCH (min:Ministerio)
                    FOREACH (_ IN CASE WHEN min IS NOT NULL THEN [1] ELSE [] END | MERGE (m)-[:PERTENCE_AO]->(min))
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "endereco": request.form['endereco'],
                    "email": request.form['email'], "data_nascimento": request.form['data_nascimento'],
                    "telefone": request.form['telefone'], "novo_convertido": request.form['novo_convertido'],
                    "membro_outro_ministerio": request.form['membro_outro_ministerio'],
                    "outra_religiao": request.form['outra_religiao'], "nao_professa_fe": request.form['nao_professa_fe'],
                    "data_cadastro": datetime.now().strftime('%Y-%m-%d')
                })
                return redirect(url_for('cad_membro', success=True))
            except Exception as e:
                return f"Erro ao inserir membro: {e}"
        return render_template('cad_membro.html')

    @app.route('/cad_visitante', methods=['GET', 'POST'])
    @login_required
    def cad_visitante():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (v:Visitante {
                        id: $id, nome: $nome, endereco: $endereco, email: $email,
                        data_nascimento: $data_nascimento, telefone: $telefone,
                        membro_outro_ministerio: toInteger($membro_outro_ministerio),
                        nome_ministerio: $nome_ministerio,
                        outra_religiao: toInteger($outra_religiao)
                    })
                    WITH v
                    OPTIONAL MATCH (min:Ministerio)
                    FOREACH (_ IN CASE WHEN min IS NOT NULL THEN [1] ELSE [] END | MERGE (v)-[:VISITOU]->(min))
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "endereco": request.form['endereco'],
                    "email": request.form['email'], "data_nascimento": request.form['data_nascimento'],
                    "telefone": request.form['telefone'], "membro_outro_ministerio": request.form['membro_outro_ministerio'],
                    "nome_ministerio": request.form.get('nome_ministerio'), "outra_religiao": request.form['outra_religiao']
                })
                return redirect(url_for('cad_visitante', success=True))
            except Exception as e:
                return f"Erro ao inserir visitante: {e}"
        return render_template('cad_visitante.html')

    @app.route('/cad_grm', methods=['GET', 'POST'])
    @login_required
    def cad_grm():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (g:GRM {id: $id, nome_grm: $nome_grm, regiao: $regiao, data_criacao: $data_criacao})
                    WITH g
                    MERGE (r:Regiao {nome: $regiao})
                    MERGE (r)-[:ABRIGA]->(g)
                    WITH g
                    OPTIONAL MATCH (l:Lider) WHERE toString(l.id) = $id_lider OR toString(l.id_mysql) = $id_lider
                    OPTIONAL MATCH (c:Colider) WHERE toString(c.id) = $id_colider OR toString(c.id_mysql) = $id_colider
                    OPTIONAL MATCH (lt:LiderTreinamento) WHERE toString(lt.id) = $id_lt OR toString(lt.id_mysql) = $id_lt
                    FOREACH (_ IN CASE WHEN l IS NOT NULL THEN [1] ELSE [] END | MERGE (l)-[:DIRIGE]->(g))
                    FOREACH (_ IN CASE WHEN c IS NOT NULL THEN [1] ELSE [] END | MERGE (c)-[:GERENCIA]->(g))
                    FOREACH (_ IN CASE WHEN lt IS NOT NULL THEN [1] ELSE [] END | MERGE (lt)-[:TREINA_EM]->(g))
                """, {
                    "id": _novo_id(), "nome_grm": request.form['nome_grm'], "regiao": request.form['regiao'],
                    "id_lider": str(request.form['id_lider']), "id_colider": str(request.form['id_colider']),
                    "id_lt": str(request.form['id_lider_treinamento']),
                    "data_criacao": datetime.now().strftime('%Y-%m-%d')
                })
                return redirect(url_for('cad_grm', success=True))
            except Exception as e:
                return f"Erro ao registrar GRM: {e}"

        lideres = db.executar("MATCH (l:Lider) RETURN COALESCE(l.id, l.id_mysql) AS id, l.nome AS nome ORDER BY l.nome")
        colideres = db.executar("MATCH (c:Colider) RETURN COALESCE(c.id, c.id_mysql) AS id, c.nome AS nome ORDER BY c.nome")
        lideres_t = db.executar("MATCH (lt:LiderTreinamento) RETURN COALESCE(lt.id, lt.id_mysql) AS id, lt.nome AS nome ORDER BY lt.nome")
        return render_template('cad_grm.html', lideres=lideres, colideres=colideres, lideres_em_treinamento=lideres_t)

    @app.route('/cad_evento', methods=['GET', 'POST'])
    @login_required
    def cad_evento():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (e:Evento {
                        id: $id, participantes: toInteger($participantes),
                        valor_ofertas: toFloat($valor_ofertas), ofertas: toFloat($valor_ofertas),
                        data_evento: $data_evento, data: $data_evento
                    })
                    WITH e
                    OPTIONAL MATCH (g:GRM) WHERE toString(g.id) = $id_grm OR toString(g.id_mysql) = $id_grm
                    OPTIONAL MATCH (l:Lider) WHERE toString(l.id) = $id_lider OR toString(l.id_mysql) = $id_lider
                    OPTIONAL MATCH (c:Colider) WHERE toString(c.id) = $id_colider OR toString(c.id_mysql) = $id_colider
                    FOREACH (_ IN CASE WHEN g IS NOT NULL THEN [1] ELSE [] END | MERGE (g)-[:REALIZOU]->(e))
                    FOREACH (_ IN CASE WHEN l IS NOT NULL THEN [1] ELSE [] END | MERGE (l)-[:RESPONSAVEL_POR]->(e))
                    FOREACH (_ IN CASE WHEN c IS NOT NULL THEN [1] ELSE [] END | MERGE (c)-[:APOIOU]->(e))
                """, {
                    "id": _novo_id(), "id_grm": str(request.form['id_grm']),
                    "id_lider": str(request.form.get('id_lider_responsavel') or ''),
                    "id_colider": str(request.form.get('id_colider_responsavel') or ''),
                    "participantes": request.form['participantes'],
                    "valor_ofertas": str(request.form['valor_ofertas']).replace(',', '.'),
                    "data_evento": request.form['data_evento']
                })
                return redirect(url_for('cad_evento', success=True))
            except Exception as e:
                return f"Erro ao registrar evento: {e}"

        grms = db.executar("MATCH (g:GRM) OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g) RETURN COALESCE(g.id, g.id_mysql) AS id, g.nome_grm AS nome_grm, COALESCE(g.regiao, r.nome) AS regiao ORDER BY g.nome_grm")
        lideres = db.executar("MATCH (l:Lider) RETURN COALESCE(l.id, l.id_mysql) AS id, l.nome AS nome ORDER BY l.nome")
        colideres = db.executar("MATCH (c:Colider) RETURN COALESCE(c.id, c.id_mysql) AS id, c.nome AS nome ORDER BY c.nome")
        return render_template('cad_evento.html', grms=grms, lideres=lideres, colideres=colideres)

    @app.route('/cad_convertido', methods=['GET', 'POST'])
    @login_required
    def cad_convertido():
        if request.method == 'POST':
            try:
                db.executar("""
                    CREATE (cv:Convertido {
                        id: $id, nome: $nome, telefone: $telefone,
                        data_conversao: $data_conversao, observacoes: $observacoes
                    })
                    WITH cv
                    OPTIONAL MATCH (e:Evento) WHERE toString(e.id) = $id_evento OR toString(e.id_mysql) = $id_evento
                    FOREACH (_ IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END | MERGE (cv)-[:ACEITOU_EM]->(e))
                """, {
                    "id": _novo_id(), "nome": request.form['nome'], "telefone": request.form['telefone'],
                    "id_evento": str(request.form['id_evento']), "data_conversao": request.form['data_conversao'],
                    "observacoes": request.form.get('observacoes', '')
                })
                return redirect(url_for('cad_convertido', success=True))
            except Exception as e:
                return f"Erro ao registrar convertido: {e}"

        eventos = db.executar("""
            MATCH (g:GRM)-[:REALIZOU|REALIZADO_NO]-(e:Evento)
            RETURN COALESCE(e.id, e.id_mysql) AS id, COALESCE(e.data_evento, e.data) AS data_evento, g.nome_grm AS nome_grm
            ORDER BY data_evento DESC
        """)
        return render_template('cad_convertido.html', eventos=eventos)
