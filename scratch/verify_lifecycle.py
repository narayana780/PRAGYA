import urllib.request
import json
import sys

DESC_SCENARIO_ID = '22222222-3333-4444-5555-666666666603'

# 1. Start Lab Session
start_req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/v1/labs/{DESC_SCENARIO_ID}/sessions',
    data=b'',
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(start_req) as resp:
    session_data = json.loads(resp.read().decode())
    session_id = session_data['id']
    print(f"Started Session ID: {session_id}")
    print(f"Current Step: {session_data['current_step']}")

# 2. Step 1: Calculate Central Tendency
s1_req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/v1/lab-sessions/{session_id}/actions',
    data=json.dumps({
        'step_number': 1,
        'action_type': 'CALCULATE_CENTRAL_TENDENCY',
        'action_payload': {
            'target_column': 'per_capita_expenditure_inr',
            'metrics': ['MEAN', 'MEDIAN']
        }
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(s1_req) as resp:
    res1 = json.loads(resp.read().decode())
    print(f"Step 1 Correct: {res1['is_correct']}, Score Awarded: {res1['score_awarded']}")
    print(f"Step 1 Feedback: {res1['feedback']}")

# 3. Step 2: Calculate Dispersion
s2_req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/v1/lab-sessions/{session_id}/actions',
    data=json.dumps({
        'step_number': 2,
        'action_type': 'CALCULATE_DISPERSION',
        'action_payload': {
            'target_column': 'per_capita_expenditure_inr',
            'metrics': ['MIN', 'MAX', 'STD_DEV']
        }
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(s2_req) as resp:
    res2 = json.loads(resp.read().decode())
    print(f"Step 2 Correct: {res2['is_correct']}, Score Awarded: {res2['score_awarded']}")
    print(f"Step 2 Feedback: {res2['feedback']}")

# 4. Step 3: Interpret Skewness
s3_req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/v1/lab-sessions/{session_id}/actions',
    data=json.dumps({
        'step_number': 3,
        'action_type': 'INTERPRET_SKEWNESS',
        'action_payload': {
            'skewness_diagnosis': 'RIGHT_SKEWED',
            'recommended_central_measure': 'MEDIAN'
        }
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(s3_req) as resp:
    res3 = json.loads(resp.read().decode())
    print(f"Step 3 Correct: {res3['is_correct']}, Score Awarded: {res3['score_awarded']}")
    print(f"Step 3 Feedback: {res3['feedback']}")

# 5. Complete Session
comp_req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/v1/lab-sessions/{session_id}/complete',
    data=b'',
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(comp_req) as resp:
    comp_data = json.loads(resp.read().decode())
    print("\n=== POST /complete Response ===")
    print(f"Total Score: {comp_data['total_score']}")
    print(f"Percentage: {comp_data['percentage']}%")
    print(f"Passed: {comp_data['passed']}")
    print(f"Evidence ID: {comp_data['evidence_id']}")
    print(f"actions_history present in complete response: {'actions_history' in comp_data}")
    print(f"actions count: {len(comp_data.get('actions_history', []))}")

# 6. Call GET /api/v1/lab-sessions/{session_id}/result
res_req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/v1/lab-sessions/{session_id}/result',
    headers={'Accept': 'application/json'}
)
with urllib.request.urlopen(res_req) as resp:
    result_json = json.loads(resp.read().decode())
    print("\n=== GET /result API JSON Response ===")
    print(json.dumps(result_json, indent=2))

# 7. Call Web Frontend Result Page
web_req = urllib.request.Request(
    f'http://127.0.0.1:3000/employee/labs/{DESC_SCENARIO_ID}/result?sessionId={session_id}',
    headers={'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(web_req) as resp:
    html = resp.read().decode()
    print("\n=== Web Frontend Result Page ===")
    print(f"HTTP Status: {resp.status}")
    print(f"Contains Scenario Title: {'District' in html}")
    print(f"Contains Analytical Execution Audit: {'Execution Audit' in html or 'Step' in html}")
    print(f"Contains Evidence Created: {'Competency Evidence' in html}")
    print(f"Contains Test this Skill: {'Test this Skill' in html}")
    print(f"Contains Reassess Competency: {'Reassess Competency' in html}")
    print(f"Runtime TypeError absent: {'TypeError' not in html and 'Cannot read properties' not in html}")
