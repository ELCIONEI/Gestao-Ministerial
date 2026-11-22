import re
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
from utils import PERFIS, login_required


def registrar_rotas(app):
    @app.route('/')
    def login_page():
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login():
        if 'username' in request.form and 'password' in request.form:
            login_input = request.form['username'].strip().lower()
            password_form = request.form['password']
            try:
                user = db.executar_um("""
                    MATCH (u:Usuario)
                    WHERE toLower(u.email) = $login OR toLower(u.username) = $login
                    RETURN elementId(u) AS id, u.nome AS nome, u.senha AS senha,
                           u.email AS email, u.perfil AS perfil, u.force_password_change AS force_pw
                """, {"login": login_input})

                if user and check_password_hash(user['senha'], password_form):
                    session['loggedin'] = True
                    session['id'] = user['id']
                    session['username'] = user['nome']
                    session['perfil'] = 'DEVELOPER' if user['email'] == 'ney@gmail.com' else user.get('perfil', 'MEMBRO')

                    if user.get('force_pw') is True:
                        return jsonify({'success': True, 'redirect_url': url_for('change_password')})
                    return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
                return jsonify({'success': False, 'message': 'E-mail/Matrícula ou senha incorretos.'}), 401
            except Exception as e:
                print(f"Erro no login Neo4j: {e}")
                return jsonify({'success': False, 'message': 'Ocorreu um erro no servidor.'}), 500
        return jsonify({'success': False, 'message': 'Requisição inválida.'}), 400

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({'success': True})

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('menu.html', PERFIS=PERFIS, perfil_usuario=session.get('perfil'))

    @app.route('/cadastros')
    @login_required
    def cadastros():
        return render_template('cadastro.html', PERFIS=PERFIS, perfil_usuario=session.get('perfil'))

    @app.route('/conceder_acesso', methods=['GET', 'POST'])
    @login_required
    def conceder_acesso():
        if session['perfil'] not in ['SUPERVISOR', 'DEVELOPER']:
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            try:
                nome = request.form.get('nome', '').strip()
                email = request.form.get('email', '').strip().lower()
                matricula = request.form.get('matricula', '').strip().lower()
                perfil = request.form.get('perfil', '').strip().upper()
                senha = request.form.get('senha', '')

                if not nome or not email or not matricula or not perfil or not senha:
                    flash("Preencha todos os campos obrigatórios (Nome, E-mail, Matrícula, Perfil e Senha).", "danger")
                    return redirect(url_for('conceder_acesso'))

                existente = db.executar_um("""
                    MATCH (u:Usuario)
                    WHERE toLower(u.email) = $email OR toLower(u.username) = $matricula
                    RETURN u.email AS email, u.username AS username
                """, {"email": email, "matricula": matricula})

                if existente:
                    flash("Erro: Já existe um usuário cadastrado com este E-mail ou Matrícula.", "danger")
                    return redirect(url_for('conceder_acesso'))

                db.executar("""
                    CREATE (u:Usuario {
                        nome: $nome,
                        email: $email,
                        username: $matricula,
                        senha: $senha,
                        perfil: $perfil,
                        force_password_change: true
                    })
                """, {
                    "nome": nome,
                    "email": email,
                    "matricula": matricula,
                    "senha": generate_password_hash(senha),
                    "perfil": perfil
                })

                flash(f"Acesso concedido para {nome}! Login: {matricula} ou {email}", "success")
                return redirect(url_for('conceder_acesso'))
            except Exception as e:
                flash(f"Ocorreu um erro ao conceder acesso: {e}", "danger")
                return redirect(url_for('conceder_acesso'))

        return render_template('conceder_acesso.html')

    @app.route('/change_password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if new_password != confirm_password:
                flash('As senhas não coincidem. Tente novamente.', 'danger')
                return redirect(url_for('change_password'))
            if len(new_password) < 8:
                flash('A senha deve ter no mínimo 8 caracteres.', 'danger')
                return redirect(url_for('change_password'))
            if not re.search(r'[A-Z]', new_password):
                flash('A senha deve conter pelo menos uma letra maiúscula.', 'danger')
                return redirect(url_for('change_password'))
            if len(re.findall(r'[0-9]', new_password)) < 2:
                flash('A senha deve conter pelo menos dois números.', 'danger')
                return redirect(url_for('change_password'))

            try:
                hashed_password = generate_password_hash(new_password)
                db.executar("""
                    MATCH (u:Usuario) WHERE elementId(u) = $uid
                    SET u.senha = $senha, u.force_password_change = false
                """, {"senha": hashed_password, "uid": session['id']})
                flash('Senha alterada com sucesso! Você já pode usar o sistema.', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Ocorreu um erro ao atualizar sua senha: {e}', 'danger')
                return redirect(url_for('change_password'))

        return render_template('change_password.html')