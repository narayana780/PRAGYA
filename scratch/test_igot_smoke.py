import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. Fetch current employee
try:
    req = urllib.request.Request(f"{BASE_URL}/api/v1/employees/me")
    with urllib.request.urlopen(req) as resp:
        me = json.loads(resp.read().decode("utf-8"))
        emp_id = me["id"]
        print(f"Logged in employee: {me['full_name']} ({emp_id})")
except Exception as e:
    print(f"Error fetching employee: {e}")
    emp_id = "00000000-0000-0000-0000-000000000001"

# 2. Get course
try:
    req = urllib.request.Request(f"{BASE_URL}/api/v1/recommendations/me?limit=1", headers={"X-Employee-Id": emp_id})
    with urllib.request.urlopen(req) as resp:
        recs = json.loads(resp.read().decode("utf-8"))
        if recs:
            course_id = recs[0]["learning_item"]["id"]
            print(f"Testing with recommended course: {recs[0]['learning_item']['title']} ({course_id})")
        else:
            course_id = "1aac14b6-4bbd-4d01-bcc6-9174895d8b41"
except Exception as e:
    print(f"Error fetching recommendations: {e}")
    course_id = "1aac14b6-4bbd-4d01-bcc6-9174895d8b41"

# 3. GET curriculum
print("\n--- 3. Testing GET Curriculum ---")
req = urllib.request.Request(f"{BASE_URL}/api/v1/courses/{course_id}/curriculum", headers={"X-Employee-Id": emp_id})
with urllib.request.urlopen(req) as resp:
    curr = json.loads(resp.read().decode("utf-8"))
    print(f"Provider Label: {curr.get('provider_label')}")
    print(f"Learning Path Mode: {curr.get('learning_path_mode')}")
    mod1 = next(m for m in curr["modules"] if m["id"] == 1)
    for r in mod1["resources"]:
        print(f"Resource '{r['id']}': title='{r['title']}' type='{r['type']}' provider='{r.get('provider')}' ext_id='{r.get('external_resource_id')}' ext_url='{r.get('external_url')}'")

# 4. POST launch
print("\n--- 4. Testing POST Launch ---")
launch_req = urllib.request.Request(
    f"{BASE_URL}/api/v1/courses/{course_id}/resources/mod1-video-1/launch",
    data=b"{}",
    headers={"Content-Type": "application/json", "X-Employee-Id": emp_id},
    method="POST",
)
with urllib.request.urlopen(launch_req) as resp:
    launch_data = json.loads(resp.read().decode("utf-8"))
    print(f"Launch Response: {json.dumps(launch_data, indent=2)}")

# 5. POST sync single resource
print("\n--- 5. Testing POST Sync Single Resource ---")
sync_req = urllib.request.Request(
    f"{BASE_URL}/api/v1/courses/{course_id}/resources/mod1-video-1/sync",
    data=b"{}",
    headers={"Content-Type": "application/json", "X-Employee-Id": emp_id},
    method="POST",
)
with urllib.request.urlopen(sync_req) as resp:
    sync_data = json.loads(resp.read().decode("utf-8"))
    print(f"Resource Sync Response: {json.dumps(sync_data, indent=2)}")

# 6. POST sync all igot resources
print("\n--- 6. Testing POST Sync iGOT Course ---")
sync_course_req = urllib.request.Request(
    f"{BASE_URL}/api/v1/courses/{course_id}/providers/igot/sync",
    data=b"{}",
    headers={"Content-Type": "application/json", "X-Employee-Id": emp_id},
    method="POST",
)
with urllib.request.urlopen(sync_course_req) as resp:
    sync_course_data = json.loads(resp.read().decode("utf-8"))
    print(f"Course Sync Response: {json.dumps(sync_course_data, indent=2)}")

# 7. GET progress
print("\n--- 7. Testing GET Progress ---")
prog_req = urllib.request.Request(f"{BASE_URL}/api/v1/courses/{course_id}/progress", headers={"X-Employee-Id": emp_id})
with urllib.request.urlopen(prog_req) as resp:
    prog_data = json.loads(resp.read().decode("utf-8"))
    print(f"Course Progress Status: {prog_data['status']}, percentage: {prog_data['progress_percentage']}%")
    print(f"Completed modules: {prog_data['completed_modules']}, Unlocked modules: {prog_data['unlocked_modules']}")
    v1_prog = prog_data["resource_progress"].get("mod1-video-1")
    print(f"mod1-video-1 in progress: {json.dumps(v1_prog, indent=2)}")

print("\nSMOKE TEST COMPLETED SUCCESSFULLY!")
