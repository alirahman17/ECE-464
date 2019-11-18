# Assignment 1, Part 3
from ipdb import set_trace
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, DateTime, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import backref, relationship
from sqlalchemy import PrimaryKeyConstraint, extract
from sqlalchemy.sql import func, asc, desc, distinct
from sqlalchemy.orm import load_only
import pytest

# Instantiate Connection
engine = create_engine(
      "mysql+pymysql://root:@localhost/sailors?host=localhost?port=3306", echo=True)

conn = engine.connect()

session = sessionmaker(bind=engine)
s = session()
metadata = MetaData(engine)

Base = declarative_base()

# Table Creation
sailors = Table('sailors', metadata, Column('sid', Integer, primary_key = True), Column('sname', String(30)), Column('rating', Integer), Column('age', Integer))
boats = Table('boats', metadata, Column('bid', Integer, primary_key = True), Column('bname', String(20)), Column('color', String(10)), Column('length', Integer), Column('cost', Integer))
reserves = Table('reserves', metadata, Column('sid', Integer, ForeignKey("sailors.sid"), primary_key = True), Column('bid', Integer, ForeignKey("boats.bid"), primary_key = True), Column('day', Date, primary_key = True))
employees = Table('employees', metadata, Column('eid', Integer, primary_key = True), Column('ename', String(30)), Column('hrwage', Integer))
hours = Table('hours', metadata, Column('eid', Integer, ForeignKey("employees.eid"), primary_key = True), Column('week', Date, primary_key = True), Column('hours_worked', Integer))

# Drop any previous data and create new data
metadata.drop_all()
metadata.create_all()

# File Used to Populate Database
sql_file = open("./sailors_mgmt.sql", "r")
for line in sql_file:
        line = line.strip("\r\n")
        conn.execute(line)

# This Class Remains Unchanged from Part 2
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
    cost = Column(Integer)                      # New Column for Monthly Cost Calc

    reservations = relationship('Reservation', backref=backref('boat', cascade='delete'))

    def __repr__(self):
        return "<Boat(id=%s, name='%s', color=%s, cost=%s)>" % (self.bid, self.bname, self.color, self.cost)


# This Class Remains Unchanged from Part 2
class Reservation(Base):
    __tablename__ = 'reserves'
    __table_args__ = (PrimaryKeyConstraint('sid', 'bid', 'day'), {})

    sid = Column(Integer, ForeignKey('sailors.sid'))
    bid = Column(Integer, ForeignKey('boats.bid'))
    day = Column(Date)

    sailor = relationship('Sailor')

    def __repr__(self):
        return "<Reservation(sid=%s, bid=%s, day=%s)>" % (self.sid, self.bid, self.day)


class Employee(Base):
    __tablename__ = 'employees'

    eid = Column(Integer, primary_key=True)
    ename = Column(String)
    hrwage = Column(Integer)

    def __repr__(self):
        return "<Employee(id=%s, name=%s, wage=%s)>" % (self.eid, self.ename, self.hrwage)

class Hour(Base):
    __tablename__ = 'hours'
    __table_args__ = (PrimaryKeyConstraint('eid', 'week'), {})

    # Uses Employee.eid as foreignkey to verify existence of employee
    eid = Column(Integer, ForeignKey('employees.eid'))
    week = Column(Date)                 # Uses eid, week pair as unique value
    hours_worked = Column(Integer)      # Hours an employee works in a given week

    employee = relationship('Employee') # Relationship with Employee Table for fkey

    def __repr__(self):
        return "<Hour(eid=%s, week=%s, hours_worked=%s)>" % (self.eid, self.week, self.hours_worked)

# Function to Calculate the Pay for a Given Employee in a Specific Month
def monthly_employee_pay(eid, month):
    query = s.query(Employee.eid, Employee.ename, Employee.hrwage, Hour.hours_worked).join(Hour).filter(Employee.eid == eid).filter(extract('month', Hour.week) == month)
    monthly_pay = 0
    for data in query:
        monthly_pay += data[2] * data[3]
    return monthly_pay

# Function to Calculate the Profit for a Given Boat in a Specific Month
def monthly_boat_profit(bid, month):
    query = s.query(Boat.bid, Boat.bname, Reservation.day, Boat.cost).join(Reservation).filter(Boat.bid == bid).filter(extract('month', Reservation.day) == month)
    monthly_profit = 0
    for data in query:
        monthly_profit += data[3]
    return monthly_profit

# Function to Calculate Total Profit in Given Month Using All bid and eid
def total_monthly_profit(month):
    eids = s.query(Employee.eid)
    total_profit = 0
    for data in eids:
        total_profit -= monthly_employee_pay(data[0], month)

    bids = s.query(Boat.bid)
    for data in bids:
        total_profit += monthly_boat_profit(data[0], month)
    return total_profit

# pytest Functions
def test_employee_pay():
    # Test Employee 4's Pay in September (9)
    assert monthly_employee_pay(4, 9) == 140

def test_boat_profit():
    # Test Boat 104's Profit in October (10)
    assert monthly_boat_profit(104, 10) == 66

def test_monthly_profit():
    # Test Net Profit of October (10)
    assert total_monthly_profit(10) == 10
