# Databricks notebook source
# MAGIC %md
# MAGIC # Automated AI Analysis Workflow (After)
# MAGIC 
# MAGIC This notebook demonstrates the accelerated workflow using the AI Automation tool.

# COMMAND ----------

# Step 1: Import the AI Analyzer
# (In a real scenario, this would be a library installed on the cluster)
import sys
import os
sys.path.append("../src") # Adding src to path for demo purposes

from log_analyzer import LogAnalyzer

# COMMAND ----------

# Step 2: Initialize the AI Model
# Consultant just instantiates the tool
analyzer = LogAnalyzer()

# COMMAND ----------

# Step 3: Run Analysis on Log Data
log_data = {
  "cluster_id": "0923-123456-abcde789",
  "events": [
    {"time": "10:12:15", "level": "ERROR", "message": "Init script failure: /dbfs/databricks/init/setup_env.sh exited with non-zero status: 127. Command not found: pip3"}
  ]
}

import json
log_text = json.dumps(log_data)

# One line to get full analysis
report = analyzer.analyze_log(log_text)

# COMMAND ----------

# Step 4: Review Automated Findings
print(f"ROOT CAUSE: {report['root_cause']}")
print(f"REMEDIATION: {report['remediation']}")
print(f"INSIGHTS: {report['insights']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Value Delivered
# MAGIC * **Time Saved:** 30 minutes of manual debugging reduced to 30 seconds.
# MAGIC * **Standardization:** Consistent reporting format.
# MAGIC * **Knowledge:** Leveraging LLM knowledge base for immediate fix suggestions.
