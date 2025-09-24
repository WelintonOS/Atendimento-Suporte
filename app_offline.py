#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Versão offline do Sistema de Atendimento HUBGEO
Usa SQLite para funcionar sem conexão com internet
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
import os

# Importar classes necessárias
from models import db, Usuario, Atendimento, LogAtendimento, Notificacao
from auth import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-hubgeo-offline'

# Configuração do banco SQLite local
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "atendimento_offline.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max para uploads

# Inicializar extensões
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
app.register_blueprint(auth_bp)

# Rotas principais
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('atendimentos'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Estatísticas básicas
    total_atendimentos = Atendimento.query.count()
    em_andamento = Atendimento.query.filter_by(status='em_andamento').count()
    concluidos_hoje = Atendimento.query.filter(
        func.date(Atendimento.data_inicio) == datetime.now().date()
    ).count()

    # Tempo médio de atendimento (concluídos)
    atendimentos_concluidos = Atendimento.query.filter_by(status='concluido').all()
    tempo_medio = 0
    if atendimentos_concluidos:
        tempos = [(a.data_fim - a.data_inicio).total_seconds() / 3600
                 for a in atendimentos_concluidos if a.data_fim]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

    # Dados para gráficos
    # Atendimentos por produto (últimos 30 dias)
    trinta_dias_atras = datetime.now() - timedelta(days=30)
    produto_query = db.session.query(
        Atendimento.produto,
        func.count(Atendimento.id).label('count')
    ).filter(
        Atendimento.data_inicio >= trinta_dias_atras
    ).group_by(Atendimento.produto).all()

    atendimentos_por_produto = [[row[0], row[1]] for row in produto_query]

    # Atendimentos por dia (últimos 7 dias)
    sete_dias_atras = datetime.now() - timedelta(days=7)
    dia_query = db.session.query(
        func.date(Atendimento.data_inicio).label('dia'),
        func.count(Atendimento.id).label('count')
    ).filter(
        Atendimento.data_inicio >= sete_dias_atras
    ).group_by(func.date(Atendimento.data_inicio)).all()

    # Converter para formato do gráfico
    atendimentos_por_dia = []
    for i in range(7):
        data = (datetime.now() - timedelta(days=i)).date()
        count = next((row[1] for row in dia_query if row[0] == data), 0)
        atendimentos_por_dia.append([data.strftime('%d/%m'), count])

    atendimentos_por_dia.reverse()

    return render_template('dashboard.html',
                         total_atendimentos=total_atendimentos,
                         em_andamento=em_andamento,
                         concluidos_hoje=concluidos_hoje,
                         tempo_medio=round(tempo_medio, 1),
                         atendimentos_por_produto=atendimentos_por_produto,
                         atendimentos_por_dia=atendimentos_por_dia)

@app.route('/atendimentos')
@login_required
def atendimentos():
    page = request.args.get('page', 1, type=int)

    # Filtros
    status_filter = request.args.get('status', '')
    produto_filter = request.args.get('produto', '')
    marca_filter = request.args.get('marca', '')
    usuario_filter = request.args.get('usuario', '')

    # Query base
    query = Atendimento.query

    # Aplicar filtros
    if status_filter:
        query = query.filter_by(status=status_filter)
    if produto_filter:
        query = query.filter_by(produto=produto_filter)
    if marca_filter:
        query = query.filter_by(marca=marca_filter)
    if usuario_filter:
        query = query.filter_by(usuario_id=int(usuario_filter))

    # Ordenação e paginação
    atendimentos = query.order_by(Atendimento.data_inicio.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    # Lista de usuários para filtro
    usuarios = Usuario.query.filter_by(ativo=True).all()

    return render_template('atendimentos.html',
                         atendimentos=atendimentos,
                         usuarios=usuarios,
                         status_filter=status_filter,
                         produto_filter=produto_filter,
                         marca_filter=marca_filter,
                         usuario_filter=usuario_filter)

@app.route('/atendimentos/novo', methods=['GET', 'POST'])
@login_required
def novo_atendimento():
    if request.method == 'POST':
        try:
            novo_atendimento = Atendimento(
                cliente_nome=request.form['cliente_nome'],
                cliente_email=request.form.get('cliente_email'),
                cliente_contato=request.form.get('cliente_contato'),
                forma_contato=request.form['forma_contato'],
                produto=request.form['produto'],
                marca=request.form.get('marca'),
                problema=request.form['problema'],
                usuario_id=current_user.id
            )

            db.session.add(novo_atendimento)
            db.session.commit()

            flash('Atendimento criado com sucesso!', 'success')
            return redirect(url_for('atendimentos'))

        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar atendimento. Tente novamente.', 'error')

    return render_template('novo_atendimento.html')

@app.route('/atendimentos/<int:id>')
@login_required
def detalhes_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)
    usuarios = Usuario.query.filter_by(ativo=True).all()

    return render_template('detalhes_atendimento.html',
                         atendimento=atendimento,
                         usuarios=usuarios)

@app.route('/atendimentos/<int:id>/finalizar', methods=['POST'])
@login_required
def finalizar_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)

    # Verificar se o usuário atual é o responsável pelo atendimento
    if atendimento.usuario_id != current_user.id:
        flash('Apenas o responsável que criou este atendimento pode finalizá-lo.', 'error')
        return redirect(url_for('detalhes_atendimento', id=id))

    try:
        observacoes = request.form.get('observacoes', '')
        atendimento.finalizar(observacoes)

        db.session.commit()
        flash('Atendimento finalizado com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Erro ao finalizar atendimento.', 'error')

    return redirect(url_for('detalhes_atendimento', id=id))

