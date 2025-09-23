from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from models import db, Usuario, Atendimento, LogAtendimento, Notificacao
from auth import auth_bp, admin_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_
import os
import base64
from io import BytesIO

# Importar PIL de forma opcional
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not available. Image processing will be disabled.")

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
    marca_filter = request.args.get('marca', '')
    usuario_filter = request.args.get('usuario', '', type=str)

    query = Atendimento.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if produto_filter:
        query = query.filter_by(produto=produto_filter)
    if marca_filter:
        query = query.filter_by(marca=marca_filter)
    if usuario_filter:
        query = query.filter_by(usuario_id=usuario_filter)

    atendimentos = query.order_by(desc(Atendimento.data_inicio)).paginate(
        page=page, per_page=10, error_out=False
    )

    # Buscar todos os usuários para o filtro
    usuarios = Usuario.query.filter_by(ativo=True).all()

    return render_template('atendimentos.html', atendimentos=atendimentos,
                         status_filter=status_filter, produto_filter=produto_filter,
                         marca_filter=marca_filter, usuario_filter=usuario_filter, usuarios=usuarios)

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
                marca=request.form.get('marca', ''),
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

    # Buscar usuários ativos para transferência (exceto o atual responsável)
    usuarios = Usuario.query.filter(
        and_(Usuario.ativo == True, Usuario.id != atendimento.usuario_id)
    ).all()

    return render_template('detalhes_atendimento.html',
                         atendimento=atendimento,
                         logs=logs,
                         usuarios=usuarios)

@app.route('/atendimentos/<int:id>/finalizar', methods=['POST'])
@login_required
def finalizar_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)

    # Verificar se o usuário atual é o responsável pelo atendimento
    if atendimento.usuario_id != current_user.id:
        flash('Apenas o responsável que criou este atendimento pode finalizá-lo.', 'error')
        return redirect(url_for('detalhes_atendimento', id=id))

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

@app.route('/atendimentos/<int:id>/transferir', methods=['POST'])
@login_required
def transferir_atendimento(id):
    atendimento = Atendimento.query.get_or_404(id)

    # Verificar se o usuário atual é o responsável pelo atendimento
    if atendimento.usuario_id != current_user.id:
        flash('Apenas o responsável atual pode transferir este atendimento.', 'error')
        return redirect(url_for('detalhes_atendimento', id=id))

    # Verificar se o atendimento está em andamento
    if atendimento.status != 'em_andamento':
        flash('Apenas atendimentos em andamento podem ser transferidos.', 'warning')
        return redirect(url_for('detalhes_atendimento', id=id))

    novo_responsavel_id = request.form.get('novo_responsavel_id')
    motivo = request.form.get('motivo', '')

    if not novo_responsavel_id:
        flash('Selecione um responsável para transferir o atendimento.', 'error')
        return redirect(url_for('detalhes_atendimento', id=id))

    # Verificar se o novo responsável existe e está ativo
    novo_responsavel = Usuario.query.filter_by(id=novo_responsavel_id, ativo=True).first()
    if not novo_responsavel:
        flash('Usuário selecionado não encontrado ou inativo.', 'error')
        return redirect(url_for('detalhes_atendimento', id=id))

    # Transferir o atendimento
    try:
        atendimento.transferir_para(novo_responsavel_id, current_user, motivo)
        db.session.commit()
        flash(f'Atendimento transferido com sucesso para {novo_responsavel.nome}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao transferir atendimento. Tente novamente.', 'error')

    return redirect(url_for('detalhes_atendimento', id=id))

@app.route('/api/notificacoes')
@login_required
def api_notificacoes():
    """API para buscar notificações do usuário atual"""
    notificacoes = Notificacao.query.filter_by(
        usuario_id=current_user.id,
        lida=False
    ).order_by(desc(Notificacao.data_criacao)).limit(10).all()

    notificacoes_json = []
    for notif in notificacoes:
        notificacoes_json.append({
            'id': notif.id,
            'tipo': notif.tipo,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'data_criacao': notif.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'atendimento_id': notif.atendimento_id
        })

    return jsonify({
        'notificacoes': notificacoes_json,
        'total_nao_lidas': len(notificacoes_json)
    })

