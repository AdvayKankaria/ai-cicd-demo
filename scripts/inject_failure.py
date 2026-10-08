import os
import sys


def inject():
    scenario = os.getenv("FAILURE_SCENARIO")
    print(f"Injecting failure: {scenario}")
    # Write to a .env file or communicate with mock orchestrator
    print("Simulated injection complete.")
    return 0


if __name__ == "__main__":
    sys.exit(inject())
