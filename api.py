# AUM SHREEGANESHAAYA NAMAH|| AUM NAMAH SHIVAAYA|| AUM SHREEHANUMATE NAMAH|| AUM SHREESEETAARAAMAAYA NAMAH||
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

import config
from CAV import CAV

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Content-Type"


@app.route("/")
@cross_origin()
def hello_world():
  return "Hello, World!"


@app.route("/simulate", methods=["POST"])
@cross_origin()
def simulate():
  try:
    # request.json is our graph
    config.WPs = request.json["waypoints"]
    config.NBs = request.json["neighbours"]
    config.cars = request.json["cars"]
    config.sectors = request.json["sectors"]
    config.carsSectors = request.json["carsSectors"]
    config.startServer()

    print("\n######## CAV EXECUTION STARTS #########\n")

    CAVs, l_cars = [], len(config.cars)
    for car in config.cars: # Initialize
      cav = CAV(car)
      CAVs.append(cav)

    for i in range(l_cars): # Start
      CAVs[i].thread.start()
    
    trajData = {} # trajectories

    for i in range(l_cars): # Wait for End
      CAVs[i].thread.join()
      CAVs[i].__del__()
      with open(f"logFiles/CAV_{CAVs[i].ID}_traj.json") as f: trajData[f"{CAVs[i].ID}"] = json.load(f)

    print("\n######## CAV EXECUTION STOPS #########\n")

    return trajData

  except:
    return "Bad Input Format", 400
