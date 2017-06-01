import unittest
import mock
import json
from datetime import date

from flask_testing import TestCase
from werkzeug.exceptions import BadRequest
from featurerequests import db, app, parse_feature, save_feature_request, to_dict
from models import Feature


class FeatureRequestTestCase(TestCase):


    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        return app
        # return create_app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_new_feature_to_db(self):
        feature = Feature(
            title='A Title',
            description='Some lengthy description',
            client='Client A',
            client_priority=1,
            target_date=date.today(),
            product_area='Policies',
        )
        db.session.add(feature)
        db.session.commit()
        assert feature in db.session

    def test_feature_request_form_renders(self):
        response = self.client.get('/feature-request')
        self.assertIn('Add a feature request', response.data)
        self.assertEqual(response.status_code, 200)

    def test_add_feature_request_ajax_method(self):
        feature = {
            'title': 'A Title',
            'description': 'Some lengthy description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Policies',
        }
        response = self.client.post('/_add_feature_request',
                                    data=json.dumps(feature),
                                    content_type='application/json')
        self.assertEqual(json.loads(response.data), {"status":"success"})
        
    def test_add_feature_request_ajax_method_returns_error_on_invalid_json(self):
        response = self.client.post('/_add_feature_request',
                                    data='invalid json',
                                    content_type='application/json')
        self.assertIn("400", response.data)

    def test_add_feature_request_ajax_method_returns_error_on_missing_item(self):
        feature = {
            'wrongtitle': 'A Title',
            'wrongdescription': 'Some lengthy description',
            'wrongclient': 'Client A',
            'wrongclient_priority': 1,
            'wrongtarget_date': '2017-05-01',
            'wrongproduct_area': 'Policies',
        }
        response = self.client.post('/_add_feature_request',
                                    data=json.dumps(feature),
                                    content_type='application/json')
        self.assertIn("is required", response.data)

    def test_if_parse_feature_returns_a_date_object_for_target_date(self):
        featuremock = mock.Mock()
        featuremock.get_json = mock.Mock(return_value={
            'title': 'A Title',
            'description': 'Some lengthy description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Policies',
        })
        parsed = parse_feature(featuremock)
        self.assertEqual(parsed['target_date'], date(2017, 5, 1))

    def test_if_parse_feature_returns_error_on_invalid_json(self):
        featuremock = mock.Mock()
        featuremock.get_json = mock.Mock()
        featuremock.get_json.side_effect = BadRequest('Whoops! Raise an error.')
        try:
            parsed = parse_feature(featuremock)
        except BadRequest as e:
            error_message = e.description
        self.assertIn('invalid json', error_message)

    def test_if_save_feature_request_saves_to_db(self):
        feature = {
            'title': 'A Title',
            'description': 'Some lengthy description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Policies',
        }

    def test_if_to_dict_returns_dict(self):
        self.add_features_helper()
        features = Feature.query.all()
        fdict = to_dict(features)
        self.assertEqual(type(fdict), type({}))

    def add_features_helper(self):
        feature1 = Feature(
            title='A Title',
            description='Some lengthy description',
            client='Client A',
            client_priority=1,
            target_date=date.today(),
            product_area='Policies',
        )
        db.session.add(feature1)
        db.session.commit()
        

if __name__ == '__main__':
    unittest.main()
