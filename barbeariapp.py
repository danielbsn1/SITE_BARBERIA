from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from datetime import datetime, date
from sqlalchemy import func # type: ignore

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    pago = db.Column(db.Boolean, default=False)

    cliente = db.relationship('Cliente', backref=db.backref('agendamentos', lazy=True))
    servico = db.relationship('Servico')

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

@app.before_request
def setup():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        if not Usuario.query.filter_by(usuario='admin').first():
            admin = Usuario(usuario='admin', senha='admin123')
            db.session.add(admin)
            db.session.commit()
        if Servico.query.count() == 0:
            s1 = Servico(nome='Corte de Cabelo', preco=30.0)
            s2 = Servico(nome='Barba', preco=20.0)
            s3 = Servico(nome='Corte + Barba', preco=45.0)
            db.session.add_all([s1, s2, s3])
            db.session.commit()
        app.db_initialized = True

@app.route('/')
def index():
    servicos = Servico.query.all()
    return render_template('index.html', servicos=servicos)

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    servicos = Servico.query.all()
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        servico_id = request.form.get('servico')
        data = request.form.get('data')
        hora = request.form.get('hora')

        if not nome or not servico_id or not data or not hora:
            flash('Por favor preencha todos os campos obrigatórios!')
            return redirect(url_for('agendar'))

        try:
            data_hora_str = f"{data} {hora}"
            data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
        except Exception:
            flash('Data ou hora inválida.')
            return redirect(url_for('agendar'))

        existe = Agendamento.query.filter_by(data_hora=data_hora).first()
        if existe:
            flash('Horário já agendado. Escolha outro horário.')
            return redirect(url_for('agendar'))

        cliente = Cliente(nome=nome, telefone=telefone)
        db.session.add(cliente)
        db.session.commit()

        agendamento = Agendamento(cliente_id=cliente.id, servico_id=servico_id, data_hora=data_hora, pago=False)
        db.session.add(agendamento)
        db.session.commit()

        return redirect(url_for('pagamento', agendamento_id=agendamento.id))
    return render_template('agendar.html', servicos=servicos, date=date)

@app.route('/agendamentos')
def agendamentos():
    # Exemplo: listar todos os agendamentos
    agendamentos = Agendamento.query.all()
    return render_template('agendamentos.html', agendamentos=agendamentos)

@app.route('/pagamento/<int:agendamento_id>', methods=['GET', 'POST'])
def pagamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    if request.method == 'POST':
        agendamento.pago = True
        db.session.commit()
        flash('Pagamento realizado com sucesso! Seu horário está confirmado.')
        return redirect(url_for('index'))
    return render_template('pagamento.html', agendamento=agendamento)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        user = Usuario.query.filter_by(usuario=usuario, senha=senha).first()
        if user:
            session['usuario'] = user.usuario
            return redirect(url_for('caixa'))
        else:
            flash('Usuário ou senha incorretos.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Desconectado com sucesso.')
    return redirect(url_for('index'))

@app.route('/caixa')
def caixa():
    if 'usuario' not in session:
        flash('É necessário fazer login para acessar essa página.')
        return redirect(url_for('login'))

    hoje = date.today()
    primeiro_dia_mes = date(hoje.year, hoje.month, 1)

    ganho_dia = db.session.query(func.sum(Servico.preco)).join(Agendamento).filter(
        Agendamento.pago == True,
        func.date(Agendamento.data_hora) == hoje
    ).scalar() or 0.0

    ganho_mes = db.session.query(func.sum(Servico.preco)).join(Agendamento).filter(
        Agendamento.pago == True,
        Agendamento.data_hora >= primeiro_dia_mes,
        func.date(Agendamento.data_hora) <= hoje
    ).scalar() or 0.0

    dias_ativos = db.session.query(func.count(func.distinct(func.date(Agendamento.data_hora)))).filter(
        Agendamento.pago == True,
        Agendamento.data_hora >= primeiro_dia_mes,
        func.date(Agendamento.data_hora) <= hoje
    ).scalar() or 1

    media_mensal = ganho_mes / dias_ativos if dias_ativos > 0 else 0.0

    return render_template('caixa.html', ganho_dia=ganho_dia, ganho_mes=ganho_mes, media_mensal=media_mensal)

@app.route('/api/horarios_disponiveis', methods=['GET'])
def horarios_disponiveis():
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({'error': 'Data não fornecida'}), 400
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Data inválida'}), 400

    horarios_possiveis = [f'{h:02d}:00' for h in range(9, 18)]

    agendamentos = Agendamento.query.filter(func.date(Agendamento.data_hora) == data).all()
    horarios_ocupados = set([ag.data_hora.strftime('%H:%M') for ag in agendamentos])
    horarios_livres = [h for h in horarios_possiveis if h not in horarios_ocupados]

    return jsonify({'horarios': horarios_livres})

if __name__ == '__main__':
    app.run(debug=True)

