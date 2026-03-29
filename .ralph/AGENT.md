# Agent Instructions — Build Supervisor

## Build Commands
```bash
# Check pipeline status
cd {PROJECT_DIR} && python3 .buildrunner/monitor.py

# View planning progress
cat {PROJECT_DIR}/.buildrunner/.planning-state | python3 -m json.tool

# View build progress
cat {PROJECT_DIR}/.buildrunner/.state

# View master state
cat {PROJECT_DIR}/.buildrunner/.autonomous-state | python3 -m json.tool

# View recent git commits
cd {PROJECT_DIR} && git log --oneline -10

# View live logs
tail -20 {PROJECT_DIR}/.buildrunner/logs/autonomous.log
tail -20 {PROJECT_DIR}/.buildrunner/logs/codex-live.log
tail -20 {PROJECT_DIR}/.buildrunner/logs/claude-live.log
```

## Test Commands
```bash
# Verify monitor script works
cd {PROJECT_DIR} && python3 .buildrunner/monitor.py; echo "Exit: $?"

# Verify process is alive
cat {PROJECT_DIR}/.buildrunner/.autonomous-pid && ps -p $(cat {PROJECT_DIR}/.buildrunner/.autonomous-pid) 2>/dev/null
```

## Recovery Commands
```bash
# Restart pipeline (preserves progress)
cd {PROJECT_DIR} && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid

# Kill stuck process
kill $(cat {PROJECT_DIR}/.buildrunner/.autonomous-pid) 2>/dev/null

# Force restart from specific phase
cd {PROJECT_DIR} && python3 .buildrunner/autonomous.py --build-only  # Skip planning
cd {PROJECT_DIR} && python3 .buildrunner/planner.py --resume         # Resume planning only
```
