#!/usr/bin/env python3
"""
Quick script to check if .env file is loading correctly
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env file
env_path = Path(__file__).parent / '.env'
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    # Load it
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"\n✅ Loaded .env file")
    
    # Check for OPENAI_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OPENAI_API_KEY found (length: {len(openai_key)})")
        print(f"   First 10 chars: {openai_key[:10]}...")
    else:
        print(f"❌ OPENAI_API_KEY not found in environment")
        
        # Read file directly
        print(f"\nReading .env file directly:")
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if 'OPENAI' in line.upper():
                    print(f"  Line {i}: {line}")
                    if '=' in line:
                        key, value = line.split('=', 1)
                        print(f"    Key: '{key.strip()}'")
                        print(f"    Value length: {len(value.strip())}")
                        print(f"    Value has quotes: {value.strip().startswith('\"') or value.strip().startswith(\"'\")}")
    
    # Show all env vars with OPENAI
    print(f"\nAll environment variables with 'OPENAI':")
    openai_vars = {k: v for k, v in os.environ.items() if 'OPENAI' in k.upper()}
    if openai_vars:
        for k, v in openai_vars.items():
            print(f"  {k} = {v[:20]}... (length: {len(v)})")
    else:
        print("  None found")
else:
    print(f"❌ .env file not found at: {env_path}")

