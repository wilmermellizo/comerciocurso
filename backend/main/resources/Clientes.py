from flask_restful import Resource
from flask import jsonify, request
from .. import db
from main.models import UsuarioModel
from flask_jwt_extended import current_user, get_jwt_identity
from main.auth.decorators import role_required

class Cliente(Resource):

    @role_required(roles=["admin", "cliente"])
    def get(self, id):
        cliente = db.session.query(UsuarioModel).get_or_404(id)
        current_user = get_jwt_identity()
        if cliente.role == 'cliente':
            if current_user['usuarioId'] == cliente.id or current_user['role'] == 'admin':
                return cliente.to_json()
            else:
                return 'Unauthorized', 401

        else:
            return '', 404
    
    @role_required(roles=["cliente"])    
    def delete(self,id):
        cliente = db.session.query(UsuarioModel).get_or_404(id)
        current_user = get_jwt_identity()
        if cliente.role == 'cliente' and current_user['usuarioId'] == cliente.id:
            try:
                db.session.delete(cliente)
                db.session.commit()
                return '', 204
            except:
                return '', 404
        else:
            return 'Unauthorized', 401

    @role_required(roles=["cliente"])     
    def put(self, id):
        cliente = db.session.query(UsuarioModel).get_or_404(id)
        current_user = get_jwt_identity()
        if cliente.role == 'cliente' and current_user['usuarioId'] == cliente.id:
            data = request.get_json().items()
            for key, value in data:
                setattr(cliente, key, value)
            try:
                db.session.add(cliente)
                db.session.commit()
                return cliente.to_json(), 201 
            except:
                return '', 404
        else:
            return 'Unauthorized', 401    

class Clientes(Resource):

    @role_required(roles=["admin"])
    def get(self):
        page = 1
        per_page = 5
        clientes = db.session.query(UsuarioModel).filter(UsuarioModel.role == 'cliente')  
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = int(value)
                elif key == 'per_page':
                    per_page = int(value)
        clientes = clientes.paginate(page, per_page, True, 10)
        return jsonify({        
            'clientes': [cliente.to_json() for cliente in clientes.items],
            'total': clientes.total,
            'pages': clientes.pages,
            'page': page
        })
    
    def post(self):
        cliente = UsuarioModel.from_json(request.get_json())
        cliente.role = 'cliente'
        db.session.add(cliente)
        db.session.commit()
        return cliente.to_json(), 201
