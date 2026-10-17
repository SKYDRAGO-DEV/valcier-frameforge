"""FRAMEFORGE backend API v0.1; demo provider only, no generative AI claims."""
from __future__ import annotations
import json
import os
import secrets
from datetime import datetime, timezone
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field
from .core import PlanRequest, Graph, storyboard, validate_graph, enforce_budget
from .db import connect, initialize


def now():
    return datetime.now(timezone.utc).isoformat()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get('FRAMEFORGE_LOCAL_DEMO') != '1' and not os.environ.get('FRAMEFORGE_API_TOKEN'):
        raise RuntimeError('Set FRAMEFORGE_API_TOKEN or FRAMEFORGE_LOCAL_DEMO=1 for local-only use')
    initialize()
    yield

app = FastAPI(title='VALCIER FRAMEFORGE API', version='0.1.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173',
                   'http://localhost:3000', 'http://127.0.0.1:3000'],
    allow_credentials=False, allow_methods=['GET','POST','DELETE'],
    allow_headers=['Authorization','Content-Type','Idempotency-Key'])


def auth(authorization: str | None = Header(default=None)):
    if os.environ.get('FRAMEFORGE_LOCAL_DEMO') == '1':
        return
    token = os.environ.get('FRAMEFORGE_API_TOKEN', '')
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Bearer token required')
    if not secrets.compare_digest(authorization[7:].encode(), token.encode()):
        raise HTTPException(status_code=401, detail='Invalid token')

@app.get('/health')
def health():
    return {'status':'ok', 'version':'0.1.0', 'mode':'demo', 'actual_media_generation':False}

@app.get('/api/v1/providers', dependencies=[Depends(auth)])
def providers():
    return {'providers':[{'id':'demo', 'enabled':True, 'generates_media':False,
                         'cost_cents':0, 'capabilities':['storyboard','job_lifecycle']},
                        {'id':'external', 'enabled':False, 'generates_media':True,
                         'reason':'No independent licensed provider configured'}]}

@app.post('/api/v1/storyboards', dependencies=[Depends(auth)])
def build_storyboard(request: PlanRequest):
    return storyboard(request)

class ProjectRequest(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    settings: PlanRequest

@app.post('/api/v1/projects', status_code=201, dependencies=[Depends(auth)])
def create_project(project: ProjectRequest):
    entry = {'id':str(uuid4()),'title':project.title,'created_at':now(),
             'settings':project.settings.model_dump(), 'storyboard':storyboard(project.settings)}
    with connect() as db:
        db.execute('INSERT INTO projects(id,title,created_at,settings,storyboard) VALUES(?,?,?,?,?)',
                   (entry['id'], entry['title'], entry['created_at'],json.dumps(entry['settings']),json.dumps(entry['storyboard'])))
    return entry

def _project_row(row):
    d = dict(row)
    d['settings'] = json.loads(d['settings'])
    d['storyboard'] = json.loads(d['storyboard'])
    return d

@app.get('/api/v1/projects', dependencies=[Depends(auth)])
def list_projects():
    with connect() as db:
        return [_project_row(r) for r in db.execute('SELECT * FROM projects ORDER BY created_at DESC')]

@app.get('/api/v1/projects/{project_id}', dependencies=[Depends(auth)])
def read_project(project_id: str):
    with connect() as db:
        row = db.execute('SELECT * FROM projects WHERE id=?',(project_id,)).fetchone()
    if not row: raise HTTPException(404, 'Unknown project')
    return _project_row(row)

class SubmitRequest(BaseModel):
    project_id: str
    provider: str = 'demo'
    max_cost_cents: int = Field(default=0, ge=0, le=10_000_000)

@app.post('/api/v1/jobs', status_code=201, dependencies=[Depends(auth)])
def submit_job(request: SubmitRequest, idempotency_key: str | None = Header(default=None, alias='Idempotency-Key')):
    if request.provider != 'demo':
        raise HTTPException(422, 'External provider disabled: no licensed provider configured')
    if idempotency_key is not None and not 5 <= len(idempotency_key) <= 128:
        raise HTTPException(422,'Idempotency-Key must be 5-128 characters')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        if idempotency_key:
            old = db.execute('SELECT * FROM jobs WHERE idem_key=?',(idempotency_key,)).fetchone()
            if old:
                if old['project_id'] != request.project_id or old['provider'] != request.provider:
                    raise HTTPException(409,'Idempotency key reused with different request')
                return _job_row(old)
        if not db.execute('SELECT 1 FROM projects WHERE id=?',(request.project_id,)).fetchone():
            raise HTTPException(404,'Unknown project')
        estimate = 0
        if not enforce_budget(estimate, request.max_cost_cents):
            raise HTTPException(402,'Budget exceeded')
        entry={'id':str(uuid4()), 'project_id':request.project_id, 'status':'queued',
               'provider':'demo', 'estimated_cents':estimate,'result_json':None,
               'error':None,'idem_key':idempotency_key, 'created_at':now(), 'updated_at':now()}
        db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?)',tuple(entry.values()))
        db.execute('COMMIT')
        return _job_row(entry)

