import traceback
try:
    from agent import run_agent
    print(run_agent('hello'))
except Exception as e:
    traceback.print_exc()
