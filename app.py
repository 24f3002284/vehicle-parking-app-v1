#beginning of app

from flask import Flask #importing library
from backend.models import db

app=None

def setup_app(): 
    app=Flask(__name__) #initialisation(ie., instance of flask or flask object is created)
    
    #this block=>db configuration(connecting flask instance(object) to db)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///parking_made_easy.sqlite3" #having db file
    #sqlite connection-nest line
    db.init_app(app) #flask app connected to db(sqlalchemy)

    app.app_context().push() #to access(interact with) other modules
    app.debug=True #throws error if any

setup_app()

from backend.controllers import *

if __name__=='__main__': #this line is not a must. this line => run this app by considering app.py as the main fn
    app.run() #running the app. debug=True=>displays the errors