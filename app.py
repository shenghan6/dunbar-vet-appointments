from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    species = db.Column(db.String(40))
    breed = db.Column(db.String(40))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client', backref=db.backref('animals', lazy=True))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    kind = db.Column(db.String(20))
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/animals')
def animals():
    all_animals = Animal.query.all()
    return render_template('animals.html', animals=all_animals)

@app.route('/animals/add', methods=['GET', 'POST'])
def add_animal():
    if request.method == 'POST':
        animal = Animal(
            name=request.form['name'],
            species=request.form['species'],
            breed=request.form['breed'],
            client_id=request.form.get('client_id') or None
        )
        db.session.add(animal)
        db.session.commit()
        return redirect(url_for('animals'))
    clients = Client.query.all()
    return render_template('add_animal.html', clients=clients)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)