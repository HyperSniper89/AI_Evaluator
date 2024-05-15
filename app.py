from flask import Flask, jsonify, request, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv
#from flask_cors import CORS
import os
import openai
from models import Category, db, User, Prompt, Response, Evaluation, EvaluationTask

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")
client = openai.OpenAI(api_key=api_key)  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evaluation_tool.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)



""" Helper functions """
def fetch_response_from_openai(system_message, user_message):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
            response_text = fetch_response_from_openai("System message for context", prompt.text)
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


if __name__ == '__main__':
    app.run(debug=True)

""" def prefetch_next_task_responses(task_id, user_id):
    prompts = Prompt.query.filter_by(evaluation_task_id=task_id).all()
    for prompt in prompts:
        try:
            # Fetch data directly without caching
            response_text = fetch_response_from_openai("System message for context", prompt.text)

            # Store the response in the database with a valid user_id
            new_response = Response(prompt_id=prompt.id, text=response_text, user_id=user_id)
            db.session.add(new_response)
            db.session.commit()  # Commit the response to the database

        except Exception as e:
            print(f"Error while prefetching responses: {e}")
            # Handle the error (log, retry, alert, etc.) """


""" @app.route('/fetch_prompt_response', methods=['POST'])
def fetch_prompt_response():
    data = request.json
    system_message = data['system_message']
    user_message = data['user_message']
    
    response_text = fetch_response_from_openai(system_message, user_message)
    if response_text:
        return jsonify({'response': response_text}), 200
    else:
        return jsonify({'error': 'Failed to fetch response'}), 500 """

""" # Update user information
@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    user.username = data.get('username', user.username)
    user.age = data.get('age', user.age)
    user.gender = data.get('gender', user.gender)
    user.occupation = data.get('occupation', user.occupation)
    db.session.commit()

    return jsonify({'message': 'User updated successfully', 'user': {
        'username': user.username,
        'age': user.age,
        'gender': user.gender,
        'occupation': user.occupation
    }}), 200 """