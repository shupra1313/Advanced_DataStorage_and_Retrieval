from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from flask import Flask, jsonify
import datetime as dt


engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """Returns links to all the API routes pertaining to climate analysis"""
    return(f"Welcome to the Climate Analysis<br>"
            f"All available routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query for the dates and precipitation from the last year.
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.

    """Return list of precipitation values and dates as json"""
    ppt = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date.between ('2016-08-23','2017-08-23')).\
    order_by(Measurement.date).all()
    ppt_values = []
    for value in ppt:
        ppt_dict={}
        ppt_dict["date"] = value.date
        ppt_dict["prcp"] = value.prcp
        ppt_values.append(ppt_dict)

    return jsonify(ppt_values)

@app.route("/api/v1.0/stations")
def station():
    # Return a JSON list of stations from the dataset.
    query = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(query))

@app.route("/api/v1.0/tobs")
def tobs():
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    
    year_ago_ppt = dt.date(2017,8,23) - dt.timedelta(days =365)
    
    query = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date>=year_ago_ppt).\
    order_by(Measurement.date).all()

    tobs_values = []
    for value in query:
        tobs_dict = {}
        query['date']=value.date
        query['tobs']=value.tobs
        tobs_values.append(tobs_dict)

    return jsonify(tobs_values)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates 
# greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
# for dates between the start and end date inclusive.

def return_weather(start, end=None):
    if end is None:
        end = get_most_recent_date()

    weather_from_to = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),
                                     func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    list_data = []
    for record in  weather_from_to:
        list_data.append({'TMIN': record[0],
                     'TAVG': record[1],
                     'TMAX': record[2]})

    return jsonify(list_data)


if __name__ == '__main__':
    app.run(debug=True)
