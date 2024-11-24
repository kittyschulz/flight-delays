from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #Need to change this to our actual db
db = SQLAlchemy(app)

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key = True)

def __repr__(self):
  return '<Task %r>' % self.id

@app.route('/')
def index():
  return render_template('index.html')

if __name__ == "__main__":
  app.run(debug=True)
