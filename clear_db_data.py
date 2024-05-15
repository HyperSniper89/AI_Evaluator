from app import app  # Import the Flask app instance
from app import db  # Import the database setup
from sqlalchemy import text  # Import text for raw SQL execution
from models import User, Category, EvaluationTask, Prompt, Response, Evaluation  # Import models

def clear_data():
    with app.app_context():  # Use the app context
        try:
            # Disable foreign key constraints for SQLite
            if db.engine.url.drivername == 'sqlite':
                db.session.execute(text('PRAGMA foreign_keys = OFF;'))

            # Delete data from tables
            Evaluation.query.delete()
            Response.query.delete()
            Prompt.query.delete()
            EvaluationTask.query.delete()
            Category.query.delete()
            User.query.delete()
            
            db.session.commit()
            print("All data has been deleted successfully.")

            # Re-enable foreign key constraints for SQLite
            if db.engine.url.drivername == 'sqlite':
                db.session.execute(text('PRAGMA foreign_keys = ON;'))

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    clear_data()
