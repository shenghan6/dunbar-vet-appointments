import pytest
from app import app, db, Appointment, Animal


@pytest.fixture
def client():
    # 用内存数据库，测试完不影响真实 vet.db
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def _make_animal():
    a = Animal(name="Rex", species="Dog")
    db.session.add(a)
    db.session.commit()
    return a


def test_cancel_appointment(client):
    """正常取消：status 变成 cancelled"""
    animal = _make_animal()
    apt = Appointment(date="2026-10-10", time="10:00", kind="clinic", animal_id=animal.id)
    db.session.add(apt)
    db.session.commit()

    resp = client.post(f'/appointments/{apt.id}/cancel')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'cancelled'


def test_cancel_already_cancelled_fails(client):
    """重复取消：已经 cancelled 的预约不能再取消"""
    animal = _make_animal()
    apt = Appointment(date="2026-10-10", time="10:00", kind="clinic",
                      status="cancelled", animal_id=animal.id)
    db.session.add(apt)
    db.session.commit()

    resp = client.post(f'/appointments/{apt.id}/cancel')
    assert resp.status_code == 400


def test_reschedule_success(client):
    """正常改期：新时间不冲突，改成功"""
    animal = _make_animal()
    apt = Appointment(date="2026-10-10", time="10:00", kind="clinic", animal_id=animal.id)
    db.session.add(apt)
    db.session.commit()

    resp = client.post(f'/appointments/{apt.id}/reschedule',
                       json={"date": "2026-10-11", "time": "14:00"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['date'] == "2026-10-11"
    assert data['time'] == "14:00"


def test_reschedule_conflict_fails(client):
    """改期到冲突时间：同种类同一天同一时间已有 confirmed 预约 -> 409"""
    animal = _make_animal()
    # 已占住 10-11 14:00 的预约
    db.session.add(Appointment(date="2026-10-11", time="14:00",
                              kind="clinic", animal_id=animal.id))
    # 要改期的预约
    apt = Appointment(date="2026-10-10", time="10:00", kind="clinic", animal_id=animal.id)
    db.session.add(apt)
    db.session.commit()

    resp = client.post(f'/appointments/{apt.id}/reschedule',
                       json={"date": "2026-10-11", "time": "14:00"})
    assert resp.status_code == 409
