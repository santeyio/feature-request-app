import unittest
import uuid
import mock
import json
from datetime import date

from flask_testing import TestCase
from werkzeug.exceptions import BadRequest
from featurerequests import db, app, parse_feature, save_feature_request, query_to_json, reorder_client_priorities
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
        response = self.client.post('/api/v1/feature',
                                    data=json.dumps(feature),
                                    content_type='application/json')
        self.assertEqual(json.loads(response.data), {"status":"success"})
        
    def test_add_feature_api_endpoint_POST_returns_error_on_invalid_json(self):
        response = self.client.post('/api/v1/feature',
                                    data='invalid json',
                                    content_type='application/json')
        self.assertIn("400", response.data)

    def test_add_feature_api_endpoint_POST_returns_error_on_missing_item(self):
        feature = {
            'wrongtitle': 'A Title',
            'wrongdescription': 'Some lengthy description',
            'wrongclient': 'Client A',
            'wrongclient_priority': 1,
            'wrongtarget_date': '2017-05-01',
            'wrongproduct_area': 'Policies',
        }
        response = self.client.post('/api/v1/feature',
                                    data=json.dumps(feature),
                                    content_type='application/json')
        self.assertIn("is required", response.data)

    def test_add_feature_api_endpoint_POST_reorders_items_correctly(self):
        self.add_features_helper()
        initial_feature_priority = Feature.query.filter_by(title="A Title")
        self.assertEqual(initial_feature_priority[0].client_priority, 1)
        feature = {
            'title': 'A New Title',
            'description': 'Some new lengthy description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Policies',
        }
        response = self.client.post('/api/v1/feature',
                                    data=json.dumps(feature),
                                    content_type='application/json')
        self.assertIn("success", response.data)
        updated_feature_priority = Feature.query.filter_by(title="A Title")
        self.assertEqual(initial_feature_priority[0].client_priority, 2)

    def test_add_feature_api_endpoint_DELETE_deletes_items(self):
        self.add_features_helper()
        feature = Feature.query.filter_by(title="A Title")
        f = feature[0]
        response = self.client.delete('/api/v1/feature/' + str(feature[0].id),
                                      content_type='application/json')
        feature = Feature.query.filter_by(title="A Title")
        self.assertFalse(feature.count())

    def test_add_feature_api_endpoint_GET_returns_valid_json(self):
        self.add_features_helper()
        response = self.client.get('/api/v1/feature',
                                   content_type='application/json')
        decoded_json = json.loads(response.data)
        self.assertEqual(type(decoded_json), type([]))

    def test_add_feature_api_endpoint_PUT_updates_object(self):
        self.add_features_helper()
        feature = Feature.query.filter_by(title="A Title")
        fid = str(feature[0].id)
        updates = {
            'title': 'A Title',
            'description': 'updated description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Claims',
        }
        response = self.client.put('/api/v1/feature/' + fid,
                                   data=json.dumps(updates),
                                   content_type='application/json')
        feature_updated = Feature.query.filter_by(title="A Title")
        self.assertEqual(feature_updated[0].description, updates['description'])
         

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

    # def test_if_parse_feature_returns_id_when_passed_id_and_no_id_when_not_passed_id(self):
        # featuremock = mock.Mock()
        # featuremock.get_json = mock.Mock(return_value={
            # 'title': 'A Title',
            # 'description': 'Some lengthy description',
            # 'client': 'Client A',
            # 'client_priority': 1,
            # 'target_date': '2017-05-01',
            # 'product_area': 'Policies',
        # })
        # parsed_no_id = parse_feature(featuremock)
        # self.assertFalse(parsed_no_id.get('id'))
        # featuremock_with_id = mock.Mock()
        # featuremock_with_id.get_json = mock.Mock(return_value={
            # 'id': str(uuid.uuid4()),
            # 'title': 'A Title',
            # 'description': 'Some lengthy description',
            # 'client': 'Client A',
            # 'client_priority': 1,
            # 'target_date': '2017-05-01',
            # 'product_area': 'Policies',
        # })
        # parsed_with_id = parse_feature(featuremock_with_id)
        # self.assertTrue(parsed_with_id.get('id'))
        

    def test_if_save_feature_request_saves_to_db(self):
        feature = {
            'title': 'A Title',
            'description': 'Some lengthy description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Policies',
        }

    def test_if_query_to_json_returns_valid_json(self):
        self.add_features_helper()
        features = Feature.query.all()
        fdict = query_to_json(features)
        assert json.loads(fdict)

    def test_if_reorder_client_priorities_reorders_clients(self):
        self.add_features_helper()
        initial_feature_priority = Feature.query.filter_by(title="A Title")
        self.assertEqual(initial_feature_priority[0].client_priority, 1)
        new_feature = {
            'title': 'A New Title',
            'description': 'Some new lengthy description',
            'client': 'Client A',
            'client_priority': 1,
            'target_date': '2017-05-01',
            'product_area': 'Policies',
        }
        reorder_client_priorities(new_feature)
        initial_feature_priority = Feature.query.filter_by(title="A Title")
        self.assertEqual(initial_feature_priority[0].client_priority, 2)

    def add_features_helper(self):
        feature1 = Feature(
            title='A Title',
            description='Some lengthy description',
            client='Client A',
            client_priority=1,
            target_date=date.today(),
            product_area='Policies',
        )
        feature2 = Feature(
            title='Another Title',
            description='Some other lengthy description',
            client='Client A',
            client_priority=2,
            target_date=date.today(),
            product_area='Claims',
        )
        db.session.add(feature1)
        db.session.add(feature2)
        db.session.commit()
        

if __name__ == '__main__':
    unittest.main()
