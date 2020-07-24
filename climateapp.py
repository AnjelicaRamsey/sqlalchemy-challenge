# imports

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
from datetime import datetime as dt, datetime
from datetime import timedelta


# db engine

#ref for check_same_thread: https://docs.python.org/3/library/sqlite3.html
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)


#  Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# assign measurement/station classes to its var Measurement/Station

Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
#============================================================
# create session
session = Session(engine)

#============================================================
# Flask
app = Flask(__name__)

#============================================================
# app routes
app.config["JSON_SORTKEYS"] = False

#home base
@app.route("/")
def index():
    return (
        f"-------------------------<br>"
        f"List all available api routes.:<br>"
        f"-------------------------<br>"
        f"Last Year's Precipation: /api/v1.0/precipitation<br/>"
        f"All Stations: /api/v1.0/stations<br/>"
        f"Last Year's Date and Temp Observation: /api/v1.0/tobs<br/>"        
        f"Min, Avg, Max Temp api route option: /api/v1.0/2012-05-15<br/>"
        f"Min, Avg, Max Temp given (api route option) a start and end date: /api/v1.0/2015-09-12/2015-09-13<br/>")
    
@app.route("/api/v1.0/precipitation")    
def precip():
    results = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= '2016-07-20')\
    .filter(Measurement.date <= '2017-07-20')\
    .order_by(Measurement.date)
    
    precipitation_data = []
    for r in results:
        prcp_dict = {}
        prcp_dict['date'] = r.date
        prcp_dict['prcp'] = r.prcp
        prcp_data.append(prcp_dict)

    return jsonify(precipitation_data)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    #query for the data, practicing join even though station table has both columns queried below
    results = session.query(Station.name, Measurement.station)\
    .filter(Station.station == Measurement.station)\
    .group_by(Station.name).all()

    stations_df = []
    for r in results:
        stations_dict = {}
        stations_dict['name']    = r.name
        stations_dict['station'] = r.station
        stations_df.append(stations_dict)
    
    return jsonify(stations_df)


# Query for the dates and temperature observations from a year from the last data point. Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date >= '2016-07-20')\
    .filter(Measurement.date <= '2017-07-20')\
    .order_by(Measurement.date)

    tobs_df = []
    for r in results:
        tobs_dict = {}
        tobs_dict['date'] = r.date
        tobs_dict['tobs'] = r.tobs
        tobs_df.append(tobs_dict)
    #
    #  Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_df)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def stats_start(start):

    results = session.query\
    (func.min(Measurement.tobs).label('min'),\
    func.avg(Measurement.tobs).label('avg'),\
    func.max(Measurement.tobs).label('max'))\
    .filter(Measurement.date >= start).all()
    

    START_df = []
    for r in results:
        start_stats_dict = {}
        start_stats_dict['Start Date'] = start
        start_stats_dict['Min Temp'] = r.min
        start_stats_dict['Avg Temp'] = r.avg
        start_stats_dict['Max Temp'] = r.max
        START_df.append(start_stats_dict)
    
    return jsonify(START_df)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def stats_start_end(start, end):

    results = session.query(func.min(Measurement.tobs).label('min'),\
    func.avg(Measurement.tobs).label('avg'),\
    func.max(Measurement.tobs).label('max'))\
    .filter(Measurement.date >= start)\
    .filter(Measurement.date <= end).all()

    startend_df = []
    for r in results:
       updatedlist= {}
       updatedlist['Start Date'] = start
       updatedlist['End Date'] = end
       updatedlist['Min Temp'] = r.min
       updatedlist['Avg Temp'] = r.avg
       updatedlist['Max Temp'] = r.max
       startend_df.append(updatedlist)
    
    return jsonify(startend_df)
