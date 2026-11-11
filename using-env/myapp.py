import os
MySecret = os.environ.get("MySecret")
if not MySecret:
    raise SystemExit("MySecret environment variable is not set")
else:
    print(f"the value of MySecret is {MySecret}")