# Logging Control

## Problem

The backend was outputting very verbose logs showing detailed scene breakdowns, which cluttered the console.

## Solution

Added `QUIET_MODE` environment variable to control logging verbosity.

## Usage

### Enable Quiet Mode (Less Verbose)

Edit `.env` file:

```bash
# Reduce console output
QUIET_MODE=true
```

Then restart the backend:

```bash
cd backend
python main.py
```

**Output with QUIET_MODE=true:**
```
✓ Loaded environment variables
✓ Successfully imported TAMUS wrapper
INFO: Uvicorn running on http://0.0.0.0:2501
```

### Disable Quiet Mode (More Verbose)

Edit `.env` file:

```bash
# Show detailed logs
QUIET_MODE=false
```

**Output with QUIET_MODE=false:**
```
✓ Loaded environment variables
✓ Successfully imported TAMUS wrapper
INFO: Uvicorn running on http://0.0.0.0:2501

============================================================
Starting REAL AI generation: concept
Project: abc-123
============================================================

Generating concept with TAMUS GPT-5.2...
✓ Concept generated: 1234 characters
✓ Generation completed: concept
```

## Default Setting

By default, `QUIET_MODE=true` is set in `.env` to keep the console clean.

## When to Use Each Mode

### Use QUIET_MODE=true (Default)
- ✅ Production environment
- ✅ Normal usage
- ✅ When you don't need detailed logs
- ✅ Cleaner console output

### Use QUIET_MODE=false
- 🔍 Debugging issues
- 🔍 Development
- 🔍 Understanding what's happening
- 🔍 Troubleshooting API calls

## Other Logging Options

### Redirect Logs to File

```bash
cd backend
python main.py > logs/backend.log 2>&1
```

### View Only Errors

```bash
cd backend
python main.py 2>&1 | grep -i error
```

### Tail Logs in Real-Time

```bash
cd backend
python main.py > logs/backend.log 2>&1 &
tail -f logs/backend.log
```

## Current Status

✅ Backend stopped (verbose output stopped)
✅ QUIET_MODE=true added to .env
✅ Ready to restart with clean output

## Restart Backend

```bash
cd backend
python main.py
```

You should now see minimal, clean output instead of detailed scene breakdowns.
