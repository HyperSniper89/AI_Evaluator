from app import app, db
from models import Category, EvaluationTask, Prompt

def add_category(name, level, topic):
    """Adds a new category or retrieves an existing one from the database."""
    category = Category.query.filter_by(name=name, level=level, topic=topic).first()
    if not category:
        category = Category(name=name, level=level, topic=topic)
        db.session.add(category)
        db.session.commit()
    return category

def create_evaluation_task(level, subject, topic, setting, is_RAG_enabled, prompts_details):
    """Creates an EvaluationTask with associated different types of prompts."""
    category = add_category(subject, level, topic)
    context = f"The appropriateness metric for these outputs should be evaluated as if they were intended for {level} students."

    task = EvaluationTask(
        category_id=category.id,
        subject=subject,
        context=context,
        is_RAG_enabled=is_RAG_enabled
    )
    db.session.add(task)
    db.session.commit()

    # Creating prompts based on the details provided
    for detail in prompts_details:
        prompt = Prompt(
            evaluation_task_id=task.id,
            text=detail['text'],
            setting=detail['setting'],
            subject=subject,
            category=category.name,
            is_RAG_enabled=detail['is_RAG_enabled']
        )
        db.session.add(prompt)
    db.session.commit()

def add_evaluation_tasks():
        topics_biology_university = ["Cellular Biology", "Genetics", "Photosynthesis"]
        topics_physics_university = ["Quantum Mechanics", "Thermodynamics", "Electromagnetism"]
        topics_biology_high_school = ["Plant Biology", "Microorganisms", "Ecosystems"]
        topics_physics_high_school = ["Mechanics", "Energy", "Magnetism"]
        # 3 University level Biology and Physics tasks
        for topic in topics_biology_university:
            create_evaluation_task("University", "Biology", topic, "Appropriateness for University students", False,
                                   [{'text': f'Explain {topic}.', 'setting': 'Neutral', 'is_RAG_enabled': False},
                                    {'text': f'You are a University teacher. Explain {topic}.', 'setting': 'Role-Based', 'is_RAG_enabled': False},
                                    {'text': f'Explain {topic} to a group of university students, in an engaging way with an example.' , 'setting': 'Contextual', 'is_RAG_enabled': False},
                                    {'text': f'You are a University teacher. Explain {topic} to a group of university students, in an engaging way with an example.', 'setting': 'Contextual', 'is_RAG_enabled': False}])

        for topic in topics_physics_university:
            create_evaluation_task("University", "Physics", topic, "Appropriateness for University students", False,
                                   [{'text': f'Explain {topic}.', 'setting': 'Neutral', 'is_RAG_enabled': False},
                                    {'text': f'You are a University teacher. Explain {topic}.', 'setting': 'Role-Based', 'is_RAG_enabled': False},
                                    {'text': f'Explain {topic} to a group of university students, in an engaging way with an example.' , 'setting': 'Contextual', 'is_RAG_enabled': False},
                                    {'text': f'You are a University teacher. Explain {topic} to a group of university students, in an engaging way with an example.', 'setting': 'Contextual', 'is_RAG_enabled': False}])

        # 3 high school Biology and Physics tasks
        for topic in topics_biology_high_school:
            create_evaluation_task("high school", "Biology", topic, "Appropriateness for 9th grade students", False,
                                   [{'text': f'Explain {topic}.', 'setting': 'Neutral', 'is_RAG_enabled': False},
                                    {'text': f'You are a high school teacher. Explain {topic}.', 'setting': 'Role-Based', 'is_RAG_enabled': False},
                                    {'text': f'Explain {topic} to a group of high school students, in an engaging way with an example.' , 'setting': 'Contextual', 'is_RAG_enabled': False},
                                    {'text': f'You are a high school teacher. Explain {topic} to a group of high school students, in an engaging way with an example.', 'setting': 'Contextual', 'is_RAG_enabled': False}])

        for topic in topics_physics_high_school:
            create_evaluation_task("high school", "Physics", topic, "Appropriateness for high school students", False,
                                   [{'text': f'Explain {topic}.', 'setting': 'Neutral', 'is_RAG_enabled': False},
                                    {'text': f'You are a high school teacher. Explain {topic}.', 'setting': 'Role-Based', 'is_RAG_enabled': False},
                                    {'text': f'Explain {topic} to a group of high school students, in an engaging way with an example.' , 'setting': 'Contextual', 'is_RAG_enabled': False},
                                    {'text': f'You are a high school teacher. Explain {topic} to a group of high school students, in an engaging way with an example.', 'setting': 'Contextual', 'is_RAG_enabled': False}])
            
def add_RAG_evaluation_tasks():
    topics_university = ["Advanced Genetics", "Advanced Mechanics"]
    topics_9th_grade = ["Basic Ecology", "Basic Physics"]

    # University Level RAG Tasks
    for topic in topics_university:
        create_evaluation_task("University", "Biology" if "Genetics" in topic else "Physics", topic, "Advanced topics at University level", True,
                               [{'text': f'Explain {topic}.', 'setting': 'General', 'is_RAG_enabled': True},
                                {'text': f'Explain {topic}.', 'setting': 'General', 'is_RAG_enabled': False}])

    # 9th Grade Level RAG Tasks
    for topic in topics_9th_grade:
        create_evaluation_task("9th grade", "Biology" if "Ecology" in topic else "Physics", topic, "Basic concepts at 9th grade level", True,
                               [{'text': f'Explain {topic}.', 'setting': 'General', 'is_RAG_enabled': True},
                                {'text': f'Explain {topic}.', 'setting': 'General', 'is_RAG_enabled': False}])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        add_evaluation_tasks()
        #add_RAG_evaluation_tasks()