@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    hoje = datetime.now().date()

    stats = {
        'atendimentos_hoje': Atendimento.query.filter(
            func.date(Atendimento.data_inicio) == hoje
        ).count(),
        'em_andamento': Atendimento.query.filter_by(status='em_andamento').count()
    }

    return jsonify(stats)

@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        # Verificar se é upload de foto ou alteração de senha
        if 'foto_perfil' in request.files:
            # Upload de foto (simplificado para offline)
            foto = request.files['foto_perfil']
            if foto and foto.filename:
                # Salvar como base64 (simplificado)
                import base64
                foto_data = base64.b64encode(foto.read()).decode('utf-8')
                current_user.foto_perfil = f"data:{foto.mimetype};base64,{foto_data}"
                db.session.commit()
                flash('Foto de perfil atualizada!', 'success')

        elif 'senha_atual' in request.form:
            # Alteração de senha
            senha_atual = request.form['senha_atual']
            nova_senha = request.form['nova_senha']
            confirmar_senha = request.form['confirmar_senha']

            if not current_user.check_password(senha_atual):
                flash('Senha atual incorreta.', 'error')
            elif nova_senha != confirmar_senha:
                flash('As senhas não coincidem.', 'error')
            elif len(nova_senha) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
            else:
                current_user.set_password(nova_senha)
                db.session.commit()
                flash('Senha alterada com sucesso!', 'success')

        return redirect(url_for('configuracoes'))

    return render_template('configuracoes.html')

@app.route('/configuracoes/foto/remover', methods=['POST'])
@login_required
def remover_foto():
    current_user.foto_perfil = None
    db.session.commit()
    flash('Foto removida com sucesso!', 'success')
    return redirect(url_for('configuracoes'))

def inicializar_banco():
    """Inicializa o banco SQLite com dados básicos"""
    with app.app_context():
        db.create_all()

        # Verificar se já existe admin
        admin = Usuario.query.filter_by(email='admin@hubgeo.com').first()
        if not admin:
            # Criar usuário admin
            admin = Usuario(
                nome='Administrador',
                email='admin@hubgeo.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)

            # Criar usuários de teste
            usuarios_teste = [
                ('João Silva', 'joao@hubgeo.com'),
                ('Maria Santos', 'maria@hubgeo.com'),
                ('Pedro Costa', 'pedro@hubgeo.com'),
                ('Ana Oliveira', 'ana@hubgeo.com'),
                ('Welinton Oliveira Silva', 'welinton@hubgeo.com')
            ]

            for nome, email in usuarios_teste:
                user = Usuario(nome=nome, email=email, role='atendente')
                user.set_password('123456')
                db.session.add(user)

            db.session.commit()
            print("Banco SQLite inicializado com usuários padrão!")
            print("Admin: admin@hubgeo.com / admin123")
            print("Usuários teste: senha 123456")

if __name__ == '__main__':
    inicializar_banco()
    print("="*50)
    print("Sistema de Atendimento HUBGEO - MODO OFFLINE")
    print("="*50)
    print("URL: http://localhost:5000")
    print("Banco: SQLite Local")
    print("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)