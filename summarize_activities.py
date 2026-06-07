import os
import datetime
import json
import sys
from garmin_planner.client import Client
from garmin_planner.parser import parseYaml

def summarize_activities():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load secrets
    secrets_path = os.path.join(current_dir, "garmin_planner", "secrets.yaml")
    if not os.path.exists(secrets_path):
        # Try root if not in garmin_planner
        secrets_path = os.path.join(current_dir, "secrets.yaml")
        
    secrets = parseYaml(secrets_path)
    if not secrets:
        print("Failed to parse secrets.yaml")
        return
    
    email = secrets['email']
    password = secrets['password']
    
    # Initialize client
    client = Client(email, password)
    
    # Ask for days back
    try:
        days = int(input("How many days back do you want to summarize? "))
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return
        
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    
    print(f"Fetching activities from {start_date} to {end_date}...")
    activities = client.getActivities(start_date, end_date)
    
    summaries = []
    for act in activities:
        # Get details
        details = client._api.get_activity_details(act['activityId'])
        
        summary = {
            "name": act.get("activityName"),
            "date": act.get("startTimeLocal"),
            "total_distance": act.get("distance"),
            "average_pace": act.get("averageSpeed"), # This might need conversion
            "average_hr": act.get("averageHR"),
            "summaries": details.get("summaries", []) # Simplified
        }
        summaries.append(summary)
        
    # Save to JSON
    output_path = os.path.join(current_dir, "summaries", f"summary_{end_date.strftime('%Y%m%d')}.json")
    with open(output_path, 'w') as f:
        json.dump(summaries, f, indent=4)
        
    print(f"Summary saved to {output_path}")

if __name__ == "__main__":
    summarize_activities()
