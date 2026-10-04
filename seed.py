"""
DV-12: 种子数据脚本
运行方式: python seed.py
作用: 向 SQLite 插入模拟客户、动物、物业、预约样例数据，方便演示和测试。
"""
from app import app, db, Client, Animal, Property, Appointment


def seed():
    with app.app_context():
        # 先清空旧数据，避免重复插入
        db.drop_all()
        db.create_all()

        # ---- 客户 ----
        c1 = Client(name="Trina Dunbar", phone="027-555-0101")
        c2 = Client(name="James Wilson", phone="027-555-0102")
        c3 = Client(name="Sarah Chen", phone="027-555-0103")
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # ---- 动物 ----
        a1 = Animal(name="Rex", species="Dog", breed="Labrador", client_id=c1.id)
        a2 = Animal(name="Mittens", species="Cat", breed="Tabby", client_id=c1.id)
        a3 = Animal(name="Bessie", species="Cow", breed="Holstein", client_id=c2.id)
        a4 = Animal(name="Daisy", species="Goat", breed="Saanen", client_id=c3.id)
        db.session.add_all([a1, a2, a3, a4])
        db.session.commit()

        # ---- 物业（农场出诊地点）----
        p1 = Property(name="Dunbar Farm", address="123 Rural Rd, Dunbar",
                      contact_phone="027-555-1001", area="North Pasture")
        p2 = Property(name="Wilson Dairy", address="456 Meadow Ln, Dunbar",
                      contact_phone="027-555-1002", area="South Field")
        p3 = Property(name="Chen Smallholding", address="789 Hill Top, Dunbar",
                      contact_phone="027-555-1003", area="Main Barn")
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        # ---- 预约 ----
        # clinic = 诊所预约, farm = 农场出诊
        apt1 = Appointment(date="2026-09-22", time="09:00", kind="clinic", animal_id=a1.id)
        apt2 = Appointment(date="2026-09-22", time="10:30", kind="clinic", animal_id=a2.id)
        apt3 = Appointment(date="2026-09-23", time="14:00", kind="farm", animal_id=a3.id)
        apt4 = Appointment(date="2026-09-24", time="11:00", kind="farm", animal_id=a4.id)
        db.session.add_all([apt1, apt2, apt3, apt4])
        db.session.commit()

        print("=" * 50)
        print("Seed data inserted successfully!")
        print(f"  Clients:    {Client.query.count()}")
        print(f"  Animals:    {Animal.query.count()}")
        print(f"  Properties: {Property.query.count()}")
        print(f"  Appointments: {Appointment.query.count()}")
        print("=" * 50)


if __name__ == "__main__":
    seed()
