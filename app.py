from flask import Flask, jsonify, request, render_template
import pymysql
from flask_cors import CORS
from dotenv import load_dotenv
import os
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import openai
from models import Category, User, Prompt, Response, Evaluation, EvaluationTask, db



project_id = "promptevaluator"
def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')
    
openai_api_key = get_secret(project_id, "OPENAI_API_KEY")
secret_key = get_secret(project_id, "SECRET_KEY")
client = openai.OpenAI(api_key=openai_api_key)


app = Flask(__name__)
CORS(app)

connector = Connector()
# function to return the database connection
def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "promptevaluator:europe-west2:cloud-evaluator-db",
        "pymysql",
        user="HyperSniper",
        password=get_secret(project_id, "DB_PASSWORD"),
        db="evaluation_db"
    )
    return conn

# create connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'creator': getconn
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

#db = SQLAlchemy(app)

db.init_app(app)


""" Helper functions """
def fetch_response_from_openai(system_message, user_message):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        generated_text = completion.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        print(f"An error occurred whole fetching data from AI API: {e}")
        return None


""" Routes """
#fetches prompt outputs from openai
@app.route('/get_evaluation_task/<int:task_id>')
def get_evaluation_task(task_id):
    user_id = request.args.get('user_id') 
    task = EvaluationTask.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    prompts = Prompt.query.filter_by(evaluation_task_id=task.id).all()
    responses = []

    for prompt in prompts:
        # Fetch the response from the database or OpenAI
        existing_response = Response.query.filter_by(prompt_id=prompt.id, user_id=user_id).first()
        if existing_response:
            response_text = existing_response.text
        else:
            try:
                response_text = fetch_response_from_openai("System message for context", prompt.text)
            except Exception as e:
                response_text = 'Error fetching response: ' + str(e)
            # Store new response in the database
            new_response = Response(prompt_id=prompt.id, text=response_text, user_id=user_id)
            db.session.add(new_response)
            db.session.commit()

        responses.append({'prompt_id': prompt.id, 'response_text': response_text})

    return jsonify({
        'task_id': task.id,
        'context': task.context,
        'subject': task.subject,
        'responses': responses,
        'more_tasks': EvaluationTask.query.get(task_id + 1) is not None
    }), 200


@app.route('/')
def user_submition_page():
    return render_template('index.html')

@app.route('/completion')
def completion_page():
    return render_template('completion.html')

@app.route('/instructions')
def instructions_page():
    return render_template('instructions.html')

@app.route('/evaluation')
def evaluation_page():
    return render_template('evaluation.html')

    
@app.route('/submit_user', methods=['POST'])
def submit_user():
    data = request.json
    user = User(username=data['username'], age=data['age'], gender=data['gender'], occupation=data['occupation'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User added successfully', 'user_id': user.id}), 201

@app.route('/submit_evaluation', methods=['POST'])
def submit_evaluation():
    data = request.json
    evaluations = data.get('evaluations', [])

    # Check if evaluations array is not empty
    if not evaluations:
        return jsonify({'message': 'No evaluations provided'}), 400

    # Loop through each evaluation and validate required fields
    for evaluation in evaluations:
        response_id = evaluation.get('response_id')
        evaluator_type = evaluation.get('evaluator_type')

        if not response_id or not evaluator_type:
            return jsonify({'message': 'Response ID and evaluator type are required'}), 400

        user_id = evaluation.get('user_id')  # This could be optional
        correctness = evaluation.get('correctness', None)
        relevance = evaluation.get('relevance', None)
        appropriateness = evaluation.get('appropriateness', None)
        clarity = evaluation.get('clarity', None)
        noanswer = evaluation.get('noanswer', False)

        # Create and store the evaluation
        new_evaluation = Evaluation(
            response_id=response_id,
            user_id=user_id,
            evaluator_type=evaluator_type,
            correctness=correctness,
            relevance=relevance,
            appropriateness=appropriateness,
            clarity=clarity,
            noanswer=noanswer
        )

        db.session.add(new_evaluation)

    # Commit the session to save all evaluations to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({'message': 'Error submitting evaluations', 'error': str(e)}), 500

    return jsonify({'message': 'Evaluations submitted successfully'}), 201



@app.route('/get_current_task', methods=['GET'])
def get_current_task():
    task_id = request.args.get('task_id', type=int)
    user_id = request.args.get('user_id', type=int)

    if not task_id or not user_id:
        return jsonify({'error': 'Task ID or User ID is missing'}), 400

    # Fetch the task with a join to include category details
    task = EvaluationTask.query \
        .join(Category, EvaluationTask.category_id == Category.id) \
        .add_columns(EvaluationTask.id, EvaluationTask.context, EvaluationTask.subject, Category.topic) \
        .filter(EvaluationTask.id == task_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    prompts = Prompt.query.filter_by(evaluation_task_id=task_id).all()
    responses = []
    for prompt in prompts:
        response = Response.query.filter_by(prompt_id=prompt.id, user_id=user_id).first()
        if response:
            responses.append({'prompt_id': prompt.id, 'response_text': response.text})
        else:
            responses.append({'prompt_id': prompt.id, 'response_text': 'No response available'})

    # Return the data with the topic field
    return jsonify({
        'task_id': task.id,
        'context': task.context,
        'subject': task.subject,
        'topic': task.topic,  # This line sends the topic info to the frontend
        'responses': responses,
        'more_tasks': len(responses) > 0
    })


""" db_user = os.environ.get('CLOUD_SQL_USERNAME')
if not db_user: raise EnvironmentError('CLOUD_SQL_USERNAME environment variable not set')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
if not db_password: raise EnvironmentError('CLOUD_SQL_PASSWORD environment variable not set')
db_name = os.environ.get('CLOUD_SQL_DATABASE')
if not db_name: raise EnvironmentError('CLOUD_SQL_DATABASE environment variable not set')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
if not db_connection_name: raise EnvironmentError('CLOUD_SQL_CONNECTION_NAME environment variable not set')
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key: raise EnvironmentError('OPENAI_API_KEY environment variable not set') """

""" def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user,
                                password=db_password, 
                                unix_socket=unix_socket,
                                db=db_name,
                                cursorclass=pymysql.cursors.DictCursor
                                )
    except pymysql.MySQLError as e:
            return e
    return conn """

""" load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables") 
client = openai.OpenAI(api_key=api_key)  """



if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

