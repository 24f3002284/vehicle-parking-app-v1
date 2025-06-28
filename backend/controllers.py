#App routes
from flask import Flask,render_template,request,redirect,url_for
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func

def ensure_admin_exists():
    admin_count=User_Details.query.filter_by(role=0).count()

    if(admin_count==0): #automatic creation of admin
        default_admin=User_Details(email="admin@parking.com",
                                   password="admin12345",
                                   role=0,
                                   full_name="Default Administrator",
                                   address="West Fort,Kerala,India",
                                   pin_code=680004)
    
        db.session.add(default_admin)
        db.session.commit()

@app.route("/")
def home():
    ensure_admin_exists()
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def signin(): #the fn written after defining route is invoked through web browser
    if request.method=="POST": #this block gets executed only when we press submit
        uname=request.form.get("gmail") #gmail is the name 
        pwd=request.form.get("password") #pwd holds
        usr=User_Details.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: 
            # if usr exists and is admin
            return redirect(url_for("admindashboardfn",name=uname,msg="")) #to change the url from login to admin dashboard when admin logs in
                
        elif usr and usr.role==1:
            return redirect(url_for("userdashboardfn",name=uname,msg="")) #to change the url from login to admin dashboard when admin logs in
        
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


# @app.route("/users/<name>",methods=["GET","POST"])
# def registered_users(name):
#     return render_template("registered_users.html",name=name)


#common route for admin dashboard 
@app.route("/admin/<name>")
def admindashboardfn(name,msg=""):
    p_lots=get_lots() #admin should be able to see all the parking lots
    lot_stats=[]

    for lot in p_lots:
        avail=0
        occ=0
        total=lot.maximum_number_of_spots

        for spot in lot.parking_spot:
            if spot.status=="A":
                avail+=1
            else:
                occ+=1

        lot_stats.append({
            'lot':lot,
            'avail':avail,
            'occ':occ,
            'total':total
        })
    
    return render_template("admindashboard.html",name=name,lot_stats=lot_stats,msg=msg)


#common route for user dashboard 
@app.route("/user/<name>")
def userdashboardfn(name):
    p_lots=get_lots()
    usr=User_Details.query.filter_by(email=name).first()

    return render_template("userdashboard.html",name=name,lots=p_lots,f_name=usr.full_name)


@app.route("/lot/<name>",methods=["POST","GET"]) #use routes to connect frontend to backend and use render template to connect backend to frontend
#parameters are passed using < and > in routes. they are passed using {{ and }} while rendering
def add_lot(name):
    if request.method=="POST":
        lot_address=request.form.get("address")
        price=request.form.get("price")
        pin=request.form.get("pincode")
        num_of_spots=int(request.form.get("max_no_of_spots"))
        
        new_lot=Parking_lot(address=lot_address,price=price,pin_code=pin,maximum_number_of_spots=num_of_spots)

        db.session.add(new_lot)
        db.session.commit()

        # Automatically create parking spots based on maximum_number_of_spots
        if(num_of_spots and num_of_spots>0):
            for i in range(int(num_of_spots)):
                new_spot=Parking_Spot(lot_id=new_lot.id,status="A")
                db.session.add(new_spot)

            db.session.commit()

        return redirect(url_for("admindashboardfn",name=name,msg=""))

    return render_template("add_lot.html",name=name)


@app.route("/search/<name>",methods=["GET","POST"])
def search(name):
    if request.method=="POST":
        search_text=request.form.get("search")
        by_location=search_by_loc(search_text)

        lot_stats=[]

        for lot in by_location:
            avail=0
            occ=0
            total=lot.maximum_number_of_spots

            for spot in lot.parking_spot:
                if spot.status=="A":
                    avail+=1

                else:
                    occ+=1

            lot_stats.append({
                'lot':lot,
                'avail':avail,
                'occ':occ,
                'total':total
            })

        return render_template("admindashboard.html",name=name,lot_stats=lot_stats)
   
    return redirect(url_for("admindashboardfn",name=name,msg=""))


