from flask import Flask
from main import main_task  # Import your task from main.py

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World!"

@app.route('/run_task')  # A new route to trigger the automation task
def run_task():
    try:
        main_task()  # This will call your automation task
        return "Task completed successfully!"
    except Exception as e:
        return f"Error occurred: {e}"

if __name__ == '__main__':
    app.run()
