#-*- coding: utf-8 -*-
import pytest
import os, sys
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dummy_be import dummy_be

@pytest.fixture
def client():
    dummy_be.app.config['TESTING'] = True
    dummy_be.init_api_dict()
    with dummy_be.app.test_client() as client:
        yield client 
    client.get('/dummy-reset')

def test_upload_cxr3(client):
    print("deleted")

def test_upload_mmg(client):
    print("deleted!!")


def test_upload_withpreset(client):
    test_status_code = 400
    headers = {'Content-Type': 'application/json'}
    payload = {
        'version':'2.7.0', 
        'api_id':'result_upload', 
        'status_code': test_status_code, 
        'test_type':'notfound'
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 200

    payload = {
        "app": "mmg",
        "uuid": "2cb150a1-105f-4d0d-8d5a-cdd8aae7af17",
        "file": "http://0.0.0.0:6008/data/dicom/2cb150a1-105f-4d0d-8d5a-cdd8aae7af17.dcm",
        "valid": True,
        "width": 2800,
        "height": 3408,
        "created_at": "2020-05-23T03:51:30.669854Z"
    }
    resp = client.post('/mmg/dcm/', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == test_status_code
    resp_json = resp.json
    assert "Not found." == resp_json['message']
    assert "not_found" == resp_json['code']

def test_predict_cxr3(client):
    print("deleted!!")

def test_predict_mmg(client):
    print("deleted!!")
    
def test_predict_withpreset(client):
    print("deleted!!")

def test_result_getscore_withpreset(client):
    print("deleted!!")

def test_result_getreport_withpreset(client):
    print("deleted!!")

def test_result_getcontour_withpreset(client):
    print("deleted!!")

def test_result_getcombined_withpreset(client):
    print("deleted!!")


########################################################
def test_settings_request(client):
    headers = {'Content-Type': 'application/json'}
    payload = {
        'version':'2.7.0', 
        'api_id':'test', 
        'status_code': 200, 
        'test_type':'basic',
        'sleep_time':30
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 200
    assert '{"version": "2.7.0", "status_code": 200, "test_type": "basic", "sleep_time": 30}' == resp.data.decode('utf-8')

    resp = client.get('/dummy-setting')
    assert resp.status_code == 200
    print(resp.data.decode('utf-8'))

def test_settings_invalidid(client):
    headers = {'Content-Type': 'application/json'}
    payload = {
        'version':'2.7.0', 
        'api_id':'notexistid', 
        'status_code': 200, 
        'test_type':'basic'
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 400
    assert '{"error_message": "The requested api_id is not in the api list"}' == resp.data.decode('utf-8')


def test_dummysetting_noversion(client):
    test_status_code = 400
    headers = {'Content-Type': 'application/json'}
    payload = {
        # 'version':'2.7.0', 
        'api_id':'result_upload', 
        'status_code': test_status_code, 
        'test_type':'notfound'
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 200
    resp_json = resp.json
    assert "2.7.0" == resp_json.get('version')
    resp = client.get('/dummy-setting')
    assert resp.status_code == 200

