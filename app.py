from flask import Flask, render_template, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy # type: ignore
from datetime import datetime,timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<Task %r>' % self.id

# for testing purpose
@app.before_first_request
def reset_db():
    db.drop_all()
    db.create_all()
    
## UI endpoints:

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)
    

## API endpoints:
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return jsonify([{"id": t.id, "content": t.content, "created": t.date_created} for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()
    if not data or not "content" in data:
        return jsonify({"error": "Content is required"}), 400
    new_task = Todo(content=data["content"])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"id": new_task.id, "content": new_task.content}), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def api_update_task(id):
    task = Todo.query.get_or_404(id)
    data = request.get_json()
    if "content" in data:
        task.content = data["content"]
    db.session.commit()
    return jsonify({"id": task.id, "content": task.content})

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def api_delete_task(id):
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
