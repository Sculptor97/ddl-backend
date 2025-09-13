#!/usr/bin/env python3
"""
Check API key configuration for Mapbox and ORS.
"""

import os
from pathlib import Path

def check_api_keys():
    """Check which API keys are configured."""
    
    print("🔑 API Key Configuration Check")
    print("=" * 40)
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        
        # Read .env file
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        # Check for Mapbox token
        mapbox_found = 'MAPBOX_ACCESS_TOKEN=' in env_content
        print(f"   Mapbox Token: {'✅ Found' if mapbox_found else '❌ Not found'}")
        
        # Check for ORS token
        ors_found = 'ORS_API_KEY=' in env_content
        print(f"   ORS Token: {'✅ Found' if ors_found else '❌ Not found'}")
        
        # Show token values (masked)
        for line in env_content.split('\n'):
            if line.startswith('MAPBOX_ACCESS_TOKEN='):
                token = line.split('=')[1]
                if token:
                    print(f"   Mapbox Token: {token[:10]}...")
                else:
                    print(f"   Mapbox Token: (empty)")
            elif line.startswith('ORS_API_KEY='):
                token = line.split('=')[1]
                if token:
                    print(f"   ORS Token: {token[:10]}...")
                else:
                    print(f"   ORS Token: (empty)")
    else:
        print("❌ .env file not found")
        print("   Create a .env file with your API keys")
    
    print()
    
    # Check environment variables
    print("🌍 Environment Variables:")
    mapbox_env = os.getenv('MAPBOX_ACCESS_TOKEN')
    ors_env = os.getenv('ORS_API_KEY')
    
    print(f"   MAPBOX_ACCESS_TOKEN: {'✅ Set' if mapbox_env else '❌ Not set'}")
    print(f"   ORS_API_KEY: {'✅ Set' if ors_env else '❌ Not set'}")
    
    if mapbox_env:
        print(f"   Mapbox Token: {mapbox_env[:10]}...")
    if ors_env:
        print(f"   ORS Token: {ors_env[:10]}...")

if __name__ == "__main__":
    check_api_keys()


