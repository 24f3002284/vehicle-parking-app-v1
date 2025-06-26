#App routes
from flask import Flask,render_template,request,redirect,url_for
from .models import *
from flask import current_app as app

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def signin(): #the fn written after defining route is invoked through web browser
    if request.method=="POST": #this block gets executed only when we press submit
        uname=request.form.get("gmail") #gmail is the name 
        pwd=request.form.get("password") #pwd holds
        usr=User_Details.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: 
            # if usr exists and is admin
            return redirect(url_for("admindashboardfn",name=uname)) #to change the url from login to admin dashboard when admin logs in
                
        elif usr and usr.role==1:
            return redirect(url_for("userdashboardfn",name=uname)) #to change the url from login to admin dashboard when admin logs in
        
        else:
            return render_template("login.html",msg="Invalid User Credentials!")

    return render_template("login.html") #if method is GET,ie., the user came from home page to login page


@app.route("/register",methods=["GET","POST"])
def signup(): #we can write def register(): also ie.,fn name can be the same as the name of route
    if request.method=="POST":
        email=request.form.get("gmail")
        pwd=request.form.get("pword")
        fname=request.form.get("fulnam")
        address=request.form.get("address")
        pin=request.form.get("pincode")
        #checking if user already exists
        usr=User_Details.query.filter_by(email=email).first() #reading or pulling the data=>use query
        if usr:
            return render_template("register.html",msg="Sorry, this user already exists! Please use a different Email id. Thank you!")
        
        # creating a new object of class user details
        new_usr=User_Details(email=email,password=pwd,full_name=fname,address=address,pin_code=pin)

        db.session.add(new_usr) #adding new object to database 
        db.session.commit() #saving. we push data of user to db in lines 45 and 44(ie., adding and committing together=pushing to db) 

        return render_template("login.html",msg="Registration Successful! You may login.") #redirect user to login page after user registers

    return render_template("register.html")


#common route for admin dashboard 
@app.route("/admin/<name>")
def admindashboardfn(name):
    p_lots=get_lots() #admin should be able to see all the parking lots
    return render_template("admindashboard.html",name=name,lots=p_lots)


#common route for user dashboard 
@app.route("/user/<name>")
def userdashboardfn(name):
    return render_template("userdashboard.html",name=name)


@app.route("/lot/<name>",methods=["POST","GET"]) #use routes to connect frontend to backend and use render template to connect backend to frontend
#parameters are passed using < and > in routes. they are passed using {{ and }} while rendering
def add_lot(name):
    if request.method=="POST":
        lot_address=request.form.get("address")
        price=request.form.get("price")
        pin=request.form.get("pincode")
        num_of_spots=request.form.get("max_no_of_spots")
        
        new_lot=Parking_lot(address=lot_address,price=price,pin_code=pin,maximum_number_of_spots=num_of_spots)

        db.session.add(new_lot)
        db.session.commit()

        return redirect(url_for("admindashboardfn",name=name))

    return render_template("add_lot.html",name=name)


@app.route("/spot/<lot_id>/<name>",methods=["POST","GET"])
def add_spot(lot_id,name):
    if request.method=="POST":
        status=request.form.get("status")
        
        new_spot=Parking_Spot(lot_id=lot_id,status=status)

        db.session.add(new_spot)
        db.session.commit()

        return redirect(url_for("admindashboardfn",name=name))

    return render_template("add_spot.html",lot_id=lot_id,name=name)


@app.route("/search/<name>",methods=["GET","POST"])
def search(name):
    if request.method=="POST":
        search_text=request.form.get("search")
        by_location=search_by_loc(search_text)
        if by_location:
            return render_template("admindashboard.html",name=name,lots=by_location)

    return redirect(url_for("admindashboardfn",name=name))


@app.route("/edit_lot/<id>/<name>",methods=["GET","POST"])
def edit_lot(id,name):
    l=get_lot(id)
    if request.method=="POST":
        address=request.form.get("address")
        price=request.form.get("price")
        pin=request.form.get("pincode")
        max_num_of_spots=request.form.get("max_no_of_spots")

        l.address=address
        l.price=price
        l.pincode=pin
        l.max_no_of_spots=max_num_of_spots

        db.session.commit() #updating
        return redirect(url_for("admindashboardfn",name=name))
    
    return render_template("edit_lot.html",id=l,name=name)

#supporter fn
def get_lots():
    pLots=Parking_lot.query.all() #pLots returns all the parking lots present in the Parking lot
    return pLots

def search_by_loc(search_text):
    ans=Parking_lot.query.filter(Parking_lot.address.ilike(f"%{search_text}%")).all()
    return ans

def get_lot(id):
    lot=Parking_lot.query.filter_by(id=id).first()
    return lot