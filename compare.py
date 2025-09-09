#!/usr/bin/env python3

import json
import click
from datetime import datetime
from typing import Dict, List, Set, NamedTuple, Optional


class BuildInfo(NamedTuple):
    definition_name: str
    build_number: str
    formatted_time: str
    queue_time_raw: str
    requested_by: str
    requested_for: str
    rollout_type: str
    select: str
    override_managed_validation_duration: str
    managed_validation_duration_in_hours: str


def extract_build_metadata(build: Dict) -> BuildInfo:
    """Extract and process metadata from a build object."""
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
#    if 'requestedBy' in build and 'displayName' in build['requestedBy']:
#        requested_by = f" by {build['requestedBy']['displayName']}"

    # Get requestedFor displayName if it exists
    requested_for = ""
    if 'requestedFor' in build and 'displayName' in build['requestedFor']:
        requested_for = f" for {build['requestedFor']['displayName']}"
    
    # Get definition name if it exists
    definition_name = build['definition']['name']

    # Get templateParameters info if it exists
    template_params = build.get('templateParameters', {})
    rollout_type = template_params.get('rolloutType', 'n/a')
    select = template_params.get('select', '*')
    override_managed_validation_duration = template_params.get('overrideManagedValidationDuration', 'n/a')
    managed_validation_duration_in_hours = template_params.get('managedValidationDurationInHours', 'n/a')
    
    return BuildInfo(
        definition_name=definition_name,
        build_number=build_number,
        formatted_time=formatted_time,
        queue_time_raw=queue_time,
        requested_by=requested_by,
        requested_for=requested_for,
        rollout_type=rollout_type,
        select=select,
        override_managed_validation_duration=override_managed_validation_duration,
        managed_validation_duration_in_hours=managed_validation_duration_in_hours
    )


def print_build_info(build_info: BuildInfo):
    """Print formatted build information."""
    print(f"'{build_info.definition_name}' at '{build_info.formatted_time}'\n   Build '{build_info.build_number}' queued{build_info.requested_by}{build_info.requested_for}")
    print(f"   Rollout Type: {build_info.rollout_type}, Select: {build_info.select}")
    
    if build_info.override_managed_validation_duration == 'True':
        print(f"   Validation Duration Override: {build_info.managed_validation_duration_in_hours}h")


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
    
    # Extract metadata from new builds
    build_infos = []
    for build in new_builds:
        build_info = extract_build_metadata(build)
        build_infos.append(build_info)
    
    # Sort builds by queue time ascending
    build_infos.sort(key=lambda x: x.queue_time_raw)
    
    # Print sorted builds
    if build_infos:
        for build_info in build_infos:
            print_build_info(build_info)

if __name__ == '__main__':
    compare_builds()
