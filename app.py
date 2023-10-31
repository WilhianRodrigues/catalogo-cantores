from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/cante'
app.secret_key = 'secreta'
db = SQLAlchemy(app)

class Usuario(db.Model):
    __usuario__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True)
    senha = db.Column(db.String(255))
    tipo = db.Column(db.String(255))
    email = db.Column(db.String(255))

    # Relacionamento com Cantor
    cantor = db.relationship('Cantor', backref='usuario', uselist=False)

    # Relacionamento com Contratante
    contratante = db.relationship('Contratante', backref='usuario', uselist=False)

    def __init__(self, login, senha, tipo, email):
        self.login = login
        self.senha = senha
        self.tipo = tipo
        self.email = email

class Cantor(db.Model):
    __cantor__ = "cantor"
    id_cantor = db.Column(db.Integer, primary_key=True)
    foto_perfil = db.Column(db.String(500))
    nome = db.Column(db.String(255))
    idade = db.Column(db.Integer)
    localidade = db.Column(db.String(255))
    celular = db.Column(db.String(255))
    email = db.Column(db.String(255))
    disponibilidade = db.Column(db.String(255))
    nota = db.Column(db.Float)
    valor_medio = db.Column(db.Float)
    sobre = db.Column(db.String(255))
    qnt_nota = db.Column(db.Float)
    id_usuario = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), unique=True)

    def __init__(self, foto_perfil, nome, idade, localidade, celular, email, disponibilidade, nota, valor_medio, sobre, qnt_nota, id_usuario):
        self.foto_perfil = foto_perfil
        self.nome = nome
        self.idade = idade
        self.localidade = localidade
        self.celular = celular
        self.email = email
        self.disponibilidade = disponibilidade
        self.nota = nota
        self.valor_medio = valor_medio
        self.sobre = sobre
        qnt_nota = qnt_nota
        self.id_usuario = id_usuario

class Contratante(db.Model):
    __contratante__ = "contratante"
    id_contratante = db.Column(db.Integer, primary_key=True)
    foto_perfil = foto_perfil = db.Column(db.String(500))
    nome = db.Column(db.String(255))
    localidade = db.Column(db.String(255))
    celular = db.Column(db.String(255))
    email = db.Column(db.String(255))
    nota = db.Column(db.Float)
    sobre = db.Column(db.String(255))
    id_usuario = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), unique=True)

    def __init__(self, foto_perfil, nome, localidade, celular, email, nota, sobre, id_usuario):
        self.foto_perfil = foto_perfil
        self.nome = nome
        self.localidade = localidade
        self.celular = celular
        self.email = email
        self.nota = nota
        self.sobre = sobre 
        self.id_usuario = id_usuario

@app.route('/')
def index():
    db.create_all()
    return redirect(url_for('login'))

# aqui é referente ao catalogo
@app.route('/catalogo')
def catalogo():
    cantores = Cantor.query.all()
    melhores = Cantor.query.order_by(Cantor.nota.desc()).limit(3).all()
    print(melhores)
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    return render_template('catalogo.html', cantores=cantores, melhores=melhores)


@app.route('/perfil_cantor/<int:id_cantor>', methods=['GET', 'POST'])
def catalogo_cantor(id_cantor):
    
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))

    cantor = Cantor.query.filter(
        Cantor.id_cantor == id_cantor
    ).all()

    for e in cantor:  
        if request.method == 'POST':
            e.nota = (e.nota + float(request.form['nota']))
            e.qnt_nota = e.qnt_nota + 1
            db.session.commit()

        valor_notas = (e.nota / e.qnt_nota)
        valor_notas = round(valor_notas, 2)

    return render_template('perfil_cantor.html', cantor=cantor, valor_notas=valor_notas)

# aqui é referente a edicao de perfis \/
@app.route('/redireciona_perfil')
def redireciona_perfil():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))

    usuario = Usuario.query.filter(
        Usuario.id_usuario == session['usuario_logado']
    ).all()
    
    for e in usuario:
        if e.tipo == "cantor":
            return redirect(url_for('editar_perfil_cantor'))
        if e.tipo == "contratante":
            return redirect(url_for('editar_perfil_contratante'))

    return redirect(url_for('catalogo'))

