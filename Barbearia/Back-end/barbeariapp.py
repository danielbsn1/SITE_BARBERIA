from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import func
import os

# ================================
# 🔧 CONFIGURAÇÃO DO FLASK E BANCO
# ================================

# Caminhos base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(BASE_DIR, 'Front-end', 'templates')
static_dir = os.path.join(BASE_DIR, 'Front-end', 'static')

# Inicializa o Flask com os caminhos corretos
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'banco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "chave_super_segura"

# Inicializa o banco
db = SQLAlchemy(app)

# =============================
# 📦 MODELOS
# =============================
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    telefone = db.Column(db.String(50))
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    preco = db.Column(db.Float)
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)

# =============================
# 🌐 ROTAS DE PÁGINAS
# =============================
@app.route('/')
def home():
    return render_template('clientes/home.html')

@app.route('/agenda')
def agenda():
    return render_template('clientes/agenda.html')

@app.route('/meus-agendamentos')
def meus_agendamentos():
    return render_template('clientes/meus_agendamentos.html')

@app.route('/admin')
def admin_home():
    return render_template('admin/login.html')

@app.route('/caixa')
def caixa():
    return render_template('admin/caixa.html')

# =============================
# 🔗 API DE SERVIÇOS E AGENDAMENTOS
# =============================
@app.route('/api/servicos')
def api_servicos():
    servicos = Servico.query.all()
    return jsonify({
        'servicos': [
            {'id': s.id, 'nome': s.nome, 'preco': s.preco}
            for s in servicos
        ]
    })

@app.route('/api/agendamentos', methods=['GET', 'POST'])
def api_agendamentos():
    if request.method == 'GET':
        data_str = request.args.get('data')
        telefone = request.args.get('telefone')

        # Busca por data
        if data_str:
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d').date()
            except:
                return jsonify({'error': 'Data inválida'}), 400

            agendamentos = Agendamento.query.filter(
                func.date(Agendamento.data_hora) == data
            ).all()

        # Busca por telefone (para cliente)
        elif telefone:
            agendamentos = (
                Agendamento.query
                .join(Cliente)
                .filter(Cliente.telefone == telefone)
                .all()
            )
        else:
            return jsonify({'agendamentos': []})

        return jsonify({
            'agendamentos': [
                {
                    'id': a.id,
                    'cliente': a.cliente.nome,
                    'telefone': a.cliente.telefone,
                    'servico': a.servico.nome,
                    'preco': a.servico.preco,
                    'data_hora': a.data_hora.strftime('%Y-%m-%d %H:%M')
                } for a in agendamentos
            ]
        })

    # Criar novo agendamento
    if request.method == 'POST':
        data = request.get_json()
        nome = data.get('nome')
        telefone = data.get('telefone')
        servico_id = data.get('servico_id')
        data_str = data.get('data')
        hora_str = data.get('hora')

        if not (nome and servico_id and data_str and hora_str):
            return jsonify({'error': 'Campos obrigatórios faltando'}), 400

        data_hora = datetime.strptime(f'{data_str} {hora_str}', '%Y-%m-%d %H:%M')

        # Verifica se horário está ocupado
        existe = Agendamento.query.filter_by(data_hora=data_hora).first()
        if existe:
            return jsonify({'error': 'Horário já ocupado'}), 400

        # Verifica se cliente já existe
        cliente = Cliente.query.filter_by(telefone=telefone).first()
        if not cliente:
            cliente = Cliente(nome=nome, telefone=telefone)
            db.session.add(cliente)
            db.session.commit()

        agendamento = Agendamento(
            cliente_id=cliente.id,
            servico_id=servico_id,
            data_hora=data_hora
        )
        db.session.add(agendamento)
        db.session.commit()

        return jsonify({'message': 'Agendamento criado com sucesso!'})

# =============================
# ⚙️ INICIALIZAÇÃO DO BANCO
# =============================
with app.app_context():
    db.create_all()
    if Servico.query.count() == 0:
        db.session.add_all([
            Servico(nome='Corte de Cabelo', preco=50.00),
            Servico(nome='Barba Terapêutica', preco=30.00),
            Servico(nome='Sobrancelha', preco=15.00),
            Servico(nome='Limpeza de Pele', preco=40.00)
        ])
        db.session.commit()

# =============================
# 🚀 INÍCIO DO SERVIDOR
# =============================
if __name__ == '__main__':
    app.run(debug=True)
# =============================