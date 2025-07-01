#App routes
from flask import Flask,render_template,request,redirect,url_for
from .models import *
from flask import current_app as app
from datetime import datetime
# from sqlalchemy import func
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

    usr=User_Details.query.filter_by(email=name).first()

    return render_template("userdashboard.html",name=name,lots=p_lots,f_name=usr.full_name,lot_stats=lot_stats)


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


@app.route("/search_lots/<name>",methods=["GET","POST"])
def search_user(name):
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

        return render_template("userdashboard.html",name=name,lot_stats=lot_stats)
   
    return redirect(url_for("userdashboardfn",name=name))


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
    l=get_lot(lid)

    if not s or not l:
        return redirect(url_for("admindashboardfn",name=name,msg="Spot not found"))

    current_reservation=None
    if s.status=="O":
        current_reservation=Reserve_parking_spot.query.filter_by(spot_id=sid,l_time=None).first()

    if request.method=="POST":
        new_status=request.form.get("status")
    
        if s.status=="O" and new_status=="A" and current_reservation:
            error="Cannot change spot to available. Please end the current reservation first."

            return render_template("edit_spot.html",spot=s,name=name,lid=l.id,current_reservation=current_reservation,error=error)
        
        if s.status=="A" and new_status=="O":
            error="Cannot manually set spot to occupied. Spots are automatically occupied when booked."

            return render_template("edit_spot.html",spot=s,name=name,lid=l.id,error=error)
        
        s.status=new_status

        db.session.commit() #updating
        return redirect(url_for("admindashboardfn",name=name,msg="Spot updated successfully"))
    
    return render_template("edit_spot.html",spot=s,name=name,lid=l.id,current_reservation=current_reservation)


@app.route("/delete_spot/<lid>/<sid>/<name>",methods=["GET","POST"])
def delete_spot(lid,sid,name):
    s=get_spot(sid)
    l=get_lot(lid)

    if not l or not s:
        return redirect(url_for("admindashboardfn",name=name,msg="Spot or lot not found"))

    if s.status=="O":
        reservation=Reserve_parking_spot.query.filter_by(spot_id=sid,l_time=None).first()
        if reservation:
            error=f"Cannot delete occupied spot. Vehicle {reservation.vehicle_no} is currently parked here from {reservation.p_time}."

            return redirect(url_for("admindashboardfn",name=name,msg=error))

    past_reservations=Reserve_parking_spot.query.filter_by(spot_id=sid).all()

    if past_reservations:
        error="Cannot delelte spot with booking history!"
        return redirect(url_for("admindashboardfn",name=name,msg=error))
    
    db.session.delete(s)
    l.maximum_number_of_spots-=1
    db.session.commit()

    return redirect(url_for("admindashboardfn",name=name,msg="Spot deleted successfully!"))


@app.route("/view_spot_details/<lid>/<sid>/<name>")
def view_spot_details(lid, sid, name):
    """View detailed information about a parking spot including vehicle details if occupied"""
    spot = get_spot(sid)
    lot = get_lot(lid)
    
    if not spot or not lot:
        return redirect(url_for("admindashboardfn", name=name, msg="Spot or lot not found"))
    
    vehicle_details = None
    booking_details = None
    
    # If spot is occupied, get the vehicle and booking details
    if spot.status == "O":
        # Get the current reservation for this spot
        current_reservation = Reserve_parking_spot.query.filter_by(
            spot_id=sid, 
            l_time=None  # l_time is None means it's still active
        ).first()
        
        if current_reservation:
            # Get user details
            user = User_Details.query.filter_by(email=current_reservation.user_id).first()
            
            # Calculate current duration and cost
            current_time = datetime.now()
            duration_seconds = (current_time - current_reservation.p_time).total_seconds()
            hours = round(duration_seconds / 3600, 1)
            current_cost = round(hours * lot.price, 2)
            
            vehicle_details = {
                'vehicle_no': current_reservation.vehicle_no,
                'user_name': user.full_name if user else 'Unknown',
                'user_email': current_reservation.user_id,
                'user_address': user.address if user else 'Unknown',
                'parking_start': current_reservation.p_time,
                'duration_hours': hours,
                'current_cost': current_cost,
                'booking_id': current_reservation.id
            }
    
    return render_template("spot_details.html", 
                         spot=spot, 
                         lot=lot, 
                         vehicle_details=vehicle_details,
                         name=name)


@app.route("/select_spot/<lot_id>/<name>",methods=["GET","POST"])
def select_spot(lot_id,name):

    lot=get_lot(lot_id)
    if not lot:
        return redirect(url_for("userdashboardfn",name=name))
    
    available_spots=Parking_Spot.query.filter_by(lot_id=lot_id,status="A").all()

    if not available_spots:
        return redirect(url_for("userdashboardfn",name=name))
    
    selected_spot=available_spots[0]
    return redirect(url_for("book_lot",name=name,pid=lot_id,sid=selected_spot.id))

