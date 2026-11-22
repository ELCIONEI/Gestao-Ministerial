import pandas as pd
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash
from database import db
from utils import PERFIS, login_required, exportar_dataframe_excel


def _listar_regioes():
    return db.executar("""
        MATCH (g:GRM) OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
        RETURN DISTINCT COALESCE(g.regiao, r.nome) AS regiao ORDER BY regiao
    """)


def _listar_grms():
    return db.executar("MATCH (g:GRM) RETURN COALESCE(g.id, g.id_mysql) AS id, g.nome_grm AS nome_grm ORDER BY g.nome_grm")


def _intervalo_periodo(periodo):
    hoje = datetime.now().date()
    ano = hoje.year

    if periodo == 'bimestre1':
        return f"{ano}-01-01", f"{ano}-02-29"
    if periodo == 'semestre1':
        return f"{ano}-01-01", f"{ano}-06-30"
    if periodo == 'ano_atual':
        return f"{ano}-01-01", f"{ano}-12-31"
    if periodo == 'ano_anterior':
        return f"{ano - 1}-01-01", f"{ano - 1}-12-31"
    if periodo == 'bimestre':
        return (hoje - timedelta(days=60)).strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d')
    if periodo == 'semestre':
        return (hoje - timedelta(days=180)).strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d')
    if periodo == 'ano':
        return (hoje - timedelta(days=365)).strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d')
    return "", ""


