#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 1단계 상위폴더를 sys path에 추가
import json, time, uuid, datetime
from pytz import utc
from waitress import serve
from flask_uuid import FlaskUUID
from flask import Flask, Response, request, send_file
from pathlib import Path
import traceback
import boto3
from botocore.client import Config
from common.exceptions import DummyServerException
from common import dummy_utils as util

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['MAX_CONTENT_LENGTH'] = 1600 * 1024 * 1024
res_base_path = None

default_version = "2.7.0"
# default_code = 200
default_type = "basic"
S3_BUCKET_NAME = 'insight-backend-aws-s3-test-bucket-ap-northeast-2'

code_cache = {} # 현재 진행/공유할 값을 전달하기 위한 저장소
api_dict = {} # API 별 설정 값을 저장할 저장소. 앱 최초 실행시*초기화 수행 시 api_dict_origin 값으로 update
api_dict_origin = {'result_upload':{'version':default_version,'status_code':201, 'test_type':default_type, 'sleep_time':1},
    'mmg_result_predict':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'cxr_result_predict':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getscore':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getreport':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getcontour':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getcombined':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getjpg':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getcontour_v2':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_getcombined_v2':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_upload_s3_get':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'result_upload_s3_post':{'version':default_version,'status_code':201, 'test_type':default_type, 'sleep_time':0},
    'connection_check':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'health_check':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0},
    'test':{'version':default_version,'status_code':200, 'test_type':default_type, 'sleep_time':0}
}   # 각 API의 호출정보를 디폴트값 및 

@app.route('/', methods=['GET'])
def connection_check():
    this_api_id = 'connection_check'
    _response_code = api_dict[this_api_id].get('status_code')
    response_body = util.get_response_body(this_api_id, api_dict,get_current_respath())
    resp = Response(json.dumps(response_body), mimetype='application/json', status=_response_code)
    util.response_wait(api_dict.get(this_api_id).get("sleep_time"))
    print(f"{request.remote_addr} - - {utc.localize(datetime.datetime.utcnow())} \"{request.method} {request.full_path} {request.scheme}\" {resp.status_code} {resp.content_length}")
    return resp

@app.route('/health', methods=['GET'])
def health_check():
    this_api_id = 'health_check'
    _response_code = api_dict[this_api_id].get('status_code')
    response_body = util.get_response_body(this_api_id, api_dict,get_current_respath())
    resp = Response(json.dumps(response_body), mimetype='application/json', status=_response_code)
    util.response_wait(api_dict.get(this_api_id).get("sleep_time"))
    print(f"{request.remote_addr} - - {utc.localize(datetime.datetime.utcnow())} \"{request.method} {request.full_path} {request.scheme}\" {resp.status_code} {resp.content_length}")
    return resp


############ 아래는 dummy_xx 에 공통적인 내용. 유틸이나 클래스로 따로 빼면?  ###############
@app.route('/dummy-setting', methods=['POST'])
def save_settings():
    """ 특정 API의 응답정보를 요청된 값으로 반환합니다. 
    요청 바디는 아래와 같으며, version, sleep_time 값은 선택입력으로 입력되지 않으면 디폴트값이 적용됩니다. 
    {
        'version':'2.7.0', 
        'api_id':'result_getscore',
        'status_code': test_status_code, 
        'test_type':'basic',
        sleep_time : int(초)
    }
    """
    try: 
        return Response(json.dumps(util.save_settings(request.get_json(), api_dict, default_version, get_current_respath())), mimetype='application/json', status=200)
    except DummyServerException as ex:
        return util.get_400error_resp(ex.value)
    except Exception:
        return util.get_500servererr_resp("Failed to set dummy-setting - " + traceback.print_stack())

@app.route('/dummy-setting', methods=['GET'])
def get_settings():
    """ 현재 각 API별 응답하는 현황(api_dict)을 반환합니다
    """
    return Response(json.dumps(api_dict), mimetype='application/json;charset=UTF-8', status=200)

@app.route('/dummy-reset', methods=['GET'])
def dummy_reset():
    """ init_api_dict() 함수를 불러 초기화하고 초기화된 api 응답정보를 반환합니다
    """
    init_api_dict()
    return Response(json.dumps(api_dict), mimetype='application/json;charset=UTF-8', status=200)

def init_api_dict():
    """ 현재 각 API별 응답하는 현황(api_dict)을 초기화하는 함수로, 별도 저장되어 있는 초기값으로 api_dict를 update합니다. 
    최초 서버 기동시, 임의로 dummy_reset 수행시 호출됩니다
    """
    api_dict.update(api_dict_origin)

def get_current_respath():
    """ 현재 파일의 상위 폴더를 절대경로로 반환한 후 응답값 json 정보가 있는 'responses' 폴더명을 붙여 반환합니다 
    """
    dirname = os.path.dirname(os.path.abspath(__file__))
    base_path = dirname + '/responses'
    return base_path

# def get_cache_value(cache_key):
#     if cache_key in code_cache:
#         return code_cache[cache_key]
#     else:
#         return None


if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=8888, threaded=True) # run by flask
    res_base_path = get_current_respath()
    init_api_dict() #최초 실행 시 api_dict origin 값으로 초기화 실행 
    serve(app, host='0.0.0.0', port=7720)
