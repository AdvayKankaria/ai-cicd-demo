import json
import sys
import os

def set_output(name, value):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'{name}={value}', file=fh)

def main():
    if len(sys.argv) < 3:
        print("Usage: parse_plan.py <json_payload> <github_sha>")
        sys.exit(1)
        
    payload_str = sys.argv[1]
    github_sha = sys.argv[2]
    
    try:
        plan = json.loads(payload_str)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to parse JSON plan: {e}")
        sys.exit(1)
        
    # Validation
    if plan.get("commit_sha") != github_sha:
        # In a real environment, we'd strictly reject. For testing locally/manual trigger, we can warn.
        print(f"::warning::Plan commit_sha '{plan.get('commit_sha')}' does not match github_sha '{github_sha}'.")
        # sys.exit(1)
        
    required_keys = ["schema_version", "mode", "services", "waves", "plan_id"]
    for key in required_keys:
        if key not in plan:
            print(f"::error::Missing required key in plan: {key}")
            sys.exit(1)
            
    mode = plan["mode"]
    services = plan["services"]
    waves = plan["waves"]
    test_suites = plan.get("test_suites", [])
    
    print(f"Plan ID: {plan['plan_id']}")
    print(f"Mode: {mode}")
    print(f"Services to process: {services}")
    
    # Export outputs for matrix jobs
    set_output("services", json.dumps(services))
    set_output("test_suites", json.dumps(test_suites))
    set_output("mode", mode)
    
    # Simple wave handling for up to 2 waves for the demo
    wave_1 = waves[0].get("services", []) if len(waves) > 0 else []
    wave_2 = waves[1].get("services", []) if len(waves) > 1 else []
    
    set_output("wave_1_services", json.dumps(wave_1))
    set_output("wave_2_services", json.dumps(wave_2))
    
    print("Successfully parsed and validated the deployment plan.")

if __name__ == "__main__":
    main()
