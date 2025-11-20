# Databricks notebook source
# MAGIC %md
# MAGIC # Manual Log Analysis Workflow (Before AI)
# MAGIC 
# MAGIC This notebook demonstrates the typical manual workflow a consultant performs when diagnosing a cluster failure.

# COMMAND ----------

# Step 1: Load the log file manually
import json

log_path = "/dbfs/mnt/logs/cluster_runtime_log.json"
# In this demo, we simulate reading from a local path
log_data = {
  "cluster_id": "0923-123456-abcde789",
  "events": [
    {"time": "10:12:15", "level": "ERROR", "message": "Init script failure: /dbfs/databricks/init/setup_env.sh exited with non-zero status: 127. Command not found: pip3"}
  ]
}

print("Log loaded.")

# COMMAND ----------

# Step 2: Manually parse and search for errors
# Consultant has to scroll through thousands of lines or write regex
for event in log_data['events']:
    if event['level'] == 'ERROR':
        print(f"FOUND ERROR: {event['message']}")

# COMMAND ----------

# Step 3: Manual Research
# Consultant switches context to Google/StackOverflow
print("Searching internal wiki for 'exit status 127'...")
print("Searching for 'pip3 command not found in init script'...")

# COMMAND ----------

# Step 4: Write up findings manually
# MAGIC %md
# MAGIC ## Findings
# MAGIC * **Issue:** Cluster failed due to init script error.
# MAGIC * **Root Cause:** `pip3` command not found.
# MAGIC * **Fix:** The init script is likely running in a base environment where pip3 isn't on the path or is named `pip`.
# MAGIC * **Recommendation:** Update script to use `/databricks/python/bin/pip` or ensure environment is activated.
