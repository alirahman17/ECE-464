from ipdb import set_trace
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.sql import func, asc, desc, distinct
from sqlalchemy.orm import load_only

engine = create_engine(
      "mysql+pymysql://root:@localhost/sailors?host=localhost?port=3306", echo=True)

conn = engine.connect()

session = sessionmaker(bind=engine)
s = session()

Base = declarative_base()

class Sailor(Base):
    __tablename__ = 'sailors'

    sid = Column(Integer, primary_key=True)
    sname = Column(String)
    rating = Column(Integer)
    age = Column(Integer)

    def __repr__(self):
        return "<Sailor(id=%s, name='%s', rating=%s)>" % (self.sid, self.sname, self.age)


class Boat(Base):
    __tablename__ = 'boats'

    bid = Column(Integer, primary_key=True)
    bname = Column(String)
    color = Column(String)
    length = Column(Integer)

    reservations = relationship('Reservation', backref=backref('boat', cascade='delete'))

    def __repr__(self):
        return "<Boat(id=%s, name='%s', color=%s)>" % (self.bid, self.bname, self.color)


class Reservation(Base):
    __tablename__ = 'reserves'
    __table_args__ = (PrimaryKeyConstraint('sid', 'bid', 'day'), {})

    sid = Column(Integer, ForeignKey('sailors.sid'))
    bid = Column(Integer, ForeignKey('boats.bid'))
    day = Column(DateTime)

    sailor = relationship('Sailor')

    def __repr__(self):
        return "<Reservation(sid=%s, bid=%s, day=%s)>" % (self.sid, self.bid, self.day)


# Test Function
def sailors_assert(sql, orm):
    sql_check = []
    sql_ret = conn.execute(sql)
    for data in sql_ret:
        sql_check.append(data)

    orm_check = []
    for data in orm:
        orm_check.append(data)

    assert sql_check == orm_check

def test_question_1():
    sql = "SELECT s.sid, s.sname, s.rating, s.age, m.bid FROM sailors AS s, (SELECT bid, sid, MAX(total) FROM (SELECT bid, sid, count(*) AS total FROM reserves GROUP BY sid,bid ORDER BY bid ASC, total DESC) AS t GROUP BY bid) AS m WHERE s.sid = m.sid;"
    t = s.query(Reservation.bid, Reservation.sid, func.count("*").label('total')).group_by(Reservation.sid, Reservation.bid).order_by(asc(Reservation.bid), desc(func.count())).subquery('t')
    m = s.query(t.c.bid, t.c.sid, func.max(t.c.total)).group_by(t.c.bid).subquery('m')
    orm = s.query(Sailor.sid, Sailor.sname, Sailor.rating, Sailor.age, m.c.bid).join(m)
    sailors_assert(sql, orm)

def test_question_2():
    sql = "SELECT b.bid, b.bname, COUNT(*) FROM boats AS b, reserves AS r WHERE b.bid = r.bid GROUP BY b.bid;"
    orm = s.query(Boat.bid, Boat.bname, func.count("*")).join(Reservation).group_by(Boat.bid)
    sailors_assert(sql, orm)

def test_question_3():
    sql = "SELECT s.sid, s.sname FROM reserves AS r, sailors AS s WHERE r.sid = s.sid AND r.bid IN (SELECT b.bid FROM boats AS b WHERE b.color = 'red') GROUP BY r.sid HAVING COUNT(DISTINCT r.bid) = (SELECT COUNT(b.bid) FROM boats AS b WHERE b.color = 'red');"
    sub = s.query(Boat.bid).filter(Boat.color == 'red')
    number = sub.count()
    orm = s.query(Sailor.sid, Sailor.sname).join(Reservation).filter(Reservation.bid.in_(sub)).group_by(Reservation.sid).having(func.count(distinct(Reservation.bid)) == number)
    sailors_assert(sql, orm)

def test_question_4():
    sql = "SELECT s.sid, s.sname, s.rating, s.age FROM sailors AS s, reserves AS r, boats AS b WHERE s.sid = r.sid AND r.bid = b.bid AND b.color = 'red';"
    orm = s.query(Sailor.sid, Sailor.sname, Sailor.rating, Sailor.age).join(Reservation).join(Boat).filter(Boat.color == 'red')
    sailors_assert(sql, orm)

def test_question_5():
    sql = "SELECT b.bid, b.bname, b.color, b.length, count(*) FROM reserves AS r, boats AS b WHERE r.bid= b.bid GROUP BY r.bid ORDER BY count(*) DESC LIMIT 1;"
    orm = s.query(Boat.bid, Boat.bname, Boat.color, Boat.length, func.count("*")).join(Reservation).group_by(Reservation.bid).order_by(desc(func.count("*"))).limit(1)
    sailors_assert(sql, orm)

def test_question_6():
    sql = "SELECT s.sid, s.sname, s.rating, s.age FROM sailors AS s, reserves AS r, boats AS b WHERE s.sid = r.sid AND r.bid = b.bid AND b.color <> 'red';"
    orm = s.query(Sailor.sid, Sailor.sname, Sailor.rating, Sailor.age).join(Reservation).join(Boat).filter(Boat.color != 'red')
    sailors_assert(sql, orm)

def test_question_7():
    sql = "SELECT AVG(age) FROM sailors WHERE rating=10;"
    orm = s.query(func.avg(Sailor.age).label('AVG(age)')).filter(Sailor.rating == 10).all()
    sailors_assert(sql, orm)
