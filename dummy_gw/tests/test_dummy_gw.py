#-*- coding: utf-8 -*-
import pytest
import os, sys
import json
# from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dummy_gw import dummy_gw

@pytest.fixture
def client():
    dummy_gw.app.config['TESTING'] = True
    dummy_gw.init_api_dict()
    with dummy_gw.app.test_client() as client:
        yield client 
    # client.get('/dummy-reset')

def test_get_producttype(client):
    resp = client.get('/gcm/product-type')
    # 1) 디폴트 응답 확인
    assert 200 == resp.status_code
    resp_json = resp.json
    assert "cxr3" == resp_json['product_type']

    # 2) preset 해서 mmg 응답 확인
    test_status_code = 200
    headers = {'Content-Type': 'application/json'}
    payload = {
        'version':'2.5.0', 
        'api_id':'get_producttype', 
        'status_code': test_status_code, 
        'test_type':'mmg_response'
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 200
    
    resp = client.get('/gcm/product-type')
    assert 200 == resp.status_code
    resp_json = resp.json
    assert "mmg" == resp_json['product_type']


def test_get_gwinfo(client):
    resp = client.get('/settings/info')
    # 1) 디폴트 응답 확인
    assert 200 == resp.status_code
    resp_json = resp.json
    assert resp_json['app_name'] != None
    assert "Lunit DICOM Gateway" == resp_json['app_name']
    assert resp_json['cxr'] != None
    assert resp_json['mmg'] == None

    # 2) preset 해서 mmg 응답 확인
    test_status_code = 200
    headers = {'Content-Type': 'application/json'}
    payload = {
        'version':'2.5.0', 
        'api_id':'get_gwinfo', 
        'status_code': test_status_code, 
        'test_type':'basic'
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 200
    
    resp = client.get('/settings/info')
    assert 200 == resp.status_code
    resp_json = resp.json
    assert resp_json['app_name'] != None
    assert "Lunit DICOM Gateway" == resp_json['app_name']
    assert resp_json['cxr'] != None
    assert resp_json['mmg'] == None

def test_upload_studydata(client):
    this_api_path = '/upload/dicom-study-data/'+'a8120440-c16f-4e94-aaf7-9de678612ccf'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "transaction_id": "a8120440-c16f-4e94-aaf7-9de678612ccf",
        "gi_callback": "http://10.220.150.118:8234/gateway/gi/airesult",
        "partner_name": "GE_Edison",
        "partner_ip": "192.168.1.77"
    }
    resp = client.post(this_api_path, headers=headers, data=json.dumps(payload, indent=4))
    # requests.post(gateway_url, files=my_file, data=my_data)

    # 1) 디폴트 응답 확인
    assert 202 == resp.status_code
    resp_json = resp.json
    assert 'message' in resp_json
    assert 'Request Accepted Successfully' == resp_json['message']
    
    # 2) preset 해서 10초 지연 응답 확인
    test_status_code = 202
    headers = {'Content-Type': 'application/json'}
    payload = {
        'version':'2.5.0', 
        'api_id':'upload_studydata', 
        'status_code': test_status_code, 
        'test_type':'basic',
        'sleep_time' : 2
    }
    resp = client.post('/dummy-setting', headers=headers, data=json.dumps(payload, indent=4))
    assert resp.status_code == 200
    
    payload = {
        "transaction_id": "a8120440-c16f-4e94-aaf7-9de678612ccg",
        "gi_callback": "http://10.220.150.118:8234/gateway/gi/airesult",
        "partner_name": "GE_Edison",
        "partner_ip": "192.168.1.77"
    }
    resp = client.post(this_api_path, headers=headers, data=json.dumps(payload, indent=4))
    assert 202 == resp.status_code
    resp_json = resp.json
    assert 'Request Accepted Successfully' == resp_json['message']

def test_result_callback(client):
    test_transaction_id = 'a8120440-c16f-4e94-aaf7-9de678612ccf'

    this_api_path = '/upload/dicom-study-data/'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "transaction_id": test_transaction_id,
        "gi_callback": "http://10.220.150.118:8234/gateway/gi/airesult",
        "partner_name": "GE_Edison",
        "partner_ip": "192.168.1.77"
    }
    resp = client.post(this_api_path, headers=headers, data=json.dumps(payload, indent=4))
    assert 202 == resp.status_code

    # 1) 디폴트 응답 확인
    resp = client.get('/result_callback/')
    assert 500 == resp.status_code
    resp_json = resp.json