# se-qa-tools
## dummy-server
### version2
version2
------------------------------
> Requirements:   

1) 응답바디로 반환할 json 파일의 깔끔한 분리    

2) API 자동화에 활용할 수 있도록 동적으로(바로바로) 응답값을 변경하는 기능 제공   


------------------------------
> Main Features   

1) dummy-setting 기능   
dummy서버의 API가 어떤 응답을 줄지 사전 설정하는 API 추가   

**(POST) /dummy-setting**   

``` json
{
    "version":"2.7.0", 
    "api_id":"result_getcontour",
    "status_code": 200, 
    "test_type":"basic",
    "sleep_time" : 0
}
```

2) 사전 준비한 폴더와 dummy-setting을 이용한 동적 응답 지원      
 - version : 해당 버전명 폴더 하위에서 탐색      
 - api_id : 해당 api_id 이름을 가진 폴더 하위 탐색    
 - status_code : 해당 응답코드(200, 400 등) 이름의 폴더 하위에서 탐색   
 - test_type : 해당 파일명을 가진 json 바디를 읽어 반환    

3) 디폴트 응답   
별도 dummy-setting을 하지 않아도 각 API별 디폴트 응답을 유지   
**(GET) /dummy-setting** : 각 API별 디폴트 응답 확인    


------------------------------   
> 필요(설치) 라이브러리   

- pip install flask_uuid : 유니크한 uuid 값 생성   
- pip install waitress : flask 더미서버 관련   
- pip install pytz : 시간 기록   
- pip install flask : flask 더미서버 관련   
- pip install requests : DUMMY_GW에서 callback API 호출시 사용   
- pip install botocore : DUMMY_IS에서 s3 upload 관련   
- pip install boto3 : DUMMY_IS에서 s3 upload 관련   



