import os
import re
import string
import math

from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue

from cs50 import SQL
from helpers import lookup

# configure application
app = Flask(__name__)
JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///mashup.db")

@app.route("/")  #checks for an API key and passes it to the index.html
def index():
    """Render map."""
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")  
    return render_template("index.html", key=os.environ.get("API_KEY"))   

@app.route("/articles", methods=['GET', 'POST'])

def articles():     
    """Look up articles for geo."""      
    # add variable name to the incoming zipcode - http://pset8.cs50.net/articles?geo=02138.
    # "q" is the name of the incoming value per the HTML form  
    geo_input=request.args.get("q")  
    
    #lookup the articles (using lookup function) based on the geo variable  
    geo_articles= lookup(request.args.get("geo"))
    
    #add error handling 
    
    return jsonify(geo_articles)

@app.route("/search")
def search():
    """Search for places that match query."""
    # add variable name to the incoming zipcode (or any other value submitted) - http://pset8.cs50.net/search?q=02138
    # take incoming value from the form and store as variable
    geo_input=request.args.get("q")
    #print(geo_input)
    
    #if the length of the input is 5 and is a digit it's a zipcode
    if (len(geo_input) == 5 and geo_input.isdigit()):
        #print("is zipcode by length and digits" + geo_input)
        
        #return places data for zipcode lookup
        place_data_zip = db.execute("SELECT distinct accuracy, admin_code1, admin_code2, admin_code3, admin_name1, admin_name2, admin_name3, country_code, latitude, longitude, place_name, postal_code FROM places WHERE postal_code like :postal_code", postal_code = geo_input)
        return jsonify(place_data_zip)
    
    #if the length of the input is not 5 and is not a digit it's not a zip
    if not (len(geo_input) == 5 and geo_input.isdigit()):
        #print("is not a zipcode: " + geo_input)
        
        #split the incoming value based on different separators
        geo_input_words = re.split(r'[;,\s]\s*', geo_input)
        #print(geo_input_words)
        #count the number of words from the split
        geo_word_count = len(geo_input_words)
        #print(geo_word_count)
          
        if geo_word_count == 2 and len(geo_input_words[1]) == 2:
            print(geo_input_words[1])
            place_data_city_state = db.execute("SELECT distinct accuracy, admin_code1, admin_code2, admin_code3, admin_name1, admin_name2, admin_name3, country_code, latitude, longitude, place_name, postal_code FROM places WHERE place_name like :place_name AND admin_code1 like :admin_code1", place_name = geo_input_words[0], admin_code1 = geo_input_words[1])
            return jsonify(place_data_city_state)
            
        if geo_word_count == 2 and len(geo_input_words[1]) > 2:
            place_data_city_state = db.execute("SELECT distinct accuracy, admin_code1, admin_code2, admin_code3, admin_name1, admin_name2, admin_name3, country_code, latitude, longitude, place_name, postal_code FROM places WHERE place_name like :place_name AND admin_name1 like :admin_name1", place_name = geo_input_words[0], admin_name1 = geo_input_words[1])
            return jsonify(place_data_city_state)

        if geo_word_count == 3 and len(geo_input_words[1]) == 2 and len(geo_input_words[2]) == 2:
            place_data_city_state_country = db.execute("SELECT distinct accuracy, admin_code1, admin_code2, admin_code3, admin_name1, admin_name2, admin_name3, country_code, latitude, longitude, place_name, postal_code FROM places WHERE place_name like :place_name AND admin_code1 like :admin_code1 AND country_code like :country_code", place_name = geo_input_words[0], admin_code1 = geo_input_words[1], country_code = geo_input_words[2])
            return jsonify(place_data_city_state_country)
            
        if geo_word_count == 3 and len(geo_input_words[1]) > 2 and len(geo_input_words[2]) == 2:
            place_data_city_state_country = db.execute("SELECT distinct accuracy, admin_code1, admin_code2, admin_code3, admin_name1, admin_name2, admin_name3, country_code, latitude, longitude, place_name, postal_code FROM places WHERE place_name like :place_name AND admin_name1 like :admin_name1 AND country_code like :country_code", place_name = geo_input_words[0], admin_name1 = geo_input_words[1], country_code = geo_input_words[2])
            return jsonify(place_data_city_state_country)
        
        return jsonify()
    return jsonify()   

@app.route("/update")  #"back end" that outputs a JSON array of up to 10 places (i.e., cities) that fall within the specified bounds
def update():
    """Find up to 10 places within view."""

    # ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # ensure parameters are in lat,lng format
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
        raise RuntimeError("invalid ne")

    # explode southwest corner into two variables
    (sw_lat, sw_lng) = [float(s) for s in request.args.get("sw").split(",")]

    # explode northeast corner into two variables
    (ne_lat, ne_lng) = [float(s) for s in request.args.get("ne").split(",")]

    # find 10 cities within view, pseudorandomly chosen if more within view
    if (sw_lng <= ne_lng):

        # doesn't cross the antimeridian
        rows = db.execute("""SELECT * FROM places
            WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude AND longitude <= :ne_lng)
            GROUP BY country_code, place_name, admin_code1
            ORDER BY RANDOM()
            LIMIT 10""",
            sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    else:

        # crosses the antimeridian
        rows = db.execute("""SELECT * FROM places
            WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude OR longitude <= :ne_lng)
            GROUP BY country_code, place_name, admin_code1
            ORDER BY RANDOM()
            LIMIT 10""",
            sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    # output places as JSON
    return jsonify(rows)