def _job_row(row):
    d = dict(row)
    d['result_json'] = json.loads(d['result_json']) if d['result_json'] else None
    return d

@app.get('/api/v1/jobs', dependencies=[Depends(auth)])
def list_jobs():
    with connect() as db:
        return [_job_row(r) for r in db.execute('SELECT * FROM jobs ORDER BY created_at DESC')]

@app.get('/api/v1/jobs/{job_id}', dependencies=[Depends(auth)])
def job_detail(job_id: str):
    with connect() as db:
        r=db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
    if not r: raise HTTPException(404,'Unknown job')
    return _job_row(r)

@app.post('/api/v1/jobs/{job_id}/run', dependencies=[Depends(auth)])
def demo_run(job_id: str):
    """Manual deterministic demo execution, NOT media generation nor distributed worker."""
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        r=db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
        if not r: raise HTTPException(404,'Unknown job')
        if r['status'] == 'cancelled': raise HTTPException(409,'Cancelled job cannot run')
        if r['status'] == 'completed': return _job_row(r)
        if r['status'] != 'queued': raise HTTPException(409,'Job is not queued')
        db.execute('UPDATE jobs SET status=?,updated_at=? WHERE id=?',('running',now(),job_id))
        project = db.execute('SELECT * FROM projects WHERE id=?',(r['project_id'],)).fetchone()
        result = {'type':'structured_plan', 'media_generated':False,
                  'message':'Demo provider executed storyboard plan; no AI media generated.',
                  'storyboard':json.loads(project['storyboard'])}
        db.execute('UPDATE jobs SET status=?,result_json=?,updated_at=? WHERE id=?',
                   ('completed',json.dumps(result),now(),job_id))
        db.execute('COMMIT')
        return job_detail(job_id)

@app.post('/api/v1/jobs/{job_id}/cancel', dependencies=[Depends(auth)])
def cancel_job(job_id: str):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        r=db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
        if not r: raise HTTPException(404,'Unknown job')
        if r['status'] != 'queued': raise HTTPException(409,'Only queued jobs can be cancelled')
        db.execute('UPDATE jobs SET status=?,updated_at=? WHERE id=?',('cancelled',now(),job_id))
        db.execute('COMMIT')
    return job_detail(job_id)

@app.post('/api/v1/graphs/validate', dependencies=[Depends(auth)])
def graph_validate(graph: Graph):
    return validate_graph(graph)

class SaveGraph(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    graph: Graph

@app.post('/api/v1/graphs', status_code=201, dependencies=[Depends(auth)])
def save_graph(request: SaveGraph):
    validation=validate_graph(request.graph)
    if not validation['valid']:
        raise HTTPException(422,validation)
    record={'id':str(uuid4()),'title':request.title,
            'graph':request.graph.model_dump(),'created_at':now()}
    with connect() as db:
        db.execute('INSERT INTO graphs VALUES(?,?,?,?)',
                   (record['id'],record['title'],json.dumps(record['graph']),record['created_at']))
    return {**record,'execution_order':validation['order']}

@app.get('/api/v1/graphs', dependencies=[Depends(auth)])
def list_graphs():
    with connect() as db:
        rows=db.execute('SELECT * FROM graphs ORDER BY created_at DESC').fetchall()
    return [{**dict(r),'graph':json.loads(r['graph'])} for r in rows]

class CostCheck(BaseModel):
    estimated_cents: int = Field(ge=0)
    budget_cents: int = Field(ge=0)

@app.post('/api/v1/budget/check', dependencies=[Depends(auth)])
def budget_check(request: CostCheck):
    return {'allowed':enforce_budget(request.estimated_cents,request.budget_cents),
            'currency':'USD', 'estimated_cents':request.estimated_cents,
            'budget_cents':request.budget_cents,
            'note':'Caller-supplied estimate; not a provider quote.'}

_WEB = Path(__file__).resolve().parent.parent / 'web'
app.mount('/static', StaticFiles(directory=str(_WEB)), name='static')

@app.get('/', include_in_schema=False)
def local_console():
    return FileResponse(_WEB / 'index.html')
