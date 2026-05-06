#from app import create_app,db
#app = create_app()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS


app = Flask(__name__)

CORS(app, 
     resources={r"/api/*": {"origins": "http://localhost:5173"}}, 
     supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)
migrate = Migrate(app, db) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

if __name__ == '__main__':
    app.run(debug=True)
