#beginning of app

from flask import Flask #importing library

app=None

def setup_app():
    app=Flask(__name__) #initialisation
    #sqlite connection-pending
    app.app_context().push() #to access other modules
    app.debug=True

setup_app()

from backend.controllers import *

if __name__=='__main__':
    app.run() #running the app. debug=True=>displays the errors