# Simple in-memory store for task status
# Format: { "user_id": { "status": "processing", "step": "Architecting...", "progress": 20 } }
task_status = {}

def update_task(user_id, status, step, progress):
    task_status[str(user_id)] = {
        "status": status,
        "step": step,
        "progress": progress
    }

def get_task(user_id):
    return task_status.get(str(user_id), {"status": "idle", "progress": 0})
