import os
from typing import Any
from datetime import date, timedelta
import httpx
from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

# Initialize GitHub OAuth provider
github_client_id = os.environ.get("GITHUB_CLIENT_ID")
github_client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
base_url = os.environ.get("BASE_URL")

# Configure authentication if GitHub credentials are provided
auth = None
if github_client_id and github_client_secret and base_url:
    auth = GitHubProvider(
        client_id=github_client_id,
        client_secret=github_client_secret,
        base_url=base_url,
        required_scopes=["user"]
    )

# Initialize FastMCP server with optional authentication
mcp = FastMCP("Oura", auth=auth)

# Configuration
OURA_API_BASE = "https://api.ouraring.com/v2/usercollection"
OURA_API_TOKEN = os.environ.get("OURA_API_TOKEN", "")

async def make_oura_request(endpoint: str, params: dict = None) -> dict[str, Any] | None:
    """Make a request to the Oura API with proper error handling."""
    if not OURA_API_TOKEN:
        return {"error": "OURA_API_TOKEN not configured"}
    
    headers = {
        "Authorization": f"Bearer {OURA_API_TOKEN}",
    }
    url = f"{OURA_API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

def format_date(days_ago: int = 0) -> str:
    """Format a date for the Oura API (YYYY-MM-DD)."""
    target_date = date.today() - timedelta(days=days_ago)
    return target_date.strftime("%Y-%m-%d")

@mcp.tool()
async def get_daily_activity(start_date: str = None, end_date: str = None) -> str:
    """Get daily activity data from Oura.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
    """
    if not start_date:
        start_date = format_date(7)
    if not end_date:
        end_date = format_date(0)
    
    params = {"start_date": start_date, "end_date": end_date}
    data = await make_oura_request("daily_activity", params)
    
    if not data or "error" in data:
        return f"Unable to fetch activity data: {data.get('error', 'Unknown error')}"
    
    if "data" not in data or not data["data"]:
        return "No activity data found for the specified date range."
    
    activities = []
    for item in data["data"]:
        activity = f"""
Date: {item.get('day', 'Unknown')}
Activity Score: {item.get('score', 'N/A')}
Active Calories: {item.get('active_calories', 'N/A')} kcal
Total Calories: {item.get('total_calories', 'N/A')} kcal
Steps: {item.get('steps', 'N/A')}
Equivalent Walking Distance: {item.get('equivalent_walking_distance', 'N/A')} meters
High Activity Time: {item.get('high_activity_time', 'N/A')} seconds
Medium Activity Time: {item.get('medium_activity_time', 'N/A')} seconds
Low Activity Time: {item.get('low_activity_time', 'N/A')} seconds
Sedentary Time: {item.get('sedentary_time', 'N/A')} seconds
    """
        activities.append(activity.strip())
    
    return "\n\n---\n\n".join(activities)

@mcp.tool()
async def get_daily_sleep(start_date: str = None, end_date: str = None) -> str:
    """Get daily sleep data from Oura.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
    """
    if not start_date:
        start_date = format_date(7)
    if not end_date:
        end_date = format_date(0)
    
    params = {"start_date": start_date, "end_date": end_date}
    data = await make_oura_request("daily_sleep", params)
    
    if not data or "error" in data:
        return f"Unable to fetch sleep data: {data.get('error', 'Unknown error')}"
    
    if "data" not in data or not data["data"]:
        return "No sleep data found for the specified date range."
    
    sleep_records = []
    for item in data["data"]:
        sleep_record = f"""
Date: {item.get('day', 'Unknown')}
Sleep Score: {item.get('score', 'N/A')}
Total Sleep Duration: {item.get('total_sleep_duration', 'N/A')} seconds
REM Sleep Duration: {item.get('rem_sleep_duration', 'N/A')} seconds
Deep Sleep Duration: {item.get('deep_sleep_duration', 'N/A')} seconds
Light Sleep Duration: {item.get('light_sleep_duration', 'N/A')} seconds
Awake Time: {item.get('awake_time', 'N/A')} seconds
Sleep Efficiency: {item.get('efficiency', 'N/A')}%
Restlessness: {item.get('restless_periods', 'N/A')}
Average Heart Rate: {item.get('average_heart_rate', 'N/A')} bpm
Lowest Heart Rate: {item.get('lowest_heart_rate', 'N/A')} bpm
    """
        sleep_records.append(sleep_record.strip())
    
    return "\n\n---\n\n".join(sleep_records)

