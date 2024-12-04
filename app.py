from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from sqlalchemy import text  # Import necessário para consultas textuais explícitas
import base64



# Configurações do Flask
app = Flask(__name__)
CORS(app)

# Configurações do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://xupeta:bigbig83121790@projeto-mysql.cp8iawgsqg45.us-east-2.rds.amazonaws.com:3306/projeto_faculdade'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o SQLAlchemy
db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False)

class Denuncia(db.Model):
    __tablename__ = 'denuncias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    localizacao = db.Column(db.String(255), nullable=False)
    tipo_lixo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    imagem = db.Column(db.LargeBinary, nullable=True)
    status = db.Column(db.Enum('enviado', 'iniciado', 'finalizado'), default='enviado', nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())


# Criação do Banco de Dados (Executar uma vez)
with app.app_context():
    db.create_all()

# Rotas de Páginas (Frontend)

# Página principal: Login
@app.route('/')
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('criar.html')


# Página de logout
@app.route('/logout')
def logout_page():
    return render_template('logout.html')

@app.route('/denuncia')
def denuncia_page():
    return render_template('denuncia.html')

@app.route('/logs')
def logs_page():
    return render_template('log.html')

@app.route('/coletor')
def coletor_page():
    return render_template('coletor.html')




import base64

@app.route('/logs/<int:user_id>', methods=['GET'])
def get_user_logs(user_id):
    try:
        denuncias = Denuncia.query.filter_by(user_id=user_id).all()
        logs = [
            {
                "id": denuncia.id,
                "localizacao": denuncia.localizacao,
                "descricao": denuncia.descricao,
                "status": denuncia.status,  # Agora inclui o status
                "data_criacao": denuncia.data_criacao.strftime("%d/%m/%Y %H:%M:%S"),
                "imagem": base64.b64encode(denuncia.imagem).decode('utf-8') if denuncia.imagem else None
            }
            for denuncia in denuncias
        ]
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar logs.", "error": str(e)}), 500

    
    

# Cadastro de usuário
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data['email']
    senha = data['password']
    telefone = data['phone_number']
    tipo_usuario = data['user_type']

    # Gera hash da senha
    senha_hashed = generate_password_hash(senha)

    try:
        # Verifica se o email já está cadastrado
        if Usuario.query.filter_by(email=email).first():
            return jsonify({"message": "Email já cadastrado."}), 400

        # Cria um novo usuário
        novo_usuario = Usuario(email=email, senha=senha_hashed, telefone=telefone, tipo_usuario=tipo_usuario)
        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar usuário.", "error": str(e)}), 500

# Login de usuário
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data['email']
    senha = data['password']

    try:
        # Busca o usuário pelo email
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            return jsonify({
                "message": "Login realizado com sucesso!",
                "user": {
                    "id": usuario.id,
                    "tipo_usuario": usuario.tipo_usuario
                }
            }), 200
        else:
            return jsonify({"message": "Email ou senha inválidos."}), 401
    except Exception as e:
        return jsonify({"message": "Erro ao realizar login.", "error": str(e)}), 500

    

@app.route('/report', methods=['POST'])
def report_issue():
    user_id = request.form.get('user_id')
    localizacao = request.form.get('localizacao')
    tipo_lixo = request.form.get('tipoLixo')
    descricao = request.form.get('descricao')
    imagem = request.files['imagem'].read() if 'imagem' in request.files else None

    try:
        nova_denuncia = Denuncia(
            user_id=user_id,
            localizacao=localizacao,
            tipo_lixo=tipo_lixo,
            descricao=descricao,
            imagem=imagem
        )
        db.session.add(nova_denuncia)
        db.session.commit()
        return jsonify({"message": "Denúncia cadastrada com sucesso!"}), 201
    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar denúncia.", "error": str(e)}), 500
    
@app.route('/denuncias', methods=['GET'])
def get_denuncias():
    try:
        denuncias = Denuncia.query.all()
        result = [
            {
                "id": denuncia.id,
                "localizacao": denuncia.localizacao,
                "descricao": denuncia.descricao,
                "status": denuncia.status,
                "imagem": base64.b64encode(denuncia.imagem).decode('utf-8') if denuncia.imagem else None
            }
            for denuncia in denuncias
        ]
        return jsonify({"denuncias": result}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar denúncias.", "error": str(e)}), 500
    
@app.route('/update-denuncias-status', methods=['PUT'])
def update_denuncias_status():
    data = request.get_json()
    ids = data.get('ids', [])
    novo_status = data.get('status')

    if not ids or novo_status not in ['enviado', 'iniciado', 'finalizado']:
        return jsonify({"message": "Dados inválidos."}), 400

    try:
        denuncias = Denuncia.query.filter(Denuncia.id.in_(ids)).all()
        for denuncia in denuncias:
            denuncia.status = novo_status
        db.session.commit()
        return jsonify({"message": "Status atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao atualizar status.", "error": str(e)}), 500
    
    




# Inicialização do servidor
if __name__ == "__main__":
    app.run(port=5000, debug=True)
