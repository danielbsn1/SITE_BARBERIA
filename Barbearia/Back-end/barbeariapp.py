import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
import logging

# Carrega variáveis do .env
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Diretórios do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(BASE_DIR, 'Front-end', 'templates')
static_dir = os.path.join(BASE_DIR, 'Front-end', 'static')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

# Configuração do banco
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuração do e-mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

mail = Mail(app)

# Para qual e-mail enviar notificações
DONO_EMAIL = os.getenv('EMAIL_USER')


# =====================================================================
# MODELS
# =====================================================================
class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)


class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    servico = db.relationship('Servico', backref=db.backref('agendamentos', lazy=True))


class Caixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Float, default=0.0)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.now)


# =====================================================================
# FUNÇÃO DE ENVIO DE EMAIL
# =====================================================================
def enviar_notificacao_agendamento(dia, hora, servico_nome, preco):
    try:
        with app.app_context():
            msg = Message(
                subject='Novo Agendamento Realizado',
                recipients=[DONO_EMAIL]
            )
            msg.body = f"""
Novo agendamento realizado:

📅 Dia: {dia}
⏰ Hora: {hora}
💈 Serviço: {servico_nome}
💵 Preço: R$ {preco:.2f}

 Barberia Style
"""
            mail.send(msg)
            app.logger.info("E-mail de notificação enviado com sucesso!")

    except Exception as e:
        app.logger.error(f"Erro ao enviar e-mail: {e}")


# =====================================================================
# ROTAS DE PÁGINAS
# =====================================================================
@app.route('/')
def home():
    return render_template('clientes/home.html')


@app.route('/agenda')
def agenda():
    return render_template('clientes/agenda.html')


@app.route('/meus-agendamentos')
def meus_agendamentos():
    return render_template('clientes/meus_agendamentos.html')


@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/caixa')
def caixa():
    return render_template('admin/caixa.html')


# =====================================================================
# API – SERVIÇOS
# =====================================================================
@app.route('/api/servicos')
def api_servicos():
    servicos = Servico.query.all()
    return jsonify({
        'servicos': [
            {'id': s.id, 'nome': s.nome, 'preco': s.preco}
            for s in servicos
        ]
    })


# =====================================================================
# API – AGENDAMENTOS
# =====================================================================
@app.route('/api/agendamentos', methods=['GET', 'POST'])
def api_agendamentos():
    # -------------------------------------------------
    # CRIAR UM AGENDAMENTO
    # -------------------------------------------------
    if request.method == 'POST':
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'error': 'Dados não fornecidos'}), 400

            data = dados.get('data')
            hora = dados.get('hora')

            if not data or not hora:
                return jsonify({'error': 'Data e hora são obrigatórios'}), 400

            data_hora = datetime.strptime(f"{data} {hora}", '%Y-%m-%d %H:%M')

            # Verifica se o horário já tem agendamento
            existente = Agendamento.query.filter(
                Agendamento.data_hora == data_hora
            ).first()

            if existente:
                return jsonify({
                    'success': False,
                    'error': 'Já existe um agendamento neste horário'
                }), 409

            novo = Agendamento(
                nome=dados.get('nome'),
                telefone=dados.get('telefone'),
                servico_id=dados.get('servico_id'),
                data_hora=data_hora
            )

            db.session.add(novo)
            db.session.commit()

            servico = Servico.query.get(dados.get('servico_id'))

         
            enviar_notificacao_agendamento(
                dia=data,
                hora=hora,
                servico_nome=servico.nome if servico else 'Indefinido',
                preco=servico.preco if servico else 0.0
            )

            return jsonify({
                'success': True,
                'message': 'Agendamento criado com sucesso',
                'id': novo.id
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

  
    if request.method == 'GET':
        agendamentos = Agendamento.query \
            .filter(Agendamento.data_hora >= datetime.now()) \
            .order_by(Agendamento.data_hora) \
            .all()

        resultado = [{
            'id': ag.id,
            'nome': ag.nome,
            'telefone': ag.telefone,
            'data_hora': ag.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
            'servico': ag.servico.nome,
            'preco': float(ag.servico.preco)
        } for ag in agendamentos]

        return jsonify({'agendamentos': resultado})


@app.route('/api/agendamentos/cliente/<telefone>')
def api_agendamentos_cliente(telefone):
    telefone_limpo = ''.join(filter(str.isdigit, telefone))

    agendamentos = Agendamento.query \
        .filter(Agendamento.telefone == telefone_limpo) \
        .filter(Agendamento.data_hora >= datetime.now()) \
        .order_by(Agendamento.data_hora) \
        .all()

    resultado = [{
        'id': ag.id,
        'data_hora': ag.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
        'servico': ag.servico.nome,
        'preco': float(ag.servico.preco),
        'telefone': ag.telefone
    } for ag in agendamentos]

    return jsonify({'agendamentos': resultado})


@app.route('/api/agendamentos/<int:id>', methods=['DELETE'])
def api_cancelar_agendamento(id):
    ag = Agendamento.query.get(id)
    if not ag:
        return jsonify({'error': 'Agendamento não encontrado'}), 404

    db.session.delete(ag)
    db.session.commit()
    return jsonify({'message': 'Agendamento cancelado com sucesso'})



@app.route('/api/caixa/saldo')
def api_caixa_saldo():
    caixa = Caixa.query.first()
    if not caixa:
        caixa = Caixa(saldo=0.0)
        db.session.add(caixa)
        db.session.commit()
    return jsonify({'saldo': float(caixa.saldo)})


@app.route('/api/caixa/adicionar', methods=['POST'])
def api_caixa_adicionar():
    dados = request.get_json()

    if not dados or 'valor' not in dados:
        return jsonify({'error': 'Valor não informado'}), 400

    valor = float(dados['valor'])
    if valor <= 0:
        return jsonify({'error': 'Valor deve ser maior que zero'}), 400

    caixa = Caixa.query.first()
    if not caixa:
        caixa = Caixa(saldo=valor)
        db.session.add(caixa)
    else:
        caixa.saldo += valor

    caixa.ultima_atualizacao = datetime.now()
    db.session.commit()

    return jsonify({'success': True, 'saldo': float(caixa.saldo)})


@app.route('/api/caixa/fechar', methods=['POST'])
def api_caixa_fechar():
    caixa = Caixa.query.first()
    if not caixa:
        return jsonify({'error': 'Caixa não encontrado'}), 404

    total = float(caixa.saldo)
    caixa.saldo = 0.0
    caixa.ultima_atualizacao = datetime.now()
    db.session.commit()

    return jsonify({'success': True, 'total': total})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
