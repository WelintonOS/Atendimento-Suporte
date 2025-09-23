from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='atendente')  # admin, atendente
    ativo = db.Column(db.Boolean, default=True)
    foto_perfil = db.Column(db.String(255), nullable=True)  # Base64 da imagem
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com atendimentos
    atendimentos = db.relationship('Atendimento', backref='responsavel', lazy=True)

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Atendimento(db.Model):
    __tablename__ = 'atendimentos'

    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_email = db.Column(db.String(120), nullable=True)
    cliente_contato = db.Column(db.String(50), nullable=True)
    forma_contato = db.Column(db.String(20), nullable=False)  # Email, WhatsApp, Presencial
    produto = db.Column(db.String(30), nullable=False)  # Acessórios, Controladoras, Drones, etc.
    marca = db.Column(db.String(30), nullable=True)  # CHCNAV, Emlid, Leica, etc.
    problema = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='em_andamento')  # em_andamento, concluido, cancelado
    observacoes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Atendimento {self.id} - {self.cliente_nome}>'

    @property
    def duracao(self):
        if self.data_fim and self.data_inicio:
            delta = self.data_fim - self.data_inicio
            hours = delta.total_seconds() // 3600
            minutes = (delta.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        return "Em andamento"

    def finalizar(self, observacoes=None):
        self.data_fim = datetime.utcnow()
        self.status = 'concluido'
        if observacoes:
            self.observacoes = observacoes

    def transferir_para(self, novo_responsavel_id, usuario_transferindo, motivo=None):
        """Transfere o atendimento para outro usuário"""
        from app import db

        responsavel_anterior = self.responsavel.nome
        self.usuario_id = novo_responsavel_id

        # Criar log da transferência
        log = LogAtendimento(
            atendimento_id=self.id,
            usuario_id=usuario_transferindo.id,
            acao='transferencia',
            detalhes=f'Transferido de {responsavel_anterior} para {self.responsavel.nome}. Motivo: {motivo or "Não informado"}'
        )
        db.session.add(log)

        # Criar notificação para o novo responsável
        notificacao = Notificacao(
            usuario_id=novo_responsavel_id,
            atendimento_id=self.id,
            tipo='transferencia',
            titulo=f'Atendimento #{self.id} transferido para você',
            mensagem=f'O atendimento do cliente {self.cliente_nome} foi transferido por {usuario_transferindo.nome}. Motivo: {motivo or "Não informado"}'
        )
        db.session.add(notificacao)

class LogAtendimento(db.Model):
    __tablename__ = 'logs_atendimento'

    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimentos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    acao = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    atendimento = db.relationship('Atendimento', backref='logs')
    usuario = db.relationship('Usuario', backref='logs_acao')

    def __repr__(self):
        return f'<Log {self.id} - {self.acao}>'


class Notificacao(db.Model):
    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimentos.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # transferencia, finalizado, etc.
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    usuario = db.relationship('Usuario', backref='notificacoes')
    atendimento = db.relationship('Atendimento', backref='notificacoes')

    def __repr__(self):
        return f'<Notificacao {self.id} - {self.tipo}>'