@mcp.tool()
async def get_daily_readiness(start_date: str = None, end_date: str = None) -> str:
    """Get daily readiness data from Oura.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
    """
    if not start_date:
        start_date = format_date(7)
    if not end_date:
        end_date = format_date(0)
    
    params = {"start_date": start_date, "end_date": end_date}
    data = await make_oura_request("daily_readiness", params)
    
    if not data or "error" in data:
        return f"Unable to fetch readiness data: {data.get('error', 'Unknown error')}"
    
    if "data" not in data or not data["data"]:
        return "No readiness data found for the specified date range."
    
    readiness_records = []
    for item in data["data"]:
        readiness = f"""
Date: {item.get('day', 'Unknown')}
Readiness Score: {item.get('score', 'N/A')}
Temperature Deviation: {item.get('temperature_deviation', 'N/A')}°C
Temperature Trend Deviation: {item.get('temperature_trend_deviation', 'N/A')}°C
Activity Balance: {item.get('contributors', {}).get('activity_balance', 'N/A')}
Body Temperature: {item.get('contributors', {}).get('body_temperature', 'N/A')}
HRV Balance: {item.get('contributors', {}).get('hrv_balance', 'N/A')}
Previous Day Activity: {item.get('contributors', {}).get('previous_day_activity', 'N/A')}
Previous Night: {item.get('contributors', {}).get('previous_night', 'N/A')}
Recovery Index: {item.get('contributors', {}).get('recovery_index', 'N/A')}
Resting Heart Rate: {item.get('contributors', {}).get('resting_heart_rate', 'N/A')}
Sleep Balance: {item.get('contributors', {}).get('sleep_balance', 'N/A')}
    """
        readiness_records.append(readiness.strip())
    
    return "\n\n---\n\n".join(readiness_records)

@mcp.tool()
async def get_heart_rate(start_datetime: str = None, end_datetime: str = None) -> str:
    """Get heart rate data from Oura.
    
    Args:
        start_datetime: Start datetime in ISO 8601 format (defaults to 24 hours ago)
        end_datetime: End datetime in ISO 8601 format (defaults to now)
    """
    params = {}
    if start_datetime:
        params["start_datetime"] = start_datetime
    if end_datetime:
        params["end_datetime"] = end_datetime
    
    data = await make_oura_request("heartrate", params)
    
    if not data or "error" in data:
        return f"Unable to fetch heart rate data: {data.get('error', 'Unknown error')}"
    
    if "data" not in data or not data["data"]:
        return "No heart rate data found for the specified time range."
    
    # Limit to first 100 entries to avoid too much data
    hr_data = data["data"][:100]
    hr_records = []
    
    for item in hr_data:
        hr_record = f"Time: {item.get('timestamp', 'Unknown')}, BPM: {item.get('bpm', 'N/A')}, Source: {item.get('source', 'N/A')}"
        hr_records.append(hr_record)
    
    result = "\n".join(hr_records)
    if len(data["data"]) > 100:
        result += f"\n\n(Showing first 100 of {len(data['data'])} records)"
    
    return result

@mcp.tool()
async def get_personal_info() -> str:
    """Get personal information from Oura."""
    data = await make_oura_request("personal_info")
    
    if not data or "error" in data:
        return f"Unable to fetch personal info: {data.get('error', 'Unknown error')}"
    
    info = f"""
Age: {data.get('age', 'N/A')}
Weight: {data.get('weight', 'N/A')} kg
Height: {data.get('height', 'N/A')} cm
Biological Sex: {data.get('biological_sex', 'N/A')}
Email: {data.get('email', 'N/A')}
    """
    
    return info.strip()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
