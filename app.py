
from flask import Flask, jsonify
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

app = Flask(__name__)

@app.route("/")
def welcome():
    return '''
        <html>
            <head>
                <title>Precipitation</title>
            </head>
            <body style="background-color:powderblue;">
                <h1 style="text-align:center">Welcome to my API, lets do some weather analysis!</h1>
                <h2 style="text-align:center">Available routes:</h2>
                <hr />
                <h3 style="text-align:center"><a href="./api/v1.0/precipitation">/api/v1.0/precipitation</a></h3>
                <h3 style="text-align:center"><a href="./api/v1.0/stations">/api/v1.0/stations</a></h3>
                <h3 style="text-align:center"><a href="./api/v1.0/tobs">/api/v1.0/tobs</a></h3>
                <h3 style="text-align:center"><a href="./api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a></h3>
                <h3 style="text-align:center"><a href="./api/v1.0/2017-01-01/2017-12-31">/api/v1.0/2017-01-01/2017-12-31</a></h3>
            </body>
        </html>
        '''
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    try:
        engine = create_engine("sqlite:///C:/Users/1000204905/Desktop/sqlalchemy-challenge/Resources/hawaii.sqlite")
        # reflect an existing database into a new model
        Base = automap_base()
        # reflect the tables
        Base.prepare(engine, reflect=True)
        # Save references to each table
        Station = Base.classes.station
        Measurement = Base.classes.measurement
        # Create our session (link) from Python to the DB
        session = Session(engine)
        # get the last date in the DB
        last_date = session.query(func.max(Measurement.date).label('last_date')).all()[0][0]
        to_date = pd.to_datetime(last_date)
        to_date = to_date.date()
        # Calculate  the date - one year ago
        year_ago = to_date - dt.timedelta(days=365)
        data = [Measurement.date,func.sum(Measurement.prcp)]
        precipitation = session.query(*data).\
            filter(Measurement.date >= func.strftime("%Y-%m-%d",year_ago)).\
            filter(Measurement.date <= func.strftime("%Y-%m-%d",to_date)).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
        # Transform into dataframe
        precipitation = pd.DataFrame(precipitation, columns=["day","prcp"])
        # update datatype for day
        precipitation["day"] = pd.to_datetime(precipitation["day"])
        # update index to handle plot easily
        precipitation.set_index("day",inplace=True)
        return jsonify({"date":precipitation.to_json()})
    except:
        return jsonify({"error":"The query is not working, verify it "}), 404

@app.route("/api/v1.0/stations")
def stations():
    try:
        engine = create_engine("sqlite:///C:/Users/1000204905/Desktop/sqlalchemy-challenge/Resources/hawaii.sqlite")
        # reflect an existing database into a new model
        Base = automap_base()
        # reflect the tables
        Base.prepare(engine, reflect=True)
        # Save references to each table
        Station = Base.classes.station
        Measurement = Base.classes.measurement
        # Create our session (link) from Python to the DB
        session = Session(engine)
        active_stations = [Station.name,func.count(Measurement.date)]
        active_stations = session.query(*active_stations).filter(Station.station == Measurement.station).group_by(Station.station).order_by(func.count(Station.station).desc()).all()
        active_stations_df = pd.DataFrame(active_stations, columns=["station","rows"])
        active_stations_df.set_index("station",inplace=True)
        active_stations_df["rows"] = active_stations_df['rows'].map('{:,}'.format)
        return jsonify({"data":active_stations_df.to_json()})
    except:
        return jsonify({"error":" The query is not working, verify it"}), 404