@app.route("/book_lot/<name>/<pid>/<sid>",methods=["GET","POST"])
def book_lot(name,pid,sid):
    available_spots=get_a(pid)
    lot=get_lot(pid)
    spot=get_spot(sid)

    if not lot or not spot:
        return redirect(url_for("userdashboardfn",name)) 

    #check if spot is still available
    if spot.status!="A":
        return redirect(url_for("userdashboardfn",name=name))
    
    if request.method=="POST":
        veh_no=request.form.get("vehicle_no")
        p_time_str=request.form.get("p_time") 
        
        #converting string to datetime objects
        p_time=datetime.strptime(p_time_str,'%Y-%m-%dT%H:%M')
        current_time=datetime.now()  

        if p_time>=current_time:
            #checking if user already has active booking
            existing_booking=Reserve_parking_spot.query.filter(Reserve_parking_spot.user_id==name,Reserve_parking_spot.l_time==None).first()
        
            if not existing_booking:
                new_booking=Reserve_parking_spot(spot_id=sid,lot_id=pid,vehicle_no=veh_no,p_time=p_time,user_id=name)
            
                spot.status="O"

                db.session.add(new_booking)
                db.session.commit()
                
                return redirect(url_for("userdashboardfn",name=name))

        else:
            return render_template("book_lot.html",name=name,
                                   spot_id=sid,lot_id=pid,
                                   available_spots=available_spots,
                                   spot=spot,lot=lot,
                                   error="Parking time cannot be in the past")

    return render_template("book_lot.html",
                           name=name,
                           spot_id=sid,
                           lot_id=pid,
                           available_spots=available_spots,
                           spot=spot,
                           lot=lot,
                        )


@app.route("/my_bookings/<name>")
def my_bookings(name):
    #present bookings of each user
    user_bookings=Reserve_parking_spot.query.filter_by(user_id=name).all()

    active_bookings=[]

    for booking in user_bookings:
        booking_data={
            'booking':booking,
            'lot':get_lot(booking.lot_id),
            'spot':get_spot(booking.spot_id)
        }

        if booking.l_time is None:
            current_time=datetime.now()
            duration_seconds=(current_time-booking.p_time).total_seconds()
            hours=round(duration_seconds/3600,1)
            current_cost=round(hours*booking_data['lot'].price,2)

            booking_data['current_hours']=hours
            booking_data['current_cost']=current_cost

            active_bookings.append(booking_data)

    return render_template("my_bookings.html",name=name,active_bookings=active_bookings)


@app.route("/l_time/<name>/<booking_id>")
def mark_l_time(name,booking_id):
    booking=Reserve_parking_spot.query.filter_by(id=booking_id,user_id=name).first()

    if booking and booking.l_time is None:
        booking.l_time=datetime.now()

        spot=get_spot(booking.spot_id)
        spot.status="A"

        db.session.commit()
    
    return redirect(url_for("my_bookings",name=name))


@app.route("/registered_users")
def registered():
    users=User_Details.query.all()
    return render_template("registered_users.html",users=users)

@app.route("/search_users",methods=["GET","POST"])
def searching():
    if request.method=="POST":
        search_text=request.form.get("search")

        if search_text:
            users=User_Details.query.filter(User_Details.email.ilike(f"%{search_text}%")).all()
    
        return render_template("registered_users.html",users=users,search_text=search_text)

    return redirect(url_for("registered"))


@app.route("/edit_profile_admin/<email>",methods=["GET","POST"])
def edit_admin(email):
    user=User_Details.query.filter_by(email=email).first()

    if not user:
        return redirect(url_for("admindashboardfn",name=email))

    p=user.password
    a=user.address
    n=user.full_name
    pi=user.pin_code

    if request.method=="POST":
        em=request.form.get("gmail")
        pwd=request.form.get("password")
        fn=request.form.get("fulnam")
        address=request.form.get("address")
        pin=request.form.get("pincode")

        user.email=em
        user.password=pwd
        user.address=address
        user.pin_code=pin
        user.full_name=fn

        db.session.commit()

        return redirect(url_for("admindashboardfn",name=email,msg="Succesfully edited!"))

    return render_template("edit_admin.html",email=email,password=p,name=n,address=a,pincode=pi)


@app.route("/summary_admin")
def get_admin_summary():
    graph=get_plots_summary()

    graph.savefig("./static/images/p_lots_summary.jpeg")
    graph.clf()  
    return render_template("summary_admin.html")


