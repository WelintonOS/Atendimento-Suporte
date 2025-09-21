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
    produto = db.Column(db.String(30), nullable=False)  # Emlid, Geomax, Posição, GTOPO
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