@app.route("/edit_lot/<id>/<name>",methods=["GET","POST"])
def edit_lot(id,name):
    l=get_lot(id)

    if not l:
        return redirect(url_for("admindashboardfn",name=name,msg=""))

    avail=0
    occ=0

    for spot in l.parking_spot:
        if spot.status=="A":
            avail+=1
        else:
            occ+=1

    if request.method=="POST":
        lotid=request.form.get("lotid")
        address=request.form.get("address")
        price=request.form.get("price")
        pin=request.form.get("pincode")
        max_num_of_spots=request.form.get("max_no_of_spots")

        current_no_of_spots=len(l.parking_spot)

        l.id=lotid
        l.address=address
        l.price=price
        l.pin_code=pin
        l.maximum_number_of_spots=max_num_of_spots

        new_max_spots=int(l.maximum_number_of_spots)

        if(new_max_spots>current_no_of_spots):
            spots_to_add=new_max_spots-current_no_of_spots
            for i in range(spots_to_add):
                new_spot=Parking_Spot(lot_id=l.id,status="A")
                db.session.add(new_spot)
                db.session.commit()

        elif(new_max_spots<current_no_of_spots):
            spots_to_remove=current_no_of_spots-new_max_spots
            
            if(avail<spots_to_remove):
                error=f"Cannot reduce spots. Need to remove {spots_to_remove} spots only {avail} are available."
                return render_template("edit_lot.html",lots=l,lid=l.id,name=name,available=avail,occupied=occ,error=error)
            
            available_spots=Parking_Spot.query.filter_by(lot_id=l.id,status="A").limit(spots_to_remove).all()
            for spot in available_spots:
                db.session.delete(spot)
                db.session.commit()

        return redirect(url_for("admindashboardfn",name=name,msg=""))
    
    return render_template("edit_lot.html",lots=l,lid=l.id,name=name,available=avail,occupied=occ)


@app.route("/delete_lot/<id>/<name>",methods=["GET","POST"])
def delete_lot(id,name):
    l=get_lot(id)

    occupied_spots = Parking_Spot.query.filter_by(lot_id=id).filter(
        Parking_Spot.status != "A"
    ).all()

    if occupied_spots:
        return redirect(url_for("admindashboardfn",name=name,msg="Sorry!"))

    db.session.delete(l)
    db.session.commit()
    return redirect(url_for("admindashboardfn",name=name,msg=""))


@app.route("/edit_spot/<lid>/<sid>/<name>",methods=["GET","POST"])
def edit_spot(lid,sid,name):
    s=get_spot(sid)
    l=get_lot(lid).id

    if request.method=="POST":
        status=request.form.get("status")
    
        s.status=status

        db.session.commit() #updating
        return redirect(url_for("admindashboardfn",name=name,msg=""))
    
    return render_template("edit_spot.html",spot=s,name=name,lid=l)


# @app.route("/delete_spot/<id>/<name>",methods=["GET","POST"])
# def delete_spot(id,name):
#     s=get_spot(id)

#     if s.status=="Occupied":
#         msg="Can't Delete an already occupied Parking spot!"
#         return redirect(url_for("admindashboardfn",name=name))
    
#     db.session.delete(s)
#     db.session.commit()
#     return redirect(url_for("admindashboardfn",name=name))


@app.route("/book_lot/<name>/<sid>/<pid>",methods=["GET","POST"])
def book_lot(name,sid,pid):
    
    available_spots=get_a(pid)
    occupied_spots=get_lot(pid).maximum_number_of_spots-available_spots

    if request.method=="POST":
        veh_no=request.form.get("vehicle_no")
        p_time_str=request.form.get("p_time")
        # l_time_str=request.form.get("l_time")

        #converting string to datetime objects
        p_time=datetime.strptime(p_time_str,'%Y-%m-%dT%H:%M')
        
        dt_time_now=datetime.today().strftime('%Y-%m-%dT%H:%M')

        #converting string to datetime objects
        dt_time_now=datetime.strptime(dt_time_now,'%Y-%m-%dT%H:%M')
        # l_time=datetime.strptime(l_time_str,'%Y-%m-%dT%H:%M')
        
        # hours_diff=(l_time-p_time).total_seconds()/3600
        # cost=(hours_diff)*(get_lot(pid).price)

        if p_time>dt_time_now:
            new_booking=Reserve_parking_spot(spot_id=sid,lot_id=pid,vehicle_no=veh_no,p_time=p_time,user_id=name)
            # spot=get_spot(sid)
            # spot.status="Occupied"

            db.session.add(new_booking)
            db.session.commit()
            
            #booked lots=> by aggregate function sum
            #1 user can book only 1 parking spot at a time,since 1 vehicle no=>1spot
            
            available_spots-=1
        return redirect(url_for("userdashboardfn",name=name))
    
    spot=Parking_Spot.query.filter_by(id=sid).first()
    lot=Parking_lot.query.filter_by(id=pid).first()

    return render_template("book_lot.html",
                           name=name,
                           spot_id=sid,
                           lot_id=pid,
                           available_spots=available_spots,
                           spot=spot,
                           lot=lot
                        )


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

def get_spot(id):
    spot=Parking_Spot.query.filter_by(id=id).first()
    return spot

def get_a(pid):
    lot=get_lot(pid)
    avail=0
    for spot in lot.parking_spot:
        if(spot.status=="A"):
            avail+=1

    return avail