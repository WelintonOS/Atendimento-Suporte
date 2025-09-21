from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Usuario.query.filter_by(email=email, ativo=True).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            next_page = request.args.get('next')
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está em uso.', 'error')
            return render_template('usuarios.html', usuarios=Usuario.query.all())

        # Criar novo usuário
        novo_user = Usuario(
            nome=nome,
            email=email,
            role=role
        )
        novo_user.set_password(password)

        try:
            db.session.add(novo_user)
            db.session.commit()
            flash(f'Usuário {nome} criado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar usuário. Tente novamente.', 'error')

        return redirect(url_for('auth.usuarios'))

    return render_template('usuarios.html', usuarios=Usuario.query.all())

@auth_bp.route('/usuarios/<int:user_id>/toggle')
@login_required
@admin_required
def toggle_usuario(user_id):
    user = Usuario.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'error')
        return redirect(url_for('auth.usuarios'))

    user.ativo = not user.ativo
    db.session.commit()

    status = "ativado" if user.ativo else "desativado"
    flash(f'Usuário {user.nome} {status} com sucesso.', 'success')

    return redirect(url_for('auth.usuarios'))

@auth_bp.route('/usuarios/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_usuario(user_id):
    user = Usuario.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'error')
        return redirect(url_for('auth.usuarios'))

    # Verificar se usuário tem atendimentos
    if user.atendimentos:
        flash('Não é possível excluir usuário com atendimentos associados.', 'error')
        return redirect(url_for('auth.usuarios'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuário {user.nome} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir usuário.', 'error')

    return redirect(url_for('auth.usuarios'))