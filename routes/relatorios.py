import pandas as pd
from flask import render_template, redirect, url_for, session, flash
from database import db
from utils import login_required, exportar_dataframe_excel

def registrar_rotas(app):
    @app.route('/relatorios')
    @login_required
    def relatorios():
        return render_template('menu_relatorios.html')

    @app.route('/relatorio/grms')
    @login_required
    def relatorio_grms():
        try:
            grms = db.executar("""
                MATCH (g:GRM)
                OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
                OPTIONAL MATCH (l:Lider)-[:DIRIGE|LIDERA]->(g)
                OPTIONAL MATCH (c:Colider)-[:GERENCIA|COLIDERA]->(g)
                OPTIONAL MATCH (lt:LiderTreinamento)-[:TREINA_EM|EM_TREINAMENTO_NO]->(g)
                RETURN COALESCE(g.id, g.id_mysql) AS id, g.nome_grm AS nome_grm,
                       COALESCE(g.regiao, r.nome) AS regiao, l.nome AS nome_lider,
                       c.nome AS nome_colider, lt.nome AS nome_lider_treinamento
                ORDER BY g.nome_grm ASC
            """)
            return render_template('relatorio_grms.html', grms=grms)
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/grms_excel')
    @login_required
    def exportar_grms_excel():
        try:
            dados = db.executar("""
                MATCH (g:GRM)
                OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
                OPTIONAL MATCH (l:Lider)-[:DIRIGE|LIDERA]->(g)
                OPTIONAL MATCH (c:Colider)-[:GERENCIA|COLIDERA]->(g)
                OPTIONAL MATCH (lt:LiderTreinamento)-[:TREINA_EM|EM_TREINAMENTO_NO]->(g)
                RETURN g.nome_grm AS `Nome do GRM`, COALESCE(g.regiao, r.nome) AS `Região`,
                       l.nome AS `Líder`, c.nome AS `Co-líder`, lt.nome AS `Líder em Treinamento`
                ORDER BY g.nome_grm ASC
            """)
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Relatorio_GRMs', 'relatorio_grms.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_grms'))

    @app.route('/relatorio/membros')
    @login_required
    def relatorio_membros():
        try:
            membros = db.executar("MATCH (m:Membro) RETURN properties(m) AS p ORDER BY m.nome ASC")
            return render_template('relatorio_membros.html', membros=[x['p'] for x in membros])
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/membros_excel')
    @login_required
    def exportar_membros_excel():
        try:
            dados = db.executar("""
                MATCH (m:Membro)
                RETURN m.nome AS `Nome Completo`, m.endereco AS `Endereço`, m.email AS `E-mail`,
                       m.data_nascimento AS `Data de Nascimento`, m.telefone AS `Telefone`,
                       m.novo_convertido AS `Novo Convertido`,
                       m.membro_outro_ministerio AS `Veio de Outro Ministério`,
                       m.outra_religiao AS `Veio de Outra Religião`,
                       m.nao_professa_fe AS `Não Professava Fé`
                ORDER BY m.nome ASC
            """)
            df = pd.DataFrame(dados)
            for col in ["Novo Convertido", "Veio de Outro Ministério", "Veio de Outra Religião", "Não Professava Fé"]:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: 'Sim' if str(x) == '1' else 'Não')
            return exportar_dataframe_excel(df, 'Relatorio_Membros', 'relatorio_membros.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_membros'))

    @app.route('/relatorio/supervisores')
    @login_required
    def relatorio_supervisores():
        try:
            sups = db.executar("MATCH (s:Supervisor) RETURN COALESCE(s.id, s.id_mysql) AS id, s.nome AS nome, s.email AS email, s.telefone AS telefone, s.funcao_ministerial AS funcao_ministerial ORDER BY s.nome ASC")
            return render_template('relatorio_supervisores.html', supervisores=sups)
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/supervisores_excel')
    @login_required
    def exportar_supervisores_excel():
        try:
            dados = db.executar("MATCH (s:Supervisor) RETURN s.nome AS `Nome Completo`, s.endereco AS `Endereço`, s.email AS `E-mail`, s.data_nascimento AS `Data de Nascimento`, s.telefone AS `Telefone`, s.funcao_ministerial AS `Função Ministerial` ORDER BY s.nome ASC")
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Relatorio_Supervisores', 'relatorio_supervisores.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_supervisores'))

    @app.route('/relatorio/lideres')
    @login_required
    def relatorio_lideres():
        try:
            lideres = db.executar("MATCH (l:Lider) RETURN COALESCE(l.id, l.id_mysql) AS id, l.nome AS nome, l.email AS email, l.telefone AS telefone, l.funcao_ministerial AS funcao_ministerial ORDER BY l.nome ASC")
            return render_template('relatorio_lideres.html', lideres=lideres)
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/lideres_excel')
    @login_required
    def exportar_lideres_excel():
        try:
            dados = db.executar("MATCH (l:Lider) RETURN l.nome AS `Nome Completo`, l.endereco AS `Endereço`, l.email AS `E-mail`, l.data_nascimento AS `Data de Nascimento`, l.telefone AS `Telefone`, l.funcao_ministerial AS `Função Ministerial` ORDER BY l.nome ASC")
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Relatorio_Lideres', 'relatorio_lideres.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_lideres'))

    @app.route('/relatorio/colideres')
    @login_required
    def relatorio_colideres():
        try:
            colideres = db.executar("""
                MATCH (c:Colider)
                OPTIONAL MATCH (c)-[:AUXILIA]->(l:Lider)
                RETURN COALESCE(c.id, c.id_mysql) AS id, c.nome AS nome, c.email AS email,
                       c.telefone AS telefone, c.funcao_ministerial AS funcao_ministerial,
                       l.nome AS nome_lider_imediato
                ORDER BY c.nome ASC
            """)
            return render_template('relatorio_colideres.html', colideres=colideres)
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/colideres_excel')
    @login_required
    def exportar_colideres_excel():
        try:
            dados = db.executar("""
                MATCH (c:Colider)
                OPTIONAL MATCH (c)-[:AUXILIA]->(l:Lider)
                RETURN c.nome AS `Nome Completo`, c.endereco AS `Endereço`, c.email AS `E-mail`,
                       c.data_nascimento AS `Data de Nascimento`, c.telefone AS `Telefone`,
                       c.funcao_ministerial AS `Função Ministerial`, l.nome AS `Líder Imediato`
                ORDER BY c.nome ASC
            """)
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Relatorio_Co-lideres', 'relatorio_colideres.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_colideres'))

    @app.route('/relatorio/lideres_treinamento')
    @login_required
    def relatorio_lideres_treinamento():
        try:
            lideres_t = db.executar("""
                MATCH (lt:LiderTreinamento)
                OPTIONAL MATCH (lt)-[:TREINADO_POR]->(l:Lider)
                OPTIONAL MATCH (lt)-[:AUXILIADO_POR]->(c:Colider)
                RETURN COALESCE(lt.id, lt.id_mysql) AS id, lt.nome AS nome, lt.email AS email,
                       lt.telefone AS telefone, l.nome AS nome_lider, c.nome AS nome_colider
                ORDER BY lt.nome ASC
            """)
            return render_template('relatorio_lideres_treinamento.html', lideres_t=lideres_t)
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/lideres_treinamento_excel')
    @login_required
    def exportar_lideres_treinamento_excel():
        try:
            dados = db.executar("""
                MATCH (lt:LiderTreinamento)
                OPTIONAL MATCH (lt)-[:TREINADO_POR]->(l:Lider)
                OPTIONAL MATCH (lt)-[:AUXILIADO_POR]->(c:Colider)
                RETURN lt.nome AS `Nome Completo`, lt.email AS `E-mail`, lt.data_nascimento AS `Data de Nascimento`,
                       lt.telefone AS `Telefone`, l.nome AS `Líder Direto`, c.nome AS `Co-líder Direto`,
                       lt.funcao_ministerial AS `Função Ministerial`
                ORDER BY lt.nome ASC
            """)
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Lideres_Treinamento', 'relatorio_lideres_treinamento.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_lideres_treinamento'))

    @app.route('/relatorio/visitantes')
    @login_required
    def relatorio_visitantes():
        try:
            vis = db.executar("MATCH (v:Visitante) RETURN properties(v) AS p ORDER BY v.nome ASC")
            return render_template('relatorio_visitantes.html', visitantes=[x['p'] for x in vis])
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/visitantes_excel')
    @login_required
    def exportar_visitantes_excel():
        try:
            dados = db.executar("""
                MATCH (v:Visitante)
                RETURN v.nome AS `Nome Completo`, v.endereco AS `Endereço`, v.email AS `E-mail`,
                       v.data_nascimento AS `Data de Nascimento`, v.telefone AS `Telefone`,
                       v.membro_outro_ministerio AS `Membro de Outro Ministério`,
                       v.nome_ministerio AS `Nome do Ministério de Origem`,
                       v.outra_religiao AS `Veio de Outra Religião`
                ORDER BY v.nome ASC
            """)
            df = pd.DataFrame(dados)
            for col in ["Membro de Outro Ministério", "Veio de Outra Religião"]:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: 'Sim' if str(x) == '1' else 'Não')
            return exportar_dataframe_excel(df, 'Relatorio_Visitantes', 'relatorio_visitantes.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_visitantes'))

    @app.route('/relatorio/convertidos')
    @login_required
    def relatorio_convertidos():
        try:
            conv = db.executar("""
                MATCH (cv:Convertido)-[:ACEITOU_EM|CONVERTEU_NO]->(ev:Evento)-[:REALIZOU|REALIZADO_NO]-(g:GRM)
                OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
                OPTIONAL MATCH (l:Lider)-[:RESPONSAVEL_POR|DIRIGE]->(ev)
                OPTIONAL MATCH (c:Colider)-[:APOIOU|GERENCIA]->(ev)
                RETURN COALESCE(cv.id, cv.id_mysql) AS id, cv.nome AS nome, cv.telefone AS telefone,
                       cv.data_conversao AS data_conversao, g.nome_grm AS nome_grm,
                       COALESCE(g.regiao, r.nome) AS regiao, l.nome AS nome_lider, c.nome AS nome_colider
                ORDER BY cv.data_conversao DESC
            """)
            return render_template('relatorio_convertidos.html', convertidos=conv)
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for('relatorios'))

    @app.route('/exportar/convertidos_excel')
    @login_required
    def exportar_convertidos_excel():
        try:
            dados = db.executar("""
                MATCH (cv:Convertido)-[:ACEITOU_EM|CONVERTEU_NO]->(ev:Evento)-[:REALIZOU|REALIZADO_NO]-(g:GRM)
                OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
                OPTIONAL MATCH (l:Lider)-[:RESPONSAVEL_POR|DIRIGE]->(ev)
                OPTIONAL MATCH (c:Colider)-[:APOIOU|GERENCIA]->(ev)
                RETURN cv.nome AS `Nome do Convertido`, cv.telefone AS `Telefone`,
                       cv.data_conversao AS `Data da Conversão`, g.nome_grm AS `GRM do Evento`,
                       COALESCE(g.regiao, r.nome) AS `Região`, l.nome AS `Líder Responsável pelo Evento`,
                       c.nome AS `Co-líder Responsável pelo Evento`, cv.observacoes AS `Observações`
                ORDER BY cv.data_conversao DESC
            """)
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Relatorio_Convertidos', 'relatorio_convertidos.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('relatorio_convertidos'))

    @app.route('/historico_ofertas')
    @login_required
    def historico_ofertas():
        if session['perfil'] not in ['SUPERVISOR', 'DEVELOPER']:
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect(url_for('dashboard'))
        try:
            ofertas = db.executar("""
                MATCH (g:GRM)-[:REALIZOU|REALIZADO_NO]-(e:Evento)
                OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
                OPTIONAL MATCH (l:Lider)-[:RESPONSAVEL_POR|DIRIGE]->(g)
                RETURN COALESCE(e.data_evento, e.data) AS data_evento,
                       COALESCE(e.valor_ofertas, e.ofertas) AS valor_ofertas,
                       g.nome_grm AS nome_grm, COALESCE(g.regiao, r.nome) AS regiao, l.nome AS nome_lider
                ORDER BY data_evento DESC
            """)
            return render_template('historico_ofertas.html', ofertas=ofertas)
        except Exception as e:
            flash(f"Erro ao gerar histórico: {e}", "danger")
            return redirect(url_for('dashboard'))

    @app.route('/exportar/ofertas_excel')
    @login_required
    def exportar_ofertas_excel():
        if session['perfil'] not in ['SUPERVISOR', 'DEVELOPER']:
            return redirect(url_for('dashboard'))
        try:
            dados = db.executar("""
                MATCH (g:GRM)-[:REALIZOU|REALIZADO_NO]-(e:Evento)
                OPTIONAL MATCH (r:Regiao)-[:ABRIGA]->(g)
                OPTIONAL MATCH (l:Lider)-[:RESPONSAVEL_POR|DIRIGE]->(g)
                RETURN COALESCE(e.data_evento, e.data) AS `Data do Evento`,
                       COALESCE(e.valor_ofertas, e.ofertas) AS `Valor Arrecadado (R$)`,
                       g.nome_grm AS `GRM`, COALESCE(g.regiao, r.nome) AS `Região`, l.nome AS `Líder Responsável`
                ORDER BY `Data do Evento` DESC
            """)
            return exportar_dataframe_excel(pd.DataFrame(dados), 'Historico_Ofertas', 'historico_ofertas.xlsx')
        except Exception as e:
            flash(f"Erro ao exportar: {e}", "danger")
            return redirect(url_for('historico_ofertas'))
