import os
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from frameforge.api import app
from frameforge.core import PlanRequest, storyboard, Graph, validate_graph, enforce_budget

@pytest.fixture
def client(tmp_path:Path, monkeypatch):
    monkeypatch.setenv('FRAMEFORGE_DB_PATH',str(tmp_path/'test.sqlite'))
    monkeypatch.setenv('FRAMEFORGE_LOCAL_DEMO','1')
    with TestClient(app) as c:
        yield c

PLAN = {'prompt':'Silver wristwatch on a marble pedestal','genre':'product_hero',
        'movement':'orbit','aspect_ratio':'9:16','duration_seconds':12,
        'focal_length_mm':50,'tone':'high-end'}

def test_storyboard_consistent_duration():
    for n in range(3,61):
        plan=storyboard(PlanRequest(**{**PLAN,'duration_seconds':n}))
        assert sum(x['seconds'] for x in plan['shots'])==n
        assert all(x['seconds']>0 for x in plan['shots'])
        assert plan['media_generated'] is False

def test_graph_valid_toposort():
    g=Graph(nodes=[{'id':'a','kind':'input'},{'id':'b','kind':'plan'},{'id':'c','kind':'video'}],
            edges=[{'source':'a','target':'b'},{'source':'b','target':'c'}])
    assert validate_graph(g)=={'valid':True,'reason':None,'order':['a','b','c']}

def test_graph_cycle_detected():
    g=Graph(nodes=[{'id':'a','kind':'input'},{'id':'b','kind':'output'}],
            edges=[{'source':'a','target':'b'},{'source':'b','target':'a'}])
    assert validate_graph(g)['reason']=='cycle_detected'

def test_graph_unknown_node():
    g=Graph(nodes=[{'id':'a','kind':'input'}],edges=[{'source':'a','target':'b'}])
    assert validate_graph(g)['reason']=='missing_node'

def test_budget():
    assert enforce_budget(0,0)
    assert enforce_budget(99,100)
    assert not enforce_budget(101,100)
    with pytest.raises(ValueError): enforce_budget(-1,1)

def test_create_and_list(client):
    r=client.post('/api/v1/projects',json={'title':'Watch commercial','settings':PLAN})
    assert r.status_code==201
    assert r.json()['storyboard']['total_seconds']==12
    r2=client.get('/api/v1/projects')
    assert len(r2.json())==1
    assert r2.json()[0]['title']=='Watch commercial'

def test_job_idempotency_and_execution(client):
    p=client.post('/api/v1/projects',json={'title':'Watch commercial','settings':PLAN}).json()
    payload={'project_id':p['id'],'provider':'demo','max_cost_cents':0}
    headers={'Idempotency-Key':'job-001'}
    first=client.post('/api/v1/jobs',json=payload,headers=headers)
    assert first.status_code==201
    again=client.post('/api/v1/jobs',json=payload,headers=headers)
    assert again.json()['id']==first.json()['id']
    job_id=first.json()['id']
    result=client.post(f'/api/v1/jobs/{job_id}/run')
    assert result.status_code==200
    assert result.json()['status']=='completed'
    assert result.json()['result_json']['media_generated'] is False
    assert client.post(f'/api/v1/jobs/{job_id}/run').status_code==200

def test_cancelled_job_is_not_run(client):
    p=client.post('/api/v1/projects',json={'title':'Project','settings':PLAN}).json()
    j=client.post('/api/v1/jobs',json={'project_id':p['id']}).json()
    assert client.post(f"/api/v1/jobs/{j['id']}/cancel").json()['status']=='cancelled'
    assert client.post(f"/api/v1/jobs/{j['id']}/run").status_code==409

def test_external_provider_disabled(client):
    p=client.post('/api/v1/projects',json={'title':'Project','settings':PLAN}).json()
    assert client.post('/api/v1/jobs',json={'project_id':p['id'],'provider':'paid'}).status_code==422

def test_graph_save_and_reject_cycles(client):
    good={'nodes':[{'id':'a','kind':'input'},{'id':'b','kind':'output'}],
          'edges':[{'source':'a','target':'b'}]}
    assert client.post('/api/v1/graphs',json={'title':'Pass','graph':good}).status_code==201
    bad={**good,'edges':[{'source':'a','target':'b'},{'source':'b','target':'a'}]}
    assert client.post('/api/v1/graphs',json={'title':'Fail','graph':bad}).status_code==422

def test_protected_auth(tmp_path, monkeypatch):
    monkeypatch.setenv('FRAMEFORGE_DB_PATH',str(tmp_path/'auth.db'))
    monkeypatch.delenv('FRAMEFORGE_LOCAL_DEMO',raising=False)
    monkeypatch.setenv('FRAMEFORGE_API_TOKEN','very-long-secret-for-tests')
    with TestClient(app) as c:
        assert c.get('/api/v1/projects').status_code==401
        assert c.get('/api/v1/projects',headers={'Authorization':'Bearer wrong'}).status_code==401
        assert c.get('/api/v1/projects',headers={'Authorization':'Bearer very-long-secret-for-tests'}).status_code==200

def test_validation_bad_input(client):
    assert client.post('/api/v1/storyboards',json={**PLAN,'duration_seconds':300}).status_code==422
    assert client.post('/api/v1/storyboards',json={**PLAN,'prompt':'x'}).status_code==422
    assert client.get('/health').json()['actual_media_generation'] is False

def test_local_console_assets(client):
    home=client.get('/')
    assert home.status_code==200
    assert 'Creative Studio' in home.text
    assert 'No paid AI inference attached' in home.text
    assert client.get('/static/app.js').status_code==200
    assert client.get('/static/style.css').status_code==200
