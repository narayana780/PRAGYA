import urllib.request
import json

def verify_live():
    # 1. Health check
    req = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health")
    health = json.loads(req.read().decode())
    print("Health Status:", health["status"])

    # 2. Get current employee
    req = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/employees/me")
    me = json.loads(req.read().decode())
    emp_id = me["id"]
    print(f"Employee: {me['full_name']} ({me['employee_code']}), Role: {me['job_role_name']}")

    # 3. Recalculate skill gaps
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/api/v1/employees/{emp_id}/skill-gaps/recalculate",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    gaps = json.loads(resp.read().decode())
    print(f"Recalculated {len(gaps)} skill gaps for {me['full_name']}")

    # 4. Get summary
    req = urllib.request.urlopen(f"http://127.0.0.1:8000/api/v1/employees/{emp_id}/skill-gaps/summary")
    summary = json.loads(req.read().decode())
    print("\n--- SKILL GAP SUMMARY ---")
    print(f"Total Competencies: {summary['total_competencies']}")
    print(f"Active Gaps Count:  {summary['gaps_count']}")
    print(f"Critical Gaps:      {summary['critical_count']}")
    print(f"High Gaps:          {summary['high_count']}")
    print(f"Medium Gaps:        {summary['medium_count']}")
    print(f"Low Gaps:           {summary['low_count']}")
    print(f"No Gap Count:       {summary['no_gap_count']}")
    print(f"Average Deficit:    {summary['average_gap']} pts")
    if summary['highest_priority_gap']:
        top = summary['highest_priority_gap']
        print(f"Highest Priority Gap: {top['competency_name']} (Priority: {top['priority_level']}, Score: {top['priority_score']}, Gap: {top['gap_score']})")

    # 5. Print individual gaps
    print("\n--- INDIVIDUAL SKILL GAPS ---")
    print(f"{'Competency':<25} {'Domain':<20} {'Current':<8} {'Req':<8} {'Gap':<8} {'Priority':<12} {'Confidence':<12}")
    print("-" * 95)
    for g in gaps:
        print(f"{g['competency_name']:<25} {g['domain_name']:<20} {g['current_score']:<8.1f} {g['required_score']:<8.1f} {g['gap_score']:<8.1f} {g['priority_level']:<12} {g['confidence_flag']:<12}")

    # 6. Verify single gap detail with PriorityBreakdown
    sample_gap = gaps[0]
    req = urllib.request.urlopen(f"http://127.0.0.1:8000/api/v1/employees/{emp_id}/skill-gaps/{sample_gap['competency_id']}")
    detail = json.loads(req.read().decode())
    print("\n--- SAMPLE DETAIL BREAKDOWN ---")
    print(f"Competency: {detail['competency_name']}")
    print(f"Priority Score: {detail['priority_score']}")
    print("Breakdown Components:")
    for k, v in detail['priority_breakdown'].items():
        print(f"  - {k}: {v}")
    print(f"Explanation:\n  {detail['explanation']}")

if __name__ == "__main__":
    verify_live()
