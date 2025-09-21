from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from models import db, Usuario, Atendimento, LogAtendimento
from auth import auth_bp, admin_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hubgeo-sistema-atendimento-2024-secret-key-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sIuTpZxKilayoTVOrFDnkOOqhYjAeoCe@ballast.proxy.rlwy.net:20008/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
app.register_blueprint(auth_bp)

# Rotas principais
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Estatísticas para o dashboard
    total_atendimentos = Atendimento.query.count()
    atendimentos_hoje = Atendimento.query.filter(
        func.date(Atendimento.data_inicio) == datetime.now().date()
    ).count()
    atendimentos_em_andamento = Atendimento.query.filter_by(status='em_andamento').count()
    atendimentos_concluidos = Atendimento.query.filter_by(status='concluido').count()

    # Atendimentos recentes
    atendimentos_recentes = Atendimento.query.order_by(desc(Atendimento.data_inicio)).limit(5).all()

    # Dados para gráficos
    # Atendimentos por produto (últimos 30 dias)
    trinta_dias_atras = datetime.now() - timedelta(days=30)
    produto_query = db.session.query(
        Atendimento.produto,
        func.count(Atendimento.id).label('count')
    ).filter(
        Atendimento.data_inicio >= trinta_dias_atras
    ).group_by(Atendimento.produto).all()

    # Converter para lista de listas
    atendimentos_por_produto = [[row[0], row[1]] for row in produto_query]

    # Atendimentos por dia (últimos 7 dias)
    sete_dias_atras = datetime.now() - timedelta(days=7)
    dia_query = db.session.query(
        func.date(Atendimento.data_inicio).label('dia'),
        func.count(Atendimento.id).label('count')
    ).filter(
        Atendimento.data_inicio >= sete_dias_atras
    ).group_by(func.date(Atendimento.data_inicio)).all()

    # Converter para lista de listas com data formatada
    atendimentos_por_dia = []
    for row in dia_query:
        if row[0]:  # Verificar se a data não é None
            atendimentos_por_dia.append([row[0].strftime('%Y-%m-%d'), row[1]])

    # Se não há dados, criar dados vazios para evitar erros
    if not atendimentos_por_produto:
        atendimentos_por_produto = []
    if not atendimentos_por_dia:
        atendimentos_por_dia = []

    return render_template('dashboard.html',
                         total_atendimentos=total_atendimentos,
                         atendimentos_hoje=atendimentos_hoje,
                         atendimentos_em_andamento=atendimentos_em_andamento,
                         atendimentos_concluidos=atendimentos_concluidos,
                         atendimentos_recentes=atendimentos_recentes,
                         atendimentos_por_produto=atendimentos_por_produto,
                         atendimentos_por_dia=atendimentos_por_dia)

@app.route('/atendimentos')
@login_required
def atendimentos():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    produto_filter = request.args.get('produto', '')

    query = Atendimento.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if produto_filter:
        query = query.filter_by(produto=produto_filter)

    atendimentos = query.order_by(desc(Atendimento.data_inicio)).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('atendimentos.html', atendimentos=atendimentos,
                         status_filter=status_filter, produto_filter=produto_filter)

@app.route('/atendimentos/novo', methods=['GET', 'POST'])
@login_required
def novo_atendimento():
    if request.method == 'POST':
        try:
            atendimento = Atendimento(
                cliente_nome=request.form['cliente_nome'],
                cliente_email=request.form.get('cliente_email', ''),
                cliente_contato=request.form.get('cliente_contato', ''),
                forma_contato=request.form['forma_contato'],
                produto=request.form['produto'],
                problema=request.form['problema'],
                usuario_id=current_user.id
            )

            db.session.add(atendimento)
            db.session.commit()

            # Registrar log
            log = LogAtendimento(
                atendimento_id=atendimento.id,
                usuario_id=current_user.id,
                acao='Atendimento criado',
                detalhes=f'Atendimento criado para {atendimento.cliente_nome}'
            )
            db.session.add(log)
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
    logs = LogAtendimento.query.filter_by(atendimento_id=id).order_by(LogAtendimento.timestamp).all()
    return render_template('detalhes_atendimento.html', atendimento=atendimento, logs=logs)

@app.route('/atendimentos/<int:id>/finalizar', methods=['POST'])
@login_required
def finalizar_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)

    if atendimento.status == 'concluido':
        flash('Este atendimento já foi finalizado.', 'warning')
        return redirect(url_for('detalhes_atendimento', id=id))

    observacoes = request.form.get('observacoes', '')
    atendimento.finalizar(observacoes)

    # Registrar log
    log = LogAtendimento(
        atendimento_id=atendimento.id,
        usuario_id=current_user.id,
        acao='Atendimento finalizado',
        detalhes=f'Atendimento finalizado por {current_user.nome}'
    )
    db.session.add(log)
    db.session.commit()

    flash('Atendimento finalizado com sucesso!', 'success')
    return redirect(url_for('detalhes_atendimento', id=id))

@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    # API para dados do dashboard em tempo real
    stats = {
        'total_atendimentos': Atendimento.query.count(),
        'atendimentos_hoje': Atendimento.query.filter(
            func.date(Atendimento.data_inicio) == datetime.now().date()
        ).count(),
        'em_andamento': Atendimento.query.filter_by(status='em_andamento').count(),
        'concluidos': Atendimento.query.filter_by(status='concluido').count()
    }
    return jsonify(stats)

# Função para criar tabelas e usuário admin inicial
def create_tables():
    db.create_all()

    # Criar usuário admin se não existir
    if not Usuario.query.filter_by(email='admin@hubgeo.com').first():
        admin = Usuario(
            nome='Administrador',
            email='admin@hubgeo.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado: admin@hubgeo.com / admin123")

if __name__ == '__main__':
    try:
        with app.app_context():
            print("Inicializando banco de dados...")
            create_tables()
            print("Sistema iniciado com sucesso!")
            print("Login: admin@hubgeo.com")
            print("Senha: admin123")

        # Configuração para produção
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

        app.run(debug=debug, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
        print("Verifique se todas as dependências estão instaladas:")
        print("pip install -r requirements.txt")