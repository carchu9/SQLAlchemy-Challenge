# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create a  base
Base = automap_base()

# reflect an existing database into a new model

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()
print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Start at the homepage
@app.route("/")
def welcome():
# List all the available routes.
    return (
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"Note: To access values between the start and end dates, please enter the date using the following format: yyyy-mm-dd"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    preciptitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-24").\
    filter(Measurement.date <= "2017-08-23").\
    order_by(Measurement.date).all()

    # Close Session
    session.close()    

    # Return the JSON representation of your dictionary

    prcp_data = {date: prcp for date, prcp in preciptitation_data}

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def station():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    stations_data = session.query(Station.station).\
    order_by(Station.station).all()

    # Close Session
    session.close()

    total_stations = list(np.ravel(stations_data))

    return jsonify(total_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    previous = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).\
    filter(Measurement.station == "USC00519281").filter(Measurement.date >= previous).all()

    # Close Session
    session.close()

    # Return a JSON list of temperature observations for the previous year.
    total_tobs = []
    for date, tobs, prcp in results:
        result_dict = {}
        result_dict["date"] = date
        result_dict["prcp"] = prcp
        result_dict["tobs"] = tobs
        total_tobs.append(result_dict)

    return jsonify(total_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    start_tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    # Close Session
    session.close()

    start_tobs_list = []
    for min, max, avg in start_tobs:
        start_dict = {}
        start_dict["min"] = min
        start_dict["max"] = max
        start_dict["avg"] = avg
        start_tobs_list.append(start_dict)
    return jsonify(start_tobs_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    start_end_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Close Session
    session.close()

    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    start_end_list = []
    for min, max, avg in start_end_data:
        start_end_dict = {}
        start_end_dict["minimum"] = min
        start_end_dict["Average"] = avg
        start_end_dict["Max"] = max
        start_end_list.append(start_end_dict)
    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)
