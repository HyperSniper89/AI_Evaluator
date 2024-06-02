from app import app, db  
from models import User, Category, EvaluationTask, Prompt, Response, Evaluation

def add_dummy_data():
    # Create an application context
    with app.app_context():
        # Clear existing data
        """ db.drop_all()
        db.create_all() """

        # Add categories
        category1 = Category(name="explain")
        category2 = Category(name="reason")

        # Addding users
        user1 = User(username="evaluator1", age=30, gender="Female", occupation="Researcher")
        user2 = User(username="evaluator2", age=35, gender="Male", occupation="Educator")

        # evaluation tasks
        task1 = EvaluationTask(category=category1, subject="Photosynthesis", context="High school biology class")
        task2 = EvaluationTask(category=category2, subject="Quantum Mechanics", context="College physics class")

        # prompts
        prompt1 = Prompt(evaluation_task=task1, text="Explain how photosynthesis works in plants.", setting="Classroom", subject="Biology", category="explain", intent="high school level")
        prompt2 = Prompt(evaluation_task=task2, text="Describe the basic principles of quantum mechanics.", setting="Lecture Hall", subject="Physics", category="reason", intent="college level")

        # responses
        response1 = Response(prompt=prompt1, text="Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water.")
        response2 = Response(prompt=prompt2, text="Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles.")

        # evaluations
        evaluation1 = Evaluation(response=response1, user=user1, evaluator_type="Human", correctness=5, relevance=5, appropriateness=5, clarity=5, noanswer=False)
        evaluation2 = Evaluation(response=response2, user=user2, evaluator_type="Human", correctness=4, relevance=4, appropriateness=4, clarity=4, noanswer=False)

        # commit all to database
        db.session.add_all([category1, category2, user1, user2, task1, task2, prompt1, prompt2, response1, response2, evaluation1, evaluation2])
        db.session.commit()

        print("Dummy data added successfully!")

if __name__ == '__main__':
    add_dummy_data()
