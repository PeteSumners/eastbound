#!/bin/bash
# Monitor automation progress in real-time

echo "======================================================================"
echo "EASTBOUND AUTOMATION MONITOR"
echo "======================================================================"
date

# Check if automation is running
echo ""
echo "[PROCESS STATUS]"
if ps aux | grep -v grep | grep "run_daily_automation.py" > /dev/null; then
    echo "✓ Automation is RUNNING"
    PID=$(ps aux | grep -v grep | grep "run_daily_automation.py" | awk '{print $2}' | head -1)
    echo "  PID: $PID"
    echo "  Runtime: $(ps -p $PID -o etime= 2>/dev/null || echo 'N/A')"
else
    echo "✗ Automation is NOT running"
fi

# Check Python processes
echo ""
echo "[PYTHON PROCESSES]"
ps aux | grep python | grep -v grep | grep -v monitor | wc -l | xargs echo "  Active Python processes:"

# Check created files
DATE=$(date +%Y-%m-%d)
echo ""
echo "[FILES CREATED TODAY ($DATE)]"

if [ -f "research/${DATE}-briefing.json" ]; then
    SIZE=$(ls -lh "research/${DATE}-briefing.json" | awk '{print $5}')
    echo "  ✓ Briefing: research/${DATE}-briefing.json ($SIZE)"
else
    echo "  ⏳ Briefing: Not created yet"
fi

if [ -f "images/${DATE}-keywords.png" ]; then
    echo "  ✓ Visualizations: images/${DATE}-*.png"
else
    echo "  ⏳ Visualizations: Not created yet"
fi

if ls content/drafts/${DATE}-*.md 1> /dev/null 2>&1; then
    DRAFT=$(ls -t content/drafts/${DATE}-*.md 2>/dev/null | head -1)
    SIZE=$(wc -w "$DRAFT" 2>/dev/null | awk '{print $1}')
    echo "  ✓ Draft article: $DRAFT ($SIZE words)"
else
    echo "  ⏳ Draft article: Not created yet"
fi

if [ -f "images/${DATE}-generated.png" ]; then
    SIZE=$(ls -lh "images/${DATE}-generated.png" | awk '{print $5}')
    echo "  ✓ Hero image: images/${DATE}-generated.png ($SIZE)"
else
    echo "  ⏳ Hero image: Not generated yet (this takes 25-30 min)"
fi

if ls _posts/${DATE}-*.md 1> /dev/null 2>&1; then
    POST=$(ls -t _posts/${DATE}-*.md 2>/dev/null | head -1)
    echo "  ✓ Published: $POST"
else
    echo "  ⏳ Published: Not published yet"
fi

# Show log tail
echo ""
echo "[LATEST LOG OUTPUT (last 20 lines)]"
echo "----------------------------------------------------------------------"
if [ -f "automation_log.txt" ]; then
    tail -20 automation_log.txt
else
    echo "Log file not created yet..."
fi

echo ""
echo "======================================================================"
echo "To continuously monitor: watch -n 30 bash monitor_automation.sh"
echo "To view full log: tail -f automation_log.txt"
echo "======================================================================"
