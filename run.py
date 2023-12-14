from app import create_app

gunicorn run:app
app = create_app()
