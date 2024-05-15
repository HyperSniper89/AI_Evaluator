
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    occupation = db.Column(db.String(80), nullable=False)
    last_task_id = db.Column(db.Integer, db.ForeignKey('evaluation_task.id', name='fk_user_last_task_id'), nullable=True)

class EvaluationTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    context = db.Column(db.Text, nullable=False)
    is_RAG_enabled = db.Column(db.Boolean, default=False, nullable=False)
    prompts = db.relationship('Prompt', backref='evaluation_task', lazy='dynamic')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  # e.g., Biology, Physics
    level = db.Column(db.String(255), nullable=False)  # e.g., University, High School
    topic = db.Column(db.String(255), nullable=True)  # e.g., Photosynthesis, Gravity
 
class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evaluation_task_id = db.Column(db.Integer, db.ForeignKey('evaluation_task.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    setting = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    is_RAG_enabled = db.Column(db.Boolean, default=False, nullable=False)

class Response(db.Model):
    __tablename__ = 'response'
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id', name='fk_response_prompt_id'), nullable=False)
    prompt = db.relationship('Prompt', backref=db.backref('responses', lazy=True))
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_response_user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('responses', lazy=True))
    
class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=False)
    response = db.relationship('Response', backref=db.backref('evaluations', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='evaluations')
    evaluator_type = db.Column(db.String(50), nullable=False)  # 'Human' or 'AI_ModelName'
    correctness = db.Column(db.Integer, nullable=True)
    relevance = db.Column(db.Integer, nullable=True)
    appropriateness = db.Column(db.Integer, nullable=True)
    clarity = db.Column(db.Integer, nullable=True)
    noanswer = db.Column(db.Boolean, default=False)