def registrar_rotas(app):
    @app.route('/analise_menu')
    @login_required
    def analise_menu():
        if session['perfil'] not in ['DEVELOPER', 'SUPERVISOR']:
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect(url_for('dashboard'))
        return render_template('analise_menu.html', PERFIS=PERFIS, perfil_usuario=session.get('perfil'))

    @app.route('/analise/grms/filtros')
    @login_required
    def analise_grms_filtros():
        if session['perfil'] not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        return render_template('analise_grms_filtros.html', regioes=_listar_regioes())

    @app.route('/analise/grms')
    @login_required
    def analise_grms():
        if session['perfil'] not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        regiao = request.args.get('regiao', 'todas')
        dados = db.executar("""
            MATCH (g:GRM) OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
            WITH g, COALESCE(g.regiao, r.nome) AS reg
            WHERE $regiao = 'todas' OR reg = $regiao
            RETURN reg AS `Região`, count(g) AS `Total de GRMs`
            ORDER BY reg
        """, {"regiao": regiao})
        return exportar_dataframe_excel(pd.DataFrame(dados), 'Analise_GRMs', f'analise_grms_{regiao}.xlsx')

    @app.route('/analise/conversoes/filtros')
    @login_required
    def analise_conversoes_filtros():
        if session['perfil'] not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        return render_template('analise_conversoes_filtros.html', regioes=_listar_regioes(), grms=_listar_grms())

    @app.route('/analise/conversoes')
    @login_required
    def analise_conversoes():
        if session.get('perfil', '').strip() not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        periodo = request.args.get('periodo', 'geral')
        regiao = request.args.get('regiao', 'todas')
        grm_id = request.args.get('grm_id', 'todos')
        data_inicio, data_fim = _intervalo_periodo(periodo)

        dados = db.executar("""
            MATCH (cv:Convertido)-[:ACEITOU_EM|CONVERTEU_NO]->(ev:Evento)-[:REALIZOU|REALIZADO_NO]-(g:GRM)
            OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
            WITH cv, g, COALESCE(g.regiao, r.nome) AS reg, toString(cv.data_conversao) AS dt
            WHERE ($regiao = 'todas' OR reg = $regiao)
              AND ($grm_id = 'todos' OR toString(g.id) = $grm_id OR toString(g.id_mysql) = $grm_id)
              AND ($inicio = '' OR (dt >= $inicio AND dt <= $fim))
            RETURN cv.nome AS `Nome do Convertido`, cv.data_conversao AS `Data da Conversão`,
                   g.nome_grm AS `GRM de Origem`, reg AS `Região`
            ORDER BY cv.data_conversao DESC
        """, {"regiao": regiao, "grm_id": str(grm_id), "inicio": data_inicio, "fim": data_fim})
        return exportar_dataframe_excel(pd.DataFrame(dados), 'Analise_Conversoes', 'analise_conversoes.xlsx')

    @app.route('/analise/membros/filtros')
    @login_required
    def analise_membros_filtros():
        if session.get('perfil', '').strip() not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        return render_template('analise_membros_filtros.html', regioes=_listar_regioes(), grms=_listar_grms())

    @app.route('/analise/membros')
    @login_required
    def analise_membros():
        if session.get('perfil', '').strip() not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        nome = request.args.get('nome_membro', '').strip()
        periodo = request.args.get('periodo', 'todos')
        regiao = request.args.get('regiao', 'todas')
        grm_id = request.args.get('grm_id', 'todos')
        data_inicio, data_fim = _intervalo_periodo(periodo)

        dados = db.executar("""
            MATCH (m:Membro)
            OPTIONAL MATCH (m)-[:PARTICIPA_DE|PERTENCE_AO]-(g:GRM)
            OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
            WITH m, g, COALESCE(g.regiao, r.nome) AS reg, toString(m.data_cadastro) AS dt
            WHERE ($nome = '' OR toLower(m.nome) CONTAINS toLower($nome))
              AND ($inicio = '' OR (dt >= $inicio AND dt <= $fim))
              AND ($regiao = 'todas' OR reg = $regiao)
              AND ($grm_id = 'todos' OR toString(g.id) = $grm_id OR toString(g.id_mysql) = $grm_id)
            RETURN DISTINCT m.nome AS `Nome`, m.email AS `E-mail`, m.telefone AS `Telefone`, m.data_cadastro AS `Data Cadastro`
            ORDER BY m.nome
        """, {"nome": nome, "inicio": data_inicio, "fim": data_fim, "regiao": regiao, "grm_id": str(grm_id)})
        return exportar_dataframe_excel(pd.DataFrame(dados), 'Analise_Membros', 'analise_membros.xlsx')

    @app.route('/analise/lideranca/filtros')
    @login_required
    def analise_lideranca_filtros():
        if session.get('perfil', '').strip() not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        return render_template('analise_lideranca_filtros.html', regioes=_listar_regioes())

    @app.route('/analise/lideranca')
    @login_required
    def analise_lideranca():
        if session.get('perfil', '').strip() not in ['DEVELOPER', 'SUPERVISOR']:
            return redirect(url_for('analise_menu'))
        cargo = request.args.get('cargo', 'todos')
        periodo = request.args.get('periodo', 'total')
        regiao = request.args.get('regiao', 'todas')
        data_inicio, data_fim = _intervalo_periodo(periodo)

        mapa_cargo = {
            'supervisores': 'Supervisor',
            'lideres': 'Lider',
            'colideres': 'Colider'
        }
        label_alvo = mapa_cargo.get(cargo, 'todos')

        dados = db.executar("""
            MATCH (n) WHERE n:Supervisor OR n:Lider OR n:Colider
            OPTIONAL MATCH (n)-[:DIRIGE|GERENCIA|SUPERVISIONA]-(g:GRM)
            OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
            WITH n, labels(n)[0] AS cargo_no, COALESCE(g.regiao, r.nome) AS reg, toString(n.data_cadastro) AS dt
            WHERE ($label = 'todos' OR cargo_no = $label)
              AND ($inicio = '' OR (dt >= $inicio AND dt <= $fim))
              AND ($regiao = 'todas' OR reg = $regiao)
            RETURN DISTINCT n.nome AS `Nome`, n.email AS `E-mail`, cargo_no AS `Cargo`, n.data_cadastro AS `Data Cadastro`
            ORDER BY `Cargo`, `Nome`
        """, {"label": label_alvo, "inicio": data_inicio, "fim": data_fim, "regiao": regiao})
        return exportar_dataframe_excel(pd.DataFrame(dados), 'Analise_Lideranca', 'analise_lideranca.xlsx')