@app.route('/notificacoes/<int:id>/marcar-lida', methods=['POST'])
@login_required
def marcar_notificacao_lida(id):
    """Marca uma notificação como lida"""
    notificacao = Notificacao.query.filter_by(
        id=id,
        usuario_id=current_user.id
    ).first_or_404()

    notificacao.lida = True
    db.session.commit()

    return jsonify({'success': True})

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

@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    """Página de configurações do usuário"""
    if request.method == 'POST':
        try:
            # Atualizar senha se fornecida
            senha_atual = request.form.get('senha_atual')
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')

            if senha_atual and nova_senha:
                # Verificar senha atual
                if not current_user.check_password(senha_atual):
                    flash('Senha atual incorreta.', 'error')
                    return redirect(url_for('configuracoes'))

                # Verificar se as senhas coincidem
                if nova_senha != confirmar_senha:
                    flash('As senhas não coincidem.', 'error')
                    return redirect(url_for('configuracoes'))

                # Verificar comprimento mínimo
                if len(nova_senha) < 6:
                    flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                    return redirect(url_for('configuracoes'))

                # Atualizar senha
                current_user.set_password(nova_senha)

            # Atualizar foto se fornecida
            foto = request.files.get('foto_perfil')
            if foto and foto.filename:
                # Verificar tipo de arquivo
                if not foto.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    flash('Apenas arquivos PNG, JPG e JPEG são permitidos.', 'error')
                    return redirect(url_for('configuracoes'))

                # Verificar tamanho (máximo 2MB)
                foto.seek(0, os.SEEK_END)
                file_length = foto.tell()
                foto.seek(0)

                if file_length > 2 * 1024 * 1024:  # 2MB
                    flash('A imagem deve ter no máximo 2MB.', 'error')
                    return redirect(url_for('configuracoes'))

                # Processar imagem
                try:
                    if PILLOW_AVAILABLE:
                        # Redimensionar e converter para base64 com Pillow
                        image = Image.open(foto)
                        # Redimensionar para 150x150 mantendo proporção
                        image.thumbnail((150, 150), Image.Resampling.LANCZOS)

                        # Converter para RGB se necessário
                        if image.mode != 'RGB':
                            image = image.convert('RGB')

                        # Salvar em buffer como JPEG
                        buffer = BytesIO()
                        image.save(buffer, format='JPEG', quality=85)
                        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        current_user.foto_perfil = f"data:image/jpeg;base64,{img_base64}"
                    else:
                        # Fallback: salvar imagem sem processamento
                        foto.seek(0)
                        img_data = foto.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')

                        # Determinar tipo MIME baseado na extensão
                        filename_lower = foto.filename.lower()
                        if filename_lower.endswith('.png'):
                            mime_type = 'image/png'
                        elif filename_lower.endswith(('.jpg', '.jpeg')):
                            mime_type = 'image/jpeg'
                        else:
                            mime_type = 'image/jpeg'  # default

                        current_user.foto_perfil = f"data:{mime_type};base64,{img_base64}"

                except Exception as e:
                    flash('Erro ao processar a imagem.', 'error')
                    return redirect(url_for('configuracoes'))

            db.session.commit()
            flash('Configurações atualizadas com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash('Erro ao salvar configurações. Tente novamente.', 'error')

        return redirect(url_for('configuracoes'))

    return render_template('configuracoes.html')

@app.route('/configuracoes/remover-foto', methods=['POST'])
@login_required
def remover_foto():
    """Remove a foto de perfil do usuário"""
    try:
        current_user.foto_perfil = None
        db.session.commit()
        flash('Foto removida com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao remover foto.', 'error')

    return redirect(url_for('configuracoes'))

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

    # Criar usuários de teste se não existirem
    usuarios_teste = [
        {'nome': 'João Silva', 'email': 'joao@hubgeo.com', 'role': 'atendente'},
        {'nome': 'Maria Santos', 'email': 'maria@hubgeo.com', 'role': 'atendente'},
        {'nome': 'Pedro Costa', 'email': 'pedro@hubgeo.com', 'role': 'atendente'},
        {'nome': 'Ana Oliveira', 'email': 'ana@hubgeo.com', 'role': 'atendente'}
    ]

    for user_data in usuarios_teste:
        if not Usuario.query.filter_by(email=user_data['email']).first():
            user = Usuario(
                nome=user_data['nome'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password('123456')
            db.session.add(user)
            print(f"Usuário criado: {user_data['email']} / 123456")

    db.session.commit()

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