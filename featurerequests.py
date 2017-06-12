import json
import uuid
import datetime

from flask import Flask, render_template, request, abort
from werkzeug.exceptions import BadRequest

from models import db, Feature

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feature-request")
def feature_request():
    return render_template("feature-request.html")


@app.route("/api/v1/feature", methods=["GET", "POST"])
@app.route("/api/v1/feature/<feature_id>", methods=["GET", "PUT", "DELETE"])
def feature_api_endpoint(feature_id=None):
    """ REST API endpoint for AJAX """

    if request.method == "GET":
        if feature_id:
            feature = get_feature_by_id(feature_id)
            return query_to_json(feature)
        else:
            features = Feature.query.all()
            return query_to_json(features)

    if request.method == "POST":
        feature = parse_feature(request)
        reorder_client_priorities(feature)
        save_feature_request(feature)
        return json.dumps({'status': 'success'})

    if request.method == "PUT":
        updates = parse_feature(request)
        reorder_client_priorities(updates)
        feature = get_feature_by_id(feature_id)
        for key, val in updates.iteritems():
            setattr(feature, key, val)
        db.session.commit()
        return json.dumps({'status': 'success'})

    if request.method == "DELETE":
        feature = get_feature_by_id(feature_id)
        db.session.delete(feature)
        db.session.commit()
        return json.dumps({'status': 'success'})


#################
#    Helpers
#################

def get_feature_by_id(feature_id):
    """
    makes sure a feature id is supplied and returns a feature object
    :param feature_id: a feature id as a string
    :return: a feature class model object
    """
    if not feature_id:
        abort(400, 'feature id required')
    feature_id = uuid.UUID(feature_id)
    feature = Feature.query.get(feature_id)
    if not feature:
        abort(400, "couldn't find the requested id")
    return feature


def query_to_json(query):
    """
    turns a sqlalchemy query object into a json string
    :param query: sqlalchemy object
    """
    features = []
    for feature in query:
        features.append({
            'id': str(feature.id),
            'title': feature.title,
            'description': feature.description,
            'client': feature.client,
            'client_priority': feature.client_priority,
            'target_date': str(feature.target_date),
            'product_area': feature.product_area
        })
    return json.dumps(features)


def parse_feature(request):
    """
    Check data is valid json and turn the date field
    into a python date object and priority into an int
    :param request: a flask request object
    :return: feature dict
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
        if not feature:
            raise BadRequest
    except BadRequest:
        abort(400, 'invalid json')
    for field in required_fields:
        if not feature.get(field):
            abort(400, 'whoops, "' + field + '" is required')
    feature['target_date'] = datetime.datetime.strptime(feature['target_date'], '%Y-%m-%d').date()
    feature['client_priority'] = int(feature['client_priority'])
    return feature


def reorder_client_priorities(feature):
    """
    Reorders client priorities within the database if the given feature
    has a client_id that conflicts with an existing one.
    :param feature: a feature as a dict
    """
    client_features = Feature.query.filter_by(client=feature['client'])
    reorder = False
    priority_list = []
    for i in client_features:
        priority_list.append(i.client_priority)
        if i.client_priority == feature['client_priority']:
            reorder = True
            priority = feature['client_priority']
    if reorder:
        for i in client_features:
            if i.client_priority >= priority:
                i.client_priority += 1

        db.session.commit()


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


def create_db():
    """ Helper to create a local test database """
    new_app = Flask(__name__)
    new_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db'
    new_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(new_app)
    db.create_all(app=new_app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
