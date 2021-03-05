#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 한단계 상위폴더를 sys path에 추가
import json
import time
import requests
from datetime import datetime
from waitress import serve
from flask import Flask, Response, request, send_file
from pathlib import Path
import argparse
import traceback
from common.exceptions import DummyServerException
from common import dummy_utils as util

app = Flask(__name__)
app.url_map.strict_slashes = False	# url 끝에 / 슬래시에 대해 엄격하게 체크할 것인지 설정  
app.config['MAX_CONTENT_LENGTH'] = 1600 * 1024 * 1024
res_base_path = None

default_version = "2.5.0"
default_type = "basic"

code_cache = {} # 현재 진행/공유할 값을 전달하기 위한 저장소
api_dict = {} # API 별 설정 값을 저장할 저장소. 앱 최초 실행시*초기화 수행 시 api_dict_origin 값으로 update
api_dict_origin = {
    'gw_healthcheck':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'get_producttype':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'get_gwinfo':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'upload_studydata':{'version':default_version,'status_code':202, 'test_type':default_type, 'sleep_time':0},
    'result_callback':{'version':default_version,'status_code':202, 'test_type':default_type, 'sleep_time':0}
}   # 각 API의 호출정보를 디폴트값 및 

################# GCM 관련 ################
@app.route('/gcm/product-type/', methods=['GET'])
@app.route('/gcm/product-type', methods=['GET'])
def get_producttype():
    try:
        this_api_id = 'get_producttype'

        _response_code = api_dict[this_api_id].get('status_code')
        response_body = util.get_response_body(this_api_id, api_dict,get_current_respath())
        resp = Response(json.dumps(response_body), mimetype='application/json;charset=UTF-8', status=_response_code)
        resp.headers['Access-Control-Allow-Origin'] = '*'

        print(f"{request.remote_addr} - - {datetime.now()} \"{request.method} {request.full_path} {request.scheme}\" {resp.status_code} {resp.content_length}")
        
        util.response_wait(api_dict.get(this_api_id).get("sleep_time"))
    except DummyServerException as ex:
        resp = util.get_400error_resp(ex.value)
    return resp


############### GI 관련 ################
# 참조. https://github.com/lunit-io/gateway-interface/blob/develop/API.md 
@app.route('/', methods=['GET'])
def gw_healthcheck():
    try:
        this_api_id = 'gw_healthcheck'

        _response_code = api_dict[this_api_id].get('status_code')
        response_body = util.get_response_body(this_api_id, api_dict,get_current_respath())
        resp = Response(json.dumps(response_body), mimetype='application/json;charset=UTF-8', status=_response_code)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print(f"{request.remote_addr} - - {datetime.now()} \"{request.method} {request.full_path} {request.scheme}\" {resp.status_code} {resp.content_length}")
        util.response_wait(api_dict.get(this_api_id).get("sleep_time"))
    except DummyServerException as ex:
        resp = util.get_400error_resp(ex.value)
    return resp


@app.route('/settings/info/', methods=['GET'])
@app.route('/settings/info', methods=['GET'])
def get_gwinfo():
    try:
        this_api_id = 'get_gwinfo'

        _response_code = api_dict[this_api_id].get('status_code')
        response_body = util.get_response_body(this_api_id, api_dict,get_current_respath())
        resp = Response(json.dumps(response_body), mimetype='application/json;charset=UTF-8', status=_response_code)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print(f"{request.remote_addr} - - {datetime.now()} \"{request.method} {request.full_path} {request.scheme}\" {resp.status_code} {resp.content_length}")
        util.response_wait(api_dict.get(this_api_id).get("sleep_time"))
    except DummyServerException as ex:
        resp = util.get_400error_resp(ex.value)
    return resp
            


############ 아래는 dummy_xx 에 공통적인 내용. 유틸이나 클래스로 따로 빼면?  ###############
@app.route('/dummy-setting', methods=['POST'])
def save_setting():
    try: 
        return Response(json.dumps(util.save_settings(request.get_json(), api_dict, default_version, get_current_respath())), mimetype='application/json', status=200)
    except DummyServerException as ex:
        return util.get_400error_resp(ex.value)
    except Exception:
        return util.get_500servererr_resp("Failed to set dummy-setting - " + traceback.print_stack())

@app.route('/dummy-settings', methods=['POST'])
def save_settings():
    try: 
        return Response(json.dumps(util.save_settings(request.get_json(), api_dict, default_version, get_current_respath())), mimetype='application/json', status=200)
    except DummyServerException as ex:
        return util.get_400error_resp(ex.value)
    except Exception:
        return util.get_500servererr_resp("Failed to set dummy-setting - " + traceback.print_stack())



@app.route('/dummy-setting', methods=['GET'])
def get_settings():
    resp = Response(json.dumps(api_dict), mimetype='application/json;charset=UTF-8', status=200)
    return resp

@app.route('/dummy-reset', methods=['GET'])
def dummy_reset():
    api_dict.update({'get_producttype':{'version':default_version,'status_code':200, 'test_type':default_type},
        'get_gwinfo':{'version':default_version,'status_code':200, 'test_type':default_type},
        'upload_studydata':{'version':default_version,'status_code':202, 'test_type':default_type},
        'result_callback':{'version':default_version,'status_code':202, 'test_type':default_type}
    })

    resp = Response(json.dumps(api_dict), mimetype='application/json;charset=UTF-8', status=200)
    return resp

def init_api_dict():
    """ 현재 각 API별 응답하는 현황(api_dict)을 초기화하는 함수로, 별도 저장되어 있는 초기값으로 api_dict를 update합니다. 
    최초 서버 기동시, 임의로 dummy_reset 수행시 호출됩니다
    """
    api_dict.update(api_dict_origin)

def get_current_respath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    base_path = dirname + '/responses'
    return base_path

# def get_cache_value(cache_key):
#     if cache_key in code_cache:
#         return code_cache[cache_key]
#     else:
#         return None

if __name__ == '__main__':
    res_base_path = get_current_respath()
    init_api_dict()
    serve(app, host='0.0.0.0', port=7730)
    
