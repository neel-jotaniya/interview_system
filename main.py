from flask import Flask, jsonify, request
from flask_restful import Resource, Api 
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from model import chat, create_finance_model, create_hr_model, correct_grammar
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "winter_is_coming" 

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app)
CORS(app)
user_list = []

class User():
    def __init__(self, username) -> None:
        self.username = username
        self.hr = None
        self.finance = None
        self.ielts = None
        self.mode_dict={
            'hr':self.hr,
            'finance':self.finance,
            'ielts':self.ielts
        }
        
    def __str__(self):
        return f"User: {self.username}"
        
    def chat(self, mode):
        self.conversion_mode = self.mode_dict[mode]
        if not self.conversion_mode:
            self.conversion_mode = self.start_conversion(mode)
        return self.conversion_mode
    
    @classmethod
    def start_conversion(cls, mode):
        if mode == 'hr':
            return create_hr_model()
        elif mode == 'finance':
            return create_finance_model()
        
    @classmethod
    def find_user(cls, username):
        user = next((user for user in user_list if user.username == username), None)
        if not user:
            user = User(username=username)
            user_list.append(user)
        return user
        

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    
    def __init__(self,username,password):
        self.username = username
        self.password = password
 
    @classmethod
    def find_by_username(cls, username :str):
        return cls.query.filter_by(username = username).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def check_password(self, password):
        return self.password == password
    
    
class Login(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = UserModel.find_by_username(username)
        if user:
            if user.check_password(password):
                access_token = create_access_token(identity=username)
                return jsonify(access_token=access_token)
            else:
                return jsonify({'message':'password is invalid'})
        else:
            return jsonify({'message':'user is not exist'})
        
        
class PracticeRound(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json()
        print(data)
        if data['option'] == 'grammar':
            return jsonify({'data':correct_grammar(data['message'])})
        else:
            return jsonify({'data':correct_grammar(data['message'])})
        
        
class Useregister(Resource):
    @cross_origin()
    @jwt_required()
    def post(self):
        data = request.get_json()
        if UserModel.find_by_username(data['username']):
            print(user_list)
            return {"message": "user already exists"}

        user = UserModel(**data)
        user.save_to_db()
        print(user_list)
        return jsonify({"message" : "user add successfully"})

class Interview(Resource):
    @cross_origin()
    @jwt_required()
    def post(self, username, mode):            
        user = User.find_user(username)
        data = request.get_json()
        message = data['message']
        return jsonify({"message":chat(user.chat(mode), input=message)})
        
    
api.add_resource(PracticeRound, '/pr')
api.add_resource(Useregister,'/register')
api.add_resource(Login,'/login')
api.add_resource(Interview, '/interview/<string:username>/<string:mode>')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
            
        