@app.template_filter('time_diff_hours')
def time_diff_hours(start_time):
    if start_time:
        diff=datetime.now()-start_time
        return round(diff.total_seconds()/3600,1)
    return 0


@app.route("/edit_profile_user/<name>",methods=["GET","POST"])
def edit_pr(name):
    user=User_Details.query.filter_by(email=name).first()

    if request.method=="POST":
        em=request.form.get("gmail")
        pwd=request.form.get("password")
        fn=request.form.get("fulnam")
        address=request.form.get("address")
        pin=request.form.get("pincode")

        user.email=em
        user.password=pwd
        user.address=address
        user.pin_code=pin
        user.full_name=fn

        db.session.commit()

        return redirect(url_for("userdashboardfn",name=name))

    return render_template("edit_user.html",usr=user,name=name)


@app.route("/summary_user/<name>")
def get_user_summary(name):
    #history of bookings of each user
    user_bookings=Reserve_parking_spot.query.filter_by(user_id=name).all()
    
    past_bookings=[]

    for booking in user_bookings:
        booking_data={
            'booking':booking,
            'lot':get_lot(booking.lot_id),
            'spot':get_spot(booking.spot_id)
        }

        if booking.l_time is not None:
            if booking.p_time and booking.l_time:
                hours_diff=(booking.l_time-booking.p_time).total_seconds()/3600
                cost=hours_diff*booking_data['lot'].price
                booking_data['cost']=round(cost,2)
                booking_data['duration']=round(hours_diff,2)

            past_bookings.append(booking_data)
    
    return render_template("summary_user.html", name=name, past_bookings=past_bookings)


#supporter fns
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

def get_plots_summary():
    lots=get_lots()

    summary={}
    i=1

    for lot in lots:
        summary[i]=lot.maximum_number_of_spots
        i+=1

    x_axis=list(summary.keys())
    y_axis=list(summary.values())

    plt.bar(x_axis,y_axis,color="blue",width=0.4)

    plt.title("Parking Lots/Capacities")
    plt.xlabel("Paking Lot")
    plt.ylabel("Capacity")

    return plt

def calc_cost(p_time,l_time,price_per_hour):
    if not p_time or not l_time:
        return 0
    
    hours_diff=(l_time-p_time).total_seconds()/3600

    if hours_diff<1:
        hours_diff=1  #minimum cost

    cost=(hours_diff)*(price_per_hour)

    return round(cost,2)

def get_info_about_spot(sid):
    spot=get_spot(sid)

    if not spot:
        return None
    
    spot_info={
        'spot':spot,
        'current_reservation':None,
        'user_details':None,
        'duration_hours':0,
        'current_cost':0
    }

    if spot.status=="O":
        reserved=Reserve_parking_spot.query.filter_by(spot_id=sid,l_time=None).first()

        if reserved:
            user=User_Details.query.filter_by(email=reserved.user_id).first()
            lot=get_lot(reserved.lot_id)

            current_time = datetime.now()
            
            duration_seconds = (current_time - reserved.p_time).total_seconds()
            
            hours = round(duration_seconds / 3600, 1)
            current_cost = round(hours * lot.price, 2) if lot else 0
            
            spot_info.update({
                'current_reservation': reserved,
                'user_details': user,
                'duration_hours': hours,
                'current_cost': current_cost
            })
    
    return spot_info

def get_user_plots_summary(email):
    #clear existing plot
    plt.clf()
    plt.close('all')
    
    user_bookings = Reserve_parking_spot.query.filter_by(user_id=email).all()
    
    lot_durations = {}
    
    for booking in user_bookings:
        lot = get_lot(booking.lot_id)
        if lot:
            lot_name = f"Lot {booking.lot_id}"
            
            if booking.l_time and booking.p_time:
                # Calculate duration in hours for completed bookings
                duration_hours = (booking.l_time - booking.p_time).total_seconds() / 3600
            else:
                # For active bookings, calculate current duration
                current_time = datetime.now()
                duration_hours = (current_time - booking.p_time).total_seconds() / 3600
            
            if lot_name in lot_durations:
                lot_durations[lot_name] += duration_hours
            else:
                lot_durations[lot_name] = duration_hours
    
    # If no bookings, show empty graph
    if not lot_durations:
        lot_durations = {"No Bookings": 0}

    plt.figure(figsize=(10,6))
    
    x_axis = list(lot_durations.keys())
    y_axis = [round(duration, 1) for duration in lot_durations.values()]
    
    plt.bar(x_axis, y_axis, color="green", width=0.4)
    plt.title("Your Parking History")
    plt.xlabel("Parking Lot")
    plt.ylabel("Total Hours Parked")
   
    
    return plt
