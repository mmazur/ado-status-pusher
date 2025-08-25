#!/usr/bin/env python3

import json
import click
from datetime import datetime
from typing import Dict, List, Set


@click.command()
@click.argument('prev', type=click.Path(exists=True))
@click.argument('latest', type=click.Path(exists=True))
def compare_builds(prev: str, latest: str):
    """Compare two Azure DevOps build JSON files and report new builds."""
    
    # Load JSON files
    with open(prev, 'r') as f:
        prev_builds = json.load(f)
    
    with open(latest, 'r') as f:
        latest_builds = json.load(f)
    
    # Extract build IDs from previous file
    prev_build_ids = set()
    if isinstance(prev_builds, dict) and 'value' in prev_builds:
        prev_build_ids = {build['id'] for build in prev_builds['value']}
    elif isinstance(prev_builds, list):
        prev_build_ids = {build['id'] for build in prev_builds}
    
    # Find new builds in latest file
    new_builds = []
    if isinstance(latest_builds, dict) and 'value' in latest_builds:
        builds_list = latest_builds['value']
    elif isinstance(latest_builds, list):
        builds_list = latest_builds
    else:
        builds_list = []
    
    for build in builds_list:
        if build['id'] not in prev_build_ids:
            new_builds.append(build)
    
    # Output new builds
    if new_builds:
        for build in new_builds:
            build_number = build.get('buildNumber', 'N/A')
            queue_time = build.get('queueTime', '')
            
            # Parse and format queue time
            if queue_time:
                try:
                    # Azure DevOps typically returns ISO format with Z suffix
                    dt = datetime.fromisoformat(queue_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M UTC')
                except (ValueError, TypeError):
                    formatted_time = queue_time
            else:
                formatted_time = 'N/A'
            
            # Get requestedBy displayName if it exists
            requested_by = ""
            if 'requestedBy' in build and 'displayName' in build['requestedBy']:
                requested_by = f" by {build['requestedBy']['displayName']}"

            # Get requestedFor displayName if it exists
            requested_for = ""
            if 'requestedFor' in build and 'displayName' in build['requestedFor']:
                requested_for = f" for {build['requestedFor']['displayName']}"

            print(f"Build '{build_number}' queued at '{formatted_time}'{requested_by}{requested_for}")

if __name__ == '__main__':
    compare_builds()
