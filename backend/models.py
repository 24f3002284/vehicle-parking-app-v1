#Data models

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

#First entity
class User_Details(db.model):
    __tablename__="user_details" #by default,tablename will be taken as the class name with all letters in lower case
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=1) #by default, the one who registers is user and not admin
    full_name=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)

    #relations..write later

class Parking_lot(db.model):
    __tablename__="parking_lot"
    id=db.Column(db.Integer,primary_key=True)
    address=db.Column(db.String,nullable=False)
    price=(db.Integer,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    maximum_number_of_spots=db.Column(db.Integer,nullable=False)
    

class 
