import pytest
from app import app, db, Client, Animal


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_edit_client(client):
    """修改客户信息：提交表单后数据库里名字/电话更新"""
    c = Client(name='Old Name', phone='111', address='Old St')
    db.session.add(c)
    db.session.commit()

    resp = client.post(f'/clients/{c.id}/edit', data={
        'name': 'New Name',
        'phone': '222',
        'address': 'New Ave'
    }, follow_redirects=True)
    assert resp.status_code == 200
    updated = Client.query.get(c.id)
    assert updated.name == 'New Name'
    assert updated.phone == '222'


def test_deactivate_client(client):
    """停用客户：is_active 变成 False，但记录还在（软删除）"""
    c = Client(name='To Deactivate', phone='333', address='')
    db.session.add(c)
    db.session.commit()

    resp = client.post(f'/clients/{c.id}/deactivate', follow_redirects=True)
    assert resp.status_code == 200
    after = Client.query.get(c.id)
    assert after.is_active is False
    # 记录没被物理删除
    assert Client.query.filter_by(name='To Deactivate').first() is not None


def test_deactivated_client_cannot_add_animal(client):
    """停用客户不能新建动物（预约）"""
    c = Client(name='Dead Client', phone='444', address='', is_active=False)
    db.session.add(c)
    db.session.commit()

    resp = client.post('/animals/add', data={
        'name': 'Ghost',
        'species': 'Dog',
        'breed': '',
        'client_id': c.id
    })
    assert resp.status_code == 400
    assert Animal.query.filter_by(name='Ghost').first() is None


def test_active_client_can_add_animal(client):
    """正常客户可以新建动物（对照用例）"""
    c = Client(name='Alive Client', phone='555', address='', is_active=True)
    db.session.add(c)
    db.session.commit()

    resp = client.post('/animals/add', data={
        'name': 'Happy',
        'species': 'Cat',
        'breed': '',
        'client_id': c.id
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert Animal.query.filter_by(name='Happy').first() is not None
