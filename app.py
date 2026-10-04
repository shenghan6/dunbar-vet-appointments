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
    address = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)  # DV-02: False = 停用（软删除）

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
    kind = db.Column(db.String(20), default="clinic")  # clinic=诊所预约 / farm=农场出诊
    status = db.Column(db.String(20), default="confirmed")  # confirmed=已确认 / cancelled=已取消
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/clients')
def clients():
    q = request.args.get('q', '')
    if q:
        all_clients = Client.query.filter(
            db.or_(Client.name.contains(q), Client.phone.contains(q))
        ).all()
    else:
        all_clients = Client.query.all()
    return render_template('clients.html', clients=all_clients, q=q)

@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        c = Client(
            name=request.form['name'],
            phone=request.form.get('phone', ''),
            address=request.form.get('address', '')
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('clients'))
    return render_template('add_client.html')

@app.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
def edit_client(client_id):
    c = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        c.name = request.form['name']
        c.phone = request.form.get('phone', '')
        c.address = request.form.get('address', '')
        db.session.commit()
        return redirect(url_for('clients'))
    return render_template('edit_client.html', client=c)

@app.route('/clients/<int:client_id>/deactivate', methods=['POST'])
def deactivate_client(client_id):
    c = Client.query.get_or_404(client_id)
    c.is_active = False  # 软删除：不物理删除，只标记停用
    db.session.commit()
    return redirect(url_for('clients'))

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
        client_id = request.form.get('client_id') or None
        # DV-02: 停用客户不能新建动物（预约）
        if client_id:
            owner = Client.query.get(client_id)
            if owner is None or not owner.is_active:
                return "Cannot add animal to a deactivated client", 400
        animal = Animal(
            name=request.form['name'],
            species=request.form['species'],
            breed=request.form['breed'],
            client_id=client_id
        )
        db.session.add(animal)
        db.session.commit()
        return redirect(url_for('animals'))
    clients = Client.query.filter_by(is_active=True).all()
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


# ---------- DV-08: cancel & reschedule appointment ----------

def _has_time_conflict(kind, date, time, exclude_id=None):
    """检查同一种类(clinic/farm)在同一天同一时间是否已有已确认预约。"""
    q = Appointment.query.filter_by(kind=kind, date=date, time=time, status="confirmed")
    if exclude_id is not None:
        q = q.filter(Appointment.id != exclude_id)
    return q.first() is not None


@app.route('/appointments/<int:apt_id>/cancel', methods=['POST'])
def cancel_appointment(apt_id):
    apt = Appointment.query.get_or_404(apt_id)
    if apt.status == "cancelled":
        return {"error": "Appointment is already cancelled"}, 400
    apt.status = "cancelled"
    db.session.commit()
    return {"message": "Appointment cancelled", "id": apt.id, "status": apt.status}


@app.route('/appointments/<int:apt_id>/reschedule', methods=['POST'])
def reschedule_appointment(apt_id):
    apt = Appointment.query.get_or_404(apt_id)
    if apt.status == "cancelled":
        return {"error": "Cannot reschedule a cancelled appointment"}, 400

    if request.is_json:
        data = request.get_json()
        new_date = data.get('date')
        new_time = data.get('time')
    else:
        new_date = request.form.get('date')
        new_time = request.form.get('time')
    if not new_date or not new_time:
        return {"error": "date and time are required"}, 400

    if _has_time_conflict(apt.kind, new_date, new_time, exclude_id=apt.id):
        return {"error": "Time conflict: another confirmed appointment already exists"}, 409

    apt.date = new_date
    apt.time = new_time
    db.session.commit()
    return {"message": "Appointment rescheduled", "id": apt.id, "date": apt.date, "time": apt.time}


@app.route('/appointment', methods=["GET","POST"])
def appointment():
    return render_template("appointment.html")

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/dv11')
def dv11_page():
    return "<h1>DV11: Pet Record Query Page</h1><p>This is ZiangDong's independent work for A2. This page allows staff to search pet basic information.</p>"

@app.route('/dv09')
def dv09_page():
    return "<h1>DV09: Vet Appointment Page</h1><p>This is ZiangDong's independent work for A2</p>"
