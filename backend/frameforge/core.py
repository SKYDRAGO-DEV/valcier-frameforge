"""Independent deterministic cinematic planning and DAG validation. No external model calls."""
from __future__ import annotations
from collections import deque
from typing import Literal
from pydantic import BaseModel, Field

Genre = Literal['product_hero', 'editorial', 'cinematic', 'ugc_ad']
Camera = Literal['dolly_in', 'orbit', 'pan', 'handheld', 'locked']
Ratio = Literal['9:16', '16:9', '1:1', '4:5', '21:9']

class PlanRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    genre: Genre = 'cinematic'
    movement: Camera = 'dolly_in'
    aspect_ratio: Ratio = '9:16'
    duration_seconds: int = Field(default=12, ge=3, le=60)
    focal_length_mm: int = Field(default=35, ge=14, le=135)
    tone: str = Field(default='premium', min_length=2, max_length=80)

class Node(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    kind: Literal['input','plan','image','video','qa','output']

class Edge(BaseModel):
    source: str
    target: str

class Graph(BaseModel):
    nodes: list[Node] = Field(min_length=1, max_length=100)
    edges: list[Edge] = Field(default_factory=list, max_length=300)

VISUAL = {
    'product_hero': ('macro feature reveal', 'product performance in context', 'hero packshot + call to action'),
    'editorial': ('fashion editorial establishing frame', 'intimate texture and details', 'strong closing silhouette'),
    'cinematic': ('atmospheric establishing scene', 'character or subject development', 'emotional concluding visual'),
    'ugc_ad': ('immediate three-second attention hook', 'demonstration of benefit', 'clear human-oriented call to action'),
}
CAMERA = {
    'dolly_in': 'smooth controlled forward dolly',
    'orbit': 'gentle clockwise orbital camera',
    'pan': 'measured horizontal pan',
    'handheld': 'natural stabilized handheld motion',
    'locked': 'tripod-locked camera',
}

def storyboard(request: PlanRequest) -> dict:
    """Produces a machine-readable shot plan; does not fabricate image/video outputs."""
    total = request.duration_seconds
    durations = [max(1, round(total * .25)), max(1, round(total * .45))]
    durations.append(total - sum(durations))
    if durations[2] < 1:
        durations[1] -= 1 - durations[2]
        durations[2] = 1
    shots = []
    for i, (beat, secs) in enumerate(zip(VISUAL[request.genre], durations), 1):
        expanded = (f"{beat}. Subject: {request.prompt}. Mood: {request.tone}. "
                    f"Camera: {CAMERA[request.movement]}, {request.focal_length_mm}mm lens. "
                    f"Aspect ratio {request.aspect_ratio}. Duration {secs} seconds. "
                    "Preserve consistent product geometry, lighting continuity and legible composition.")
        shots.append({'index': i, 'beat': beat, 'seconds': secs,
                      'camera': request.movement, 'lens_mm': request.focal_length_mm,
                      'expanded_prompt': expanded})
    return {'kind': 'deterministic_storyboard', 'simulated': False, 'media_generated': False,
            'genre': request.genre, 'aspect_ratio': request.aspect_ratio,
            'total_seconds': total, 'shots': shots,
            'note': 'This is a structured shot plan. It is not AI-generated media.'}

def validate_graph(graph: Graph) -> dict:
    ids = [n.id for n in graph.nodes]
    if len(ids) != len(set(ids)):
        return {'valid': False, 'reason': 'duplicate_node_id', 'order': []}
    lookup = set(ids)
    forward = {x: [] for x in ids}
    indegree = {x: 0 for x in ids}
    seen = set()
    for e in graph.edges:
        if e.source not in lookup or e.target not in lookup:
            return {'valid': False, 'reason': 'missing_node', 'order': []}
        if e.source == e.target:
            return {'valid': False, 'reason': 'self_cycle', 'order': []}
        key = (e.source, e.target)
        if key in seen:
            return {'valid': False, 'reason': 'duplicate_edge', 'order': []}
        seen.add(key)
        forward[e.source].append(e.target)
        indegree[e.target] += 1
    queue = deque(x for x in ids if indegree[x] == 0)
    result = []
    while queue:
        source = queue.popleft()
        result.append(source)
        for target in forward[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(result) < len(ids):
        return {'valid': False, 'reason': 'cycle_detected', 'order': []}
    return {'valid': True, 'reason': None, 'order': result}

def enforce_budget(estimated_cents: int, remaining_cents: int) -> bool:
    if estimated_cents < 0 or remaining_cents < 0:
        raise ValueError('Amounts cannot be negative')
    return estimated_cents <= remaining_cents
