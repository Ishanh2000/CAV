# AUM SHREEGANESHAYA NAMAH||

################ IMPORTS ################
import flask
from flask import request, jsonify
from flask_cors import cross_origin


################ CONFIGURATIONS ################
app = flask.Flask(__name__)
app.config["DEBUG"] = True

##############################################################################
################ APIS (SEPARATE INTO MULTIPLE FILES LATER ON) ################
##############################################################################

@app.route('/', methods=['GET'])
@cross_origin()
def home():
  return jsonify({"g": ["AUM SHREEGANESHAAYA NAMAH||"]})


################ RUN APPLICATION ################
if (__name__ == "__main__"):
  
  # run only after importing parent graph
  app.run(host="0.0.0.0", port="5000", debug=True)