# aqui é referente a criação do perfil do cantor \/
@app.route('/perfil_cantor')
def perfil_cantor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    cantor = Cantor.query.filter(
        Cantor.id_usuario == session['usuario_logado']
    ).all()
    return render_template('perfil_cantor.html', cantor=cantor)

@app.route('/editar_perfil_cantor', methods=['GET', 'POST'])
def editar_perfil_cantor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login')) 
    
    cantor = Cantor.query.filter(
        Cantor.id_usuario == session['usuario_logado']
    ).all()

    conta = Usuario.query.filter(
    Usuario.id_usuario == session['usuario_logado']
        ).all()

    for n in conta:
        if (n.tipo != 'cantor'):
            flash('Sem permissão!')

            return render_template('index')

    cantor_edit = Cantor.query.get(1)

    if request.method == 'POST':
        cantor_edit.nome = request.form['nome']
        cantor_edit.idade = request.form['idade']
        cantor_edit.localidade = request.form['localidade']
        cantor_edit.celular = request.form['celular']
        cantor_edit.foto_perfil = request.form['foto_perfil']
        cantor_edit.email = request.form['email']
        cantor_edit.disponibilidade = request.form['disponibilidade']
        cantor_edit.valor_medio = request.form['valor_medio']
        cantor_edit.sobre = request.form['sobre']
        db.session.commit()

        return redirect(f"/perfil_cantor")

    return render_template('editar_perfil_cantor.html', cantor=cantor)

# aqui é referente a criação do perfil do contratante \/
@app.route('/perfil_contratante')
def perfil_contratante():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    contratante = Contratante.query.filter(
        Contratante.id_usuario == session['usuario_logado']
    ).all()
    return render_template('perfil_contratante.html', contratante=contratante)

@app.route('/editar_perfil_contratante', methods=['GET', 'POST'])
def editar_perfil_contratante():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login')) 
    
    contratante = Contratante.query.filter(
        Contratante.id_usuario == session['usuario_logado']
    ).all()

    contratante_edit = Contratante.query.get(1)

    if request.method == 'POST':
        contratante_edit.nome = request.form['nome']
        contratante_edit.localidade = request.form['localidade']
        contratante_edit.celular = request.form['celular']
        contratante_edit.email = request.form['email']
        contratante_edit.foto_perfil = request.form['foto_perfil']
        contratante_edit.sobre = request.form['sobre']

        db.session.commit()

        return redirect(f"/perfil_contratante")

    return render_template('editar_perfil_contratante.html', contratante=contratante)

# aqui é referente ao login \/
@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        try:
            cadastro = Usuario(request.form['login'], request.form['senha'],
                            request.form['tipo'], request.form['email'])
            db.session.add(cadastro)
            db.session.commit()

            login = request.form['login']
            usuario = Usuario.query.filter(Usuario.login == login).first()

            if request.form['tipo'] == 'cantor':
                cantor = Cantor('Foto perfil.txt', request.form['login'], 45, 'Brasilia', '00 0000-0000', request.form['email'], 'todos', 5, 50.2, 'sobre', 1, usuario.id_usuario)
                db.session.add(cantor)
                db.session.commit()

            if request.form['tipo'] == 'contratante':
                contratante = Contratante('Foto perfil.txt', request.form['login'], 'localidade', '61 0000-0000', request.form['email'], 5, 'sobre', usuario.id_usuario)
                db.session.add(contratante)
                db.session.commit()

            flash('Usuário cadastrado com sucesso!')
            return redirect('/login')
        except Exception as e:
            flash(f'Ocorreu um erro ao cadastrar: {str(e)}')

    return render_template('cadastrar.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    if request.method == 'POST':
        try:
            login = request.form['login']
            senha = request.form['senha']
            usuario = Usuario.query.filter(and_(
                Usuario.login == login,
                Usuario.senha == senha)).first()

            if usuario is not None:
                session['usuario_logado'] = usuario.id_usuario
                flash(f'{login} logou com sucesso!')
                return redirect('/catalogo')
            else:
                flash("Usuário ou senha incorretos")
        except Exception as e:
            flash(f"Ocorreu um erro ao autenticar: {str(e)}")

    return render_template("login.html")


@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
