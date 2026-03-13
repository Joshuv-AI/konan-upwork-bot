"""
Upwork API Integration
=====================
Job search and proposal submission using Upwork API.

Authentication: OAuth 1.0
Docs: https://developers.upwork.com/
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from requests_oauthlib import OAuth1
    import requests
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call(["pip", "install", "requests", "requests-oauthlib"])
    from requests_oauthlib import OAuth1
    import requests

# Load credentials
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials" / "upwork-api.env"

def load_credentials():
    """Load Upwork API credentials from env file."""
    creds = {}
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    creds[key] = val
    return creds.get('UPWORK_API_KEY'), creds.get('UPWORK_SECRET_KEY')

API_KEY, API_SECRET = load_credentials()

# Upwork API endpoints
BASE_URL = "https://api.upwork.com/graphql"
GQL_JOB_SEARCH = """
query GetJobPosts($params: SearchParamsInput!) {
  jobPostsSearch(params: $params) {
    edges {
      node {
        id
        title
        description
        budget {
          maximum
          minimum
          hourlyRate {
            hourlyFrom
            hourlyTo
          }
        }
        duration
        workload
        skills {
          name
        }
        client {
          name
          rating
          totalSpent
          reviewsCount
        }
        createdAt
        subcategory {
          name
        }
        category {
          name
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

def create_oauth_auth():
    """Create OAuth 1.0 authentication object."""
    if not API_KEY or not API_SECRET:
        raise ValueError("Missing API credentials")
    return OAuth1(API_KEY, client_secret=API_SECRET)

def search_jobs(
    query="",
    categories=None,
    min_hourly_rate=20,
    max_results=20,
    experience_level=None,
    job_type="hourly"
):
    """
    Search Upwork jobs.
    
    Args:
        query: Search keywords
        categories: List of category names to filter
        min_hourly_rate: Minimum hourly rate
        max_results: Maximum number of results
        experience_level: "entry", "intermediate", "expert"
        job_type: "hourly" or "fixed"
    
    Returns:
        List of job postings
    """
    auth = create_oauth_auth()
    
    # Build query variables
    variables = {
        "q": query,
        "limit": min(max_results, 50),
        "sort": "recency",
        "paging": {"offset": 0, "count": max_results}
    }
    
    # Add filters
    filters = {}
    if min_hourly_rate:
        filters["minHourlyRate"] = min_hourly_rate
    if experience_level:
        filters["experienceLevels"] = [experience_level.upper()]
    if job_type:
        filters["contractType"] = [job_type.upper()]
    
    if filters:
        variables["filters"] = filters
    
    payload = {
        "query": GQL_JOB_SEARCH,
        "variables": json.dumps(variables)
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(BASE_URL, auth=auth, json={"query": GQL_JOB_SEARCH, "variables": variables}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL Errors: {data['errors']}")
                return []
            edges = data.get('data', {}).get('jobPostsSearch', {}).get('edges', [])
            jobs = []
            for edge in edges:
                job = edge.get('node', {})
                jobs.append({
                    'id': job.get('id'),
                    'title': job.get('title'),
                    'description': job.get('description', '')[:500],
                    'budget': job.get('budget', {}),
                    'duration': job.get('duration'),
                    'workload': job.get('workload'),
                    'skills': [s.get('name') for s in job.get('skills', [])],
                    'client': job.get('client', {}),
                    'created_at': job.get('createdAt'),
                    'category': job.get('category', {}).get('name'),
                    'subcategory': job.get('subcategory', {}).get('name'),
                })
            return jobs
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Request failed: {e}")
        return []

def format_job_for_demo(job):
    """Format job for demo proposal."""
    budget = job.get('budget', {})
    hourly = budget.get('hourlyRate', {})
    client = job.get('client', {})
    
    rate = ""
    if hourly.get('hourlyFrom'):
        rate = f"${hourly.get('hourlyFrom')}-${hourly.get('hourlyTo')}/hr"
    elif budget.get('maximum'):
        rate = f"${budget.get('minimum')}-${budget.get('maximum')}"
    
    return f"""
## {job.get('title', 'Untitled')}

**ID:** {job.get('id')}
**Rate:** {rate}
**Duration:** {job.get('duration', 'N/A')}
**Workload:** {job.get('workload', 'N/A')}
**Category:** {job.get('category', 'N/A')}
**Posted:** {job.get('created_at', 'N/A')}

**Client:** {client.get('name', 'Unknown')}
- Rating: {client.get('rating', 'N/A')} stars
- Total Spent: ${client.get('totalSpent', 0):,}
- Reviews: {client.get('reviewsCount', 0)}

**Skills:** {', '.join(job.get('skills', [])[:10])}

**Description:**
{job.get('description', 'No description')[:800]}
"""

def test_connection():
    """Test API connection."""
    print("Testing Upwork API connection...")
    print(f"API Key loaded: {bool(API_KEY)}")
    print(f"API Secret loaded: {bool(API_SECRET)}")
    
    if not API_KEY or not API_SECRET:
        print("[X] Missing credentials!")
        return False
    
    # Try a simple query
    jobs = search_jobs(query="data entry", max_results=5)
    
    if jobs:
        print(f"[OK] Connection successful! Found {len(jobs)} jobs")
        return True
    else:
        print("[X] No jobs found (or API error)")
        return False

if __name__ == "__main__":
    test_connection()
