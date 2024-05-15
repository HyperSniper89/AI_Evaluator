from app import app, db
from models import Category, EvaluationTask, Prompt

def add_evaluation_tasks():
    with app.app_context():
        try:
            explain, reason = Category.query.filter_by(name='explain').first(), Category.query.filter_by(name='reason').first()
            
            if not explain:
                explain = Category(name="explain")
                db.session.add(explain)

            if not reason:
                reason = Category(name="reason")
                db.session.add(reason)

            db.session.commit()  # Commit the categories first

            """ tasks = [
                EvaluationTask(category=explain, subject="Photosynthesis", context="High school biology class"),
                EvaluationTask(category=explain, subject="Cellular Respiration", context="College biology course"),
                EvaluationTask(category=reason, subject="Why is the sky blue", context="General curiosity"),
                EvaluationTask(category=reason, subject="How does gravity work", context="Physics class in college")
            ] """

            tasks = [
                EvaluationTask(category=explain, subject="what is 4+4?", context="High school biology class"),
                EvaluationTask(category=explain, subject="what is 4+7?", context="College biology course"),
                EvaluationTask(category=reason, subject="what is 4+6?", context="General curiosity"),
                EvaluationTask(category=reason, subject="Hwhat is 4+5?", context="Physics class in college")
            ]
            db.session.add_all(tasks)
            db.session.commit()  # Commit the evaluation tasks

            
            prompt_templates = {
                "third_grade": "You are a third grade teacher. Explain {subject}",
            }
            
            """ prompt_templates = {
                "third_grade": "You are a third grade teacher. Explain {subject} as you would to a third grade student.",
                "college": "You are a college teacher. Explain {subject} as you would to a college class student.",
                "non_specific": "Explain {subject}."
            } """

            for task in tasks:
                for intent, template in prompt_templates.items():
                    prompt_text = template.format(subject=task.subject)
                    prompt = Prompt(
                        evaluation_task=task,
                        text=prompt_text,
                        setting=task.context,
                        subject=task.subject,
                        category=task.category.name,
                        intent=intent
                    )
                    db.session.add(prompt)
            
            db.session.commit()  # Final commit for all prompts

        except Exception as e:
            db.session.rollback()  # Roll back in case of error
            print("Error in add_evaluation_tasks:", e)  # Log the error


# Run the function to add evaluation tasks
if __name__ == "__main__":
    add_evaluation_tasks()