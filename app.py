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

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(200))
    contact_phone = db.Column(db.String(20))
    area = db.Column(db.String(40))

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
    q = request.args.get('q', '')
    if q:
        all_animals = Animal.query.filter(
            db.or_(Animal.name.contains(q), Animal.species.contains(q))
        ).all()
    else:
        all_animals = Animal.query.all()
    return render_template('animals.html', animals=all_animals, q=q)

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

@app.route('/properties')
def properties():
    return render_template('properties.html', properties=Property.query.all())

@app.route('/properties/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        p = Property(
            name=request.form['name'],
            address=request.form['address'],
            contact_phone=request.form['contact_phone'],
            area=request.form['area']
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('properties'))
    return render_template('add_property.html')

@app.route('/route')
def route_view():
    properties = Property.query.order_by(Property.name).all()
    return render_template('route.html', properties=properties)

with app.app_context():
    db.create_all()

@app.route('/appointment', methods=["GET","POST"])
def appointment():
    return render_template("appointment.html")

if __name__ == '__main__':
    app.run(debug=True)

