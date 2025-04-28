
 
from typing import Dict, Any
import os

# Configuration for GPT API
GPT_CONFIG: Dict[str, Any] = {
    "gpt_api_key": os.getenv("GPT_API_KEY", "")
}

# Configuration for Groq API
GROQ_CONFIG: Dict[str, Any] = {
    "groq_api_key": os.getenv("GROQ_API_KEY", "")
}


JIRA_API_TOKEN=""
JIRA_INSTANCE_URL=""
JIRA_CLOUD=True