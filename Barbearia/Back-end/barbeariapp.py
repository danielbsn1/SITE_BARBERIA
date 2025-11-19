import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(BASE_DIR, 'Front-end', 'templates')
static_dir = os.path.join(BASE_DIR, 'Front-end', 'static')

app = Flask(__name__, 
    template_folder=template_dir,
    static_folder=static_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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


@app.route('/api/servicos')
def api_servicos():
    servicos = Servico.query.all()
    return jsonify({
        'servicos': [
            {'id': s.id, 'nome': s.nome, 'preco': s.preco}
            for s in servicos
        ]
    })

@app.route('/api/servicos-debug')
def api_servicos_debug():
    exemplo = [
        {'id': 1, 'nome': 'Corte de Cabelo', 'preco': 40.0},
        {'id': 2, 'nome': 'Barba', 'preco': 25.0},
        {'id': 3, 'nome': 'Sobrancelha', 'preco': 20.0}
    ]
    return jsonify({'servicos': exemplo})

@app.route('/api/agendamentos', methods=['GET', 'POST'])
def api_agendamentos():
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
            
            agendamento_existente = Agendamento.query.filter(
                Agendamento.data_hora == data_hora
            ).first()
            
            if agendamento_existente:
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
            
            return jsonify({
                'success': True,
                'message': 'Agendamento criado com sucesso',
                'id': novo.id
            })

        except Exception as e:
            db.session.rollback()
            app.logger.exception("Erro ao criar agendamento")
            return jsonify({'error': str(e)}), 500

    if request.method == 'GET':
        try:
            agendamentos = Agendamento.query\
                .filter(Agendamento.data_hora >= datetime.now())\
                .order_by(Agendamento.data_hora)\
                .all()
            
            resultado = []
            for ag in agendamentos:
                resultado.append({
                    'id': ag.id,
                    'nome': ag.nome,
                    'telefone': ag.telefone,
                    'data_hora': ag.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                    'servico': ag.servico.nome,
                    'preco': float(ag.servico.preco)
                })
            
            return jsonify({'agendamentos': resultado})
        except Exception as e:
            app.logger.exception("Erro ao listar agendamentos")
            return jsonify({'error': str(e)}), 500

@app.route('/api/agendamentos/cliente/<telefone>')
def api_agendamentos_cliente(telefone):
    try:
        app.logger.debug(f"Buscando agendamentos para telefone: {telefone}")
        
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        app.logger.debug(f"Telefone limpo: {telefone_limpo}")
        
        agendamentos = Agendamento.query\
            .filter(Agendamento.telefone == telefone_limpo)\
            .filter(Agendamento.data_hora >= datetime.now())\
            .order_by(Agendamento.data_hora)\
            .all()
        
        app.logger.debug(f"Encontrados {len(agendamentos)} agendamentos")
        
        resultado = []
        for ag in agendamentos:
            resultado.append({
                'id': ag.id,
                'data_hora': ag.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                'servico': ag.servico.nome,
                'preco': float(ag.servico.preco),
                'telefone': ag.telefone
            })
        
        return jsonify({'agendamentos': resultado})
    
    except Exception as e:
        app.logger.exception("Erro ao buscar agendamentos")
        return jsonify({
            'error': 'Erro ao buscar agendamentos',
            'details': str(e)
        }), 500

@app.route('/api/agendamentos/<int:id>', methods=['DELETE'])
def api_cancelar_agendamento(id):
    try:
        agendamento = Agendamento.query.get(id)
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        db.session.delete(agendamento)
        db.session.commit()
        
        return jsonify({'message': 'Agendamento cancelado com sucesso'})
    
    except Exception as e:
        app.logger.error(f"Erro ao cancelar agendamento: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro ao cancelar agendamento'}), 500


@app.route('/api/caixa/saldo')
def api_caixa_saldo():
    try:
        logger.debug("Buscando saldo do caixa")
        caixa = Caixa.query.first()
        if not caixa:
            logger.debug("Criando novo caixa")
            caixa = Caixa(saldo=0.0)
            db.session.add(caixa)
            db.session.commit()
        return jsonify({'saldo': float(caixa.saldo)})
    except Exception as e:
        logger.error(f"Erro ao buscar saldo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/caixa/adicionar', methods=['POST'])
def api_caixa_adicionar():
    try:
        dados = request.get_json()
        if not dados or 'valor' not in dados:
            return jsonify({'error': 'Valor não informado'}), 400
            
        valor = float(dados['valor'])
        if valor <= 0:
            return jsonify({'error': 'Valor deve ser maior que zero'}), 400

        logger.debug(f"Adicionando valor ao caixa: R$ {valor}")
        caixa = Caixa.query.first()
        if not caixa:
            caixa = Caixa(saldo=valor)
            db.session.add(caixa)
        else:
            caixa.saldo += valor
        
        caixa.ultima_atualizacao = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'saldo': float(caixa.saldo)
        })
    except Exception as e:
        logger.error(f"Erro ao adicionar valor: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/caixa/fechar', methods=['POST'])
def api_caixa_fechar():
    try:
        logger.debug("Fechando caixa")
        caixa = Caixa.query.first()
        if not caixa:
            return jsonify({'error': 'Caixa não encontrado'}), 404
        
        total = float(caixa.saldo)
        caixa.saldo = 0.0
        caixa.ultima_atualizacao = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'total': total
        })
    except Exception as e:
        logger.error(f"Erro ao fechar caixa: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


with app.app_context():

    db.drop_all()
    db.create_all()

    caixa = Caixa(saldo=0.0)
    db.session.add(caixa)

    servicos_iniciais = [
        Servico(nome='Corte de Cabelo', preco=50.00),
        Servico(nome='Barba Terapêutica', preco=30.00),
        Servico(nome='Sobrancelha', preco=15.00),
        Servico(nome='Limpeza de Pele', preco=40.00),
        Servico(nome='Corte de cabelo + Barba', preco=70.00),
        Servico(nome='Barba', preco=20.00)
    ]
    for s in servicos_iniciais:
        db.session.add(s)
 
    try:
        db.session.commit()
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao inicializar banco: {str(e)}")
        
     
if __name__ == "__main__":
    app.run()

