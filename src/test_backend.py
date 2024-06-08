# -*- coding: utf-8 -*-

import requests, json, time

url = 'http://127.0.0.1:5678'

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_query():
    for i in range(0, 100, 10):
        _url = url + '/query'
        params = {
            "query": "婚姻法",
            "mode": "blurred",
            "judge": "",
            "law": "",
            "begin": i,
            "end": i + 10,
        }
        json_str = json.dumps(params)
        beg = time.time()
        response = requests.get(_url, headers=headers, data=json_str)
        end = time.time()
        print(end - beg)
        assert response.status_code == 200
        content = response.content.decode('unicode-escape')
        content = json.loads(content)
    
def test_query2():
    _url = url + '/query'
    params = {
        "query": "名誉权受到了侵犯",
        "mode": "blurred",
        "judge": "",
        "law": "",
        "begin": 0,
        "end": 10,
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

def test_accurate():
    _url = url + '/query'
    params = {
        "query": "婚姻法",
        "mode": "accurate",
        "judge": "",
        "law": "",
        "begin": 0,
        "end": 10,
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

def test_filter():
    _url = url + '/query'
    params = {
        "query": "婚姻法",
        "mode": "accurate",
        "judge": "韦威助 OR 陈淑佩",
        "law": "",
        "begin": 0,
        "end": 10,
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

def test_advanced():
    _url = url + '/query'
    params = {
        "query": "婚姻法 AND 离婚",
        "mode": "accurate",
        "judge": "",
        "law": "",
        "begin": 0,
        "end": 10,
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

def test_judge():
    _url = url + '/query-judge'
    params = {
        "query": "韦威助",
        "begin": 0,
        "end": 10,
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

def test_law():
    _url = url + '/query-laws'
    params = {
        "query": "婚姻法",
        "begin": 0,
        "end": 10,
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

def test_expand():
    _url = url + '/expand'
    params = {
        "query": "婚姻",
    }
    json_str = json.dumps(params)
    beg = time.time()
    response = requests.get(_url, headers=headers, data=json_str)
    end = time.time()
    print(end - beg)
    assert response.status_code == 200
    content = response.content.decode('unicode-escape')
    content = json.loads(content)

test_query()
test_query2()
test_accurate()
test_filter()
test_advanced()
test_judge()
test_law()
test_expand()