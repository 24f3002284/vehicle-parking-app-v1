#Data models

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

#First entity
class User_Details(db.Model):
    __tablename__="user_details" #by default,tablename will be taken as the class name with all letters in lower case
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=1) # by default, the one who registers is user and not admin
    full_name=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)

    # relations..we should be able to access all the reserve parking spots of a user
    reserve_parking_spot=db.relationship("Reserve_parking_spot",cascade="all,delete",backref="user_details",lazy=True)


#entity 2
class Parking_lot(db.Model):
    __tablename__="parking_lot"
    id=db.Column(db.Integer,primary_key=True)
    address=db.Column(db.String,nullable=False)
    price=db.Column(db.Float,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    maximum_number_of_spots=db.Column(db.Integer,nullable=False,default=0)
    
    #relnship.. parking lot should be able to access all parking spots
    parking_spot=db.relationship("Parking_Spot",cascade="all,delete",backref="parking_lot",lazy=True)

#entity 3
class Parking_Spot(db.Model): #db.Model is a predefined class which is inherited from SQLAlchemy. our class(here, Parking_Spot behaves like a data table) =>inheritance
    __tablename__="parking_spot"
    id=db.Column(db.Integer,primary_key=True) 
    lot_id=db.Column(db.Integer,db.ForeignKey("parking_lot.id"),nullable=False)
    status=db.Column(db.String,default="A")
    #Relnships..later

    reserve_parking_spot=db.relationship("Reserve_parking_spot",cascade="all,delete",backref="parking_spot",lazy=True)

#entity4
class Reserve_parking_spot(db.Model):
    __tablename__="reserve_parking_spot"
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.String,db.ForeignKey("user_details.email"),nullable=False) #user_id=email
    lot_id=db.Column(db.Integer,db.ForeignKey("parking_lot.id"),nullable=False)
    spot_id=db.Column(db.Integer,db.ForeignKey("parking_spot.id"),nullable=False)
    vehicle_no=db.Column(db.String,nullable=False)
    p_time=db.Column(db.DateTime,nullable=True)
    l_time=db.Column(db.DateTime,nullable=True)

    #no need of relnships bcz this table is not acting as a master table(has no child table)

#access parent from child using foreign key. access child from parent, use relationship

#venv\Scripts\activate =>to activate venv
#python app.py