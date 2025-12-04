from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_super_segura_2024_estoque_v1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== MODELOS DO BANCO DE DADOS ====================

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('Item', backref='owner', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'username': self.username,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M')
        }


class Item(db.Model):
    __tablename__ = 'item'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    item_type = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'item_type': self.item_type,
            'quantity': self.quantity,
            'value': self.value,
            'total': self.quantity * self.value,
            'created_at': self.created_at.strftime('%d/%m/%Y'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M')
        }


with app.app_context():
    db.create_all()


# ==================== FUNÇÕES AUXILIARES ====================

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_username(username):
    pattern = r'^[a-zA-Z0-9_]{3,}$'
    return re.match(pattern, username) is not None


# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/registro')
def registro():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('registro.html')


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()

        if not all([username, password, full_name, email]):
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos'}), 400

        if len(password) < 6:
            return jsonify({'error': 'A senha deve ter no mínimo 6 caracteres'}), 400

        if not validar_email(email):
            return jsonify({'error': 'Email inválido'}), 400

        if not validar_username(username):
            return jsonify({'error': 'Nome de usuário inválido. Use apenas letras, números e underscore (mínimo 3 caracteres)'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Nome de usuário já existe'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email já cadastrado'}), 400

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            username=username,
            password=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao registrar: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': 'Usuário ou senha inválidos'}), 401

        session['user_id'] = user.id
        session['username'] = user.username
        session['full_name'] = user.full_name

        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao fazer login: {str(e)}'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200


@app.route('/api/perfil', methods=['GET'])
def get_perfil():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    return jsonify(user.to_dict()), 200


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')


# ==================== ROTAS DE ITENS/ESTOQUE ====================

@app.route('/api/items', methods=['GET'])
def get_items():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    items = Item.query.filter_by(user_id=session['user_id']).all()
    total_value = sum(item.quantity * item.value for item in items)
    total_quantity = sum(item.quantity for item in items)

    return jsonify({
        'items': [item.to_dict() for item in items],
        'total_value': total_value,
        'total_quantity': total_quantity,
        'total_items_count': len(items)
    }), 200


@app.route('/api/items', methods=['POST'])
def add_item():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        item_type = data.get('item_type', '').strip()
        quantity = data.get('quantity')
        value = data.get('value')

        if not all([name, item_type, quantity, value]):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

        try:
            quantity = int(quantity)
            value = float(value)
        except ValueError:
            return jsonify({'error': 'Quantidade e valor devem ser números'}), 400

        if quantity <= 0:
            return jsonify({'error': 'Quantidade deve ser maior que zero'}), 400

        if value < 0:
            return jsonify({'error': 'Valor não pode ser negativo'}), 400

        item = Item(
            user_id=session['user_id'],
            name=name,
            item_type=item_type,
            quantity=quantity,
            value=value
        )
        
        db.session.add(item)
        db.session.commit()

        return jsonify(item.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao adicionar item: {str(e)}'}), 500


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    item = Item.query.filter_by(id=item_id, user_id=session['user_id']).first()
    if not item:
        return jsonify({'error': 'Item não encontrado'}), 404

    return jsonify(item.to_dict()), 200


@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    try:
        item = Item.query.filter_by(id=item_id, user_id=session['user_id']).first()
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404

        data = request.get_json()
        
        if 'name' in data:
            item.name = data['name'].strip()
        if 'item_type' in data:
            item.item_type = data['item_type'].strip()
        if 'quantity' in data:
            quantity = int(data['quantity'])
            if quantity <= 0:
                return jsonify({'error': 'Quantidade deve ser maior que zero'}), 400
            item.quantity = quantity
        if 'value' in data:
            value = float(data['value'])
            if value < 0:
                return jsonify({'error': 'Valor não pode ser negativo'}), 400
            item.value = value

        item.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify(item.to_dict()), 200

    except ValueError:
        return jsonify({'error': 'Dados inválidos'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar item: {str(e)}'}), 500


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    try:
        item = Item.query.filter_by(id=item_id, user_id=session['user_id']).first()
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({'message': 'Item deletado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar item: {str(e)}'}), 500


# ==================== ROTAS DE RELATÓRIOS ====================

@app.route('/api/relatorio/resumo', methods=['GET'])
def relatorio_resumo():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    items = Item.query.filter_by(user_id=session['user_id']).all()
    
    total_value = sum(item.quantity * item.value for item in items)
    total_quantity = sum(item.quantity for item in items)
    
    tipos = {}
    for item in items:
        if item.item_type not in tipos:
            tipos[item.item_type] = {
                'quantidade': 0,
                'valor_total': 0,
                'itens': 0
            }
        tipos[item.item_type]['quantidade'] += item.quantity
        tipos[item.item_type]['valor_total'] += item.quantity * item.value
        tipos[item.item_type]['itens'] += 1

    return jsonify({
        'total_value': total_value,
        'total_quantity': total_quantity,
        'total_items_count': len(items),
        'tipos': tipos
    }), 200


# ==================== PÁGINAS DE ERRO ====================

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return jsonify({'error': 'Página não encontrada'}), 404


@app.errorhandler(500)
def erro_servidor(error):
    db.session.rollback()
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Sistema de Estoque iniciado!")
    print("="*60)
    print("📍 Acesse em: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
