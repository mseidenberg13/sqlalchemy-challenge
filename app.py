import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, date, time
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"List all available api routes:<br/>"
        f" <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Returns date and precipitation amount<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns a list of Stations (ID and Name)<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"Returns the temperature observations for the last year of data<br/><br/>"
        f"/api/v1.0/start<br/>"
        f"Enter start date, year-month-day<br/>"
        f"Returns minimum, maximum, and average temperatures from a start date<br/><br/>"
        f"/api/v1.0/start/end<br/>"
        f"Enter start date and end date, year-month-day<br/>"
        f"Returns minimum, maximum, and average temperatures from a date range"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        prcp_data.append(prcp_dict)  

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()
    
    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_data.append(station_dict)
    
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23", Measurement.date <= "2017-08-23").all()
    
    temp_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        temp_data.append(temp_dict)  

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    temps_results = list(np.ravel(temp_stats))
    
    min_temp = temps_results[0]
    max_temp = temps_results[1]
    avg_temp = temps_results[2]
    
    temp_data= []
    temp_dict = [{"Start Date": start},
                       {"Minimum Temperature": min_temp},
                       {"Maximum Temperature": max_temp},
                       {"Average Temperature": avg_temp}]

    temp_data.append(temp_dict)
    
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temp_results = list(np.ravel(temp_stats))
    
    min_temp = temp_results[0]
    max_temp = temp_results[1]
    avg_temp = temp_results[2]
    
    temp_data = []
    temp_dict = [{"Start Date": start_date},
                       {"End Date": end_date},
                       {"Minimum Temperature": min_temp},
                       {"Maximum Temperature": max_temp},
                       {"Average Temperature": avg_temp}]

    temp_data.append(temp_dict)
    
    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)