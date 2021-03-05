import json, time
from pathlib import Path
from flask import Response # Flask, request, send_file
from common.exceptions import DummyServerException


def save_settings(req_data, api_dict, default_version, this_res_path):
    """ 더미서버에 미리 응답설정을 하는 임의의 API 
    (example json body)
    {
        'version':'2.5.0', 
        'api_id':'getProductType', 
        'status_code': '200', 
        'test_type':'basic'
        'sleep_time': 3
    }
    """
    req_api_id = req_data.get('api_id')
    req_version = req_data.get('version')
    req_status_code = req_data.get('status_code')
    req_test_type = req_data.get('test_type')
    req_sleep_time = req_data.get('sleep_time')

    if req_api_id in api_dict:
        origin_api_info = api_dict[req_api_id]
        if req_version == None:
            req_version = origin_api_info.get('version')   # 버전값 없으면 기존 설정되어 있는 버전값으로 설정 
        if req_sleep_time == None:
            req_sleep_time = origin_api_info.get('sleep_time')
        # 실제 폴더, 파일이 존재하면 그 때 저장
        get_jsonpath(this_res_path, req_version, req_api_id, req_status_code, req_test_type)
        api_dict.update({req_api_id : {'version':req_version, 'status_code': req_status_code, 'test_type':req_test_type, 'sleep_time':req_sleep_time}})
        return {'version':req_version, 'status_code': req_status_code, 'test_type':req_test_type, 'sleep_time':req_sleep_time}
    else:
        raise DummyServerException(f"The requested api_id is not in the api list")


def get_response_body(this_api_id, api_dict, res_base_path):
    _tmp_dict = api_dict[this_api_id]
    with open(get_jsonpath(res_base_path, _tmp_dict['version'], this_api_id, _tmp_dict['status_code'], _tmp_dict['test_type'])) as json_file:
        _response_body = json.load(json_file)
        json_file.close()
    return _response_body

def get_400error_resp(msg):
    resp = Response(json.dumps({"error_message" : msg}), 
            mimetype='application/json;charset=UTF-8', 
            status=400)
    return resp

def response_wait(second_to_wait):
    if second_to_wait != None and str(type(second_to_wait)) == "<class 'int'>": 
        time.sleep(second_to_wait)

def get_404notfound_resp():
    resp = Response('{"error_message" : "Not Found"}', mimetype='application/json', status=404)
    return resp

def get_500servererr_resp(msg):
    resp = Response(json.dumps({"error_message" : msg}), mimetype='application/json', status=500)
    return resp

def get_jpgfile_dictinfo(this_api_id, api_dict, app_name, jpg_type, base_path):
    _tmp_dict = api_dict[this_api_id]
    return get_jpgfile(base_path, _tmp_dict['version'], this_api_id, app_name, jpg_type)

def get_jpgfile(base_path, version, api_id, app_name, jpg_type):
    _temp_path = base_path
    if Path(_temp_path).exists() == False:
        raise DummyServerException("base path not found in " + _temp_path)
    _temp_path = _temp_path + "/" + version
    if Path(_temp_path).exists() == False:
        raise DummyServerException("version path not found in " + _temp_path)
    _temp_path = _temp_path + "/" + api_id
    if Path(_temp_path).exists() == False:
        raise DummyServerException("api_id path not found in " + _temp_path)
    _temp_path = _temp_path + "/" + app_name
    if Path(_temp_path).exists() == False:
        raise DummyServerException("status_code path not found in " + _temp_path)
    _temp_path = _temp_path + "/" + jpg_type+'.jpg'
    if Path(_temp_path).exists() == False:
        raise DummyServerException("json file not found in " + _temp_path)
    with open(_temp_path, 'rb') as f:
        sample = bytearray(f.read())
        f.close()
    return sample

def get_jsonpath(base_path, version, api_id, status_code, test_type):
    """ 응답 body json파일 경로를 입력값으로부터 찾아서 반환해 주는 유틸리티 함수
    """
    # 현재 파일의 상위 디렉토리 정보를 가져온 후 ./response 디렉토리를 기본 디렉토리로 지정
    _temp_path = base_path
    # print(str(os.path.exists(_temp_path)))
    if Path(_temp_path).exists() == False:
        raise DummyServerException("base path not found in " + _temp_path)
    
    _temp_path = _temp_path + "/" + version
    if Path(_temp_path).exists() == False:
        raise DummyServerException("version path not found in " + _temp_path)

    _temp_path = _temp_path + "/" + api_id
    if Path(_temp_path).exists() == False:
        raise DummyServerException("api_id path not found in " + _temp_path)

    _temp_path = _temp_path + "/" + str(status_code)
    if Path(_temp_path).exists() == False:
        raise DummyServerException("status_code path not found in " + _temp_path)

    _temp_path = _temp_path + "/" + test_type+'.json'
    if Path(_temp_path).exists() == False:
        raise DummyServerException("json file not found in " + _temp_path)
    return _temp_path
