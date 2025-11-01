from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'banco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =============================
# MODELOS
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
# ROTAS DE PÁGINAS
# =============================
@app.route('/')
def index():
    return render_template('agenda.html')

# =============================
# API DE SERVIÇOS E AGENDAMENTOS
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
# INICIALIZAÇÃO DO BANCO
# =============================
with app.app_context():
    db.create_all()
    # Adiciona serviços se ainda não existirem
    if Servico.query.count() == 0:
        db.session.add_all([
            Servico(nome='Corte de Cabelo', preco=50.00),
            Servico(nome='Barba Terapêutica', preco=30.00),
            Servico(nome='Sobrancelha', preco=15.00),
            Servico(nome='Limpeza de Pele', preco=40.00)
        ])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
