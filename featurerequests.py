import json
import datetime

from flask import Flask, render_template, request, abort 
from werkzeug.exceptions import BadRequest

from models import db, Feature

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/feature-request")
def feature_request():
    return render_template("feature-request.html")     


@app.route("/_add_feature_request", methods=["POST"])
def add_feature_request():
    feature = parse_feature(request)

    # add to db
    save_feature_request(feature)
    return json.dumps({'status': 'success'})


@app.route("/_get_feature_requests", methods=["POST"])
def get_feature_requests():
    features = Feature.query.all()
    return json.dumps(to_dict(features))


#################
#    Helpers
#################

def to_dict(query):
    """
    turns a sqlalchemy query object into a dict
    :param query: sqlalchemy object
    """
    features = {}
    for feature in query:
        features[str(feature.id)] = {
            'title': feature.title,
            'description': feature.description,
            'client': feature.client,
            'client_priority': feature.client_priority,
            'target_date': str(feature.target_date),
            'product_area': feature.product_area
        }
    return features
            

def parse_feature(request):
    """
    Check data is valid json and turn the date field
    into a python date object
    """
    required_fields = [
        'title',
        'description',
        'client',
        'client_priority',
        'target_date',
        'product_area'
    ]
    try:
        feature = request.get_json() 
        if not feature: raise BadRequest
    except BadRequest:
        abort(400, 'invalid json')
    for field in required_fields:
        if not feature.get(field):
            abort(400, 'whoops, "' + field + '" is required')
    dateobject = datetime.datetime.strptime(feature['target_date'], '%Y-%m-%d').date()
    feature['target_date'] = dateobject
    return feature


def save_feature_request(feature):
    """
    Saves a feature dictionary into the database
    :param feature: a dictionary of feature request data
    """
    db.session.add(Feature(
        title=feature.get('title'),
        description=feature.get('description'),
        client=feature.get('client'),
        client_priority=feature.get('client_priority'),
        target_date=feature.get('target_date'),
        product_area=feature.get('product_area')
    ))
    db.session.commit()


if __name__ == "__main__":
    app.run()