@app.route("/api/v1.0/tobs")
def temperature():
    try:
        engine = create_engine("sqlite:///C:/Users/1000204905/Desktop/sqlalchemy-challenge/Resources/hawaii.sqlite")
        # reflect an existing database into a new model
        Base = automap_base()
        # reflect the tables
        Base.prepare(engine, reflect=True)
        # Save references to each table
        Station = Base.classes.station
        Measurement = Base.classes.measurement
        # Create our session (link) from Python to the DB
        session = Session(engine)
        # get the last date in the DB
        last_date = session.query(func.max(Measurement.date).label('last_date')).all()[0][0]
        to_date = pd.to_datetime(last_date)
        to_date = to_date.date()
        # Convert to date
        # Calculate  the date - one year ago
        year_ago = to_date - dt.timedelta(days=365)
        data_max_temp = [Measurement.date, Measurement.tobs]

        temp_data = session.query(*data_max_temp).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= func.strftime("%Y-%m-%d",year_ago)).\
            filter(Measurement.date <= func.strftime("%Y-%m-%d",to_date)).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
        # Transform into dataframe
        temp_data_df = pd.DataFrame(temp_data, columns=["day","temp"])
        # update datatype for day
        temp_data_df["day"] = pd.to_datetime(temp_data_df["day"])
        # update index to handle plot easily
        temp_data_df.set_index("day",inplace=True)
        # See sample data
        return jsonify({"content":temp_data_df.to_json()})
    except:
        return jsonify({"error":" The query is not working, verify it"}), 404



@app.route("/api/v1.0/<start>")
def start_temperature(start):
    try:
        print(f"parameter: {start} - {type(start)}")
        engine = create_engine("sqlite:///C:/Users/1000204905/Desktop/sqlalchemy-challenge/Resources/hawaii.sqlite")
        # reflect an existing database into a new model
        Base = automap_base()
        # reflect the tables
        Base.prepare(engine, reflect=True)
        # Save references to each table
        Station = Base.classes.station
        Measurement = Base.classes.measurement
        # Create our session (link) from Python to the DB
        session = Session(engine)
        data_data_list_temp = [Measurement.date, func.min(Measurement.tobs).label('min_temp'), func.avg(Measurement.tobs).label('avg_temp'), func.max(Measurement.tobs).label('data_max_temp') ]
        temp = session.query(*data_data_list_temp).filter(Measurement.date >= start).group_by(Measurement.date).order_by(Measurement.date).all()
        # Transform into dataframe
        temp_data_df = pd.DataFrame(temp, columns=["day","Min Temp","Avg Temp","Max Temp"])
        # update datatype for day
        temp_data_df["day"] = pd.to_datetime(temp_data_df["day"])
        # update index to handle plot easily
        temp_data_df.set_index("day",inplace=True)
        # See sample data
        return jsonify({"content":temp_data_df.to_json()})
    except:
        return jsonify({"error":" The query is not working, verify it"}), 404


@app.route("/api/v1.0/<start>/<end>")
def range_temperature(start,end):
    try:
        engine = create_engine("sqlite:///C:/Users/1000204905/Desktop/sqlalchemy-challenge/Resources/hawaii.sqlite")
        # reflect an existing database into a new model
        Base = automap_base()
        # reflect the tables
        Base.prepare(engine, reflect=True)
        # Save references to each table
        Station = Base.classes.station
        Measurement = Base.classes.measurement
        # Create our session (link) from Python to the DB
        session = Session(engine)
        list_temp = [Measurement.date, func.min(Measurement.tobs).label('min_temp'), func.avg(Measurement.tobs).label('avg_temp'), func.max(Measurement.tobs).label('data_max_temp') ]
        temp = session.query(*list_temp).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
        # Transform into dataframe
        temp_data_df = pd.DataFrame(temp, columns=["day","Min Temp","Avg Temp","Max Temp"])
        # update datatype for day
        temp_data_df["day"] = pd.to_datetime(temp_data_df["day"])
        # update index to handle plot easily
        temp_data_df.set_index("day",inplace=True)
        # See sample data
        return jsonify({"date":temp_data_df.to_json()})
    except:
        return jsonify({"error":" The query is not working, verify it"}), 404



if __name__ == "__main__":
    app.run(debug=True)
