# Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Inspect database
inspector = inspect(engine)
inspector.get_table_names()

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Homepage & all available routes
@app.route("/")
def welcome():
    """List of all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature Data @ Most Active Station for Last Year: /api/v1.0/tobs<br/>"
        f"Temperature stats from start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stats from start to end date (yyyy-mm-dd):/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# Precipitation Query
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session (link) from Python to the DB
    session = Session(engine)

    # Query date & precipitation from Measurement table:
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Convert query results to dictionary using DATE as the key & PRCP as the value
    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of all stations"""
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)
    
# Query the dates and temperature observations of the most active station for the last year of data
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Most active station:
    most_active = 'USC00519281'
    # Find most recent date in dataset & convert to correct format
    session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest = dt.date(2017, 8, 23).isoformat()
    # Calculate the date one year from the last date in data set.
    year_diff = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Put it all together to get original request
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).\
        filter((Measurement.date<= latest) & (Measurement.date >= year_diff)).\
        order_by(Measurement.date.desc()).all()
    session.close()

    #Convert query results to dictionary
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)
    
    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(tobs_data)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def temp_start(start):
    #Create session (link) from Python to the DB
    session = Session(engine)

    # Query date & tobs functions from Measurement table:
    sel = [func.min(Measurement.tobs),
      func.max(Measurement.tobs),
      func.avg(Measurement.tobs)]
    results = session.query(*sel).\
        filter(Measurement.date <= start).all()
    session.close()

     #Convert query results to dictionary
    tobs_start = []
    for date, tmin, tmax, tavg in results:
        start_dict = {}
        start_dict["date"] = date
        start_dict["tmin"] = tmin
        start_dict["tmax"] = tmax
        start_dict["tavg"] = tavg
        tobs_start.append(start_dict)

    # Return a json list of dates & temps
    return jsonify(tobs_start)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    #Create session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs),
      func.max(Measurement.tobs),
      func.avg(Measurement.tobs)]
    results = session.query(*sel).\
        filter((Measurement.date <= start) & (Measurement.date>= end)).all()
    session.close()

     #Convert query results to dictionary
    start_end = []
    for date, tmin, tmax, tavg in results:
        start_end_dict = {}
        start_end_dict["date"] = date
        start_end_dict["tmin"] = tmin
        start_end_dict["tmax"] = tmax
        start_end_dict["tavg"] = tavg
        start_end.append(start_end_dict)

    # Return a json list of dates & temps
    return jsonify(start_end)

if __name__ == '__main__':
    app.run(debug=True)