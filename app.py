#Climate App

#################################################
# Import Dependencies
#################################################

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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Todd's Climate app!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start_date&gt;<br/>"
        f"/api/v1.0/&lt;start_date&gt/&lt;end_date&gt<br/>"
        f"<br/>"
        f"FYI: Dates must be in yyyy-mm-dd format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    # Query for dates and pcp
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query for stations
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    #query for date and tobs where dates are the last year of the db
    query_date = dt.date(2017,8,23) - dt.timedelta(days = 365)
    temp_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_date).\
        filter(Measurement.station == 'USC00519281').all()
    
    session.close()

    all_temps = list(np.ravel(temp_results))
    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def calc_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates."""
    
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    temps = list(np.ravel(data))
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def date_range(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates."""

    
    range_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_range = list(np.ravel(range_data))
    return jsonify(temp_range)


if __name__ == '__main__':
    app.run(debug=True)

