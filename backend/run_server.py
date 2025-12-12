#!/usr/bin/env python3
"""
Simple script to run the Tutorly backend server.

Usage:
    python run_server.py              # Development mode
    python run_server.py --prod       # Production mode
    python run_server.py --port 8080  # Custom port
"""

import os
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description='Run Tutorly Backend Server')
    parser.add_argument('--prod', action='store_true', help='Run in production mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port (default: 8000)')

    args = parser.parse_args()

    # Set environment
    os.environ['APP_ENV'] = 'production' if args.prod else 'development'

    # Build command
    cmd = [
        'uvicorn',
        'app.main:app',
        '--host', args.host,
        '--port', str(args.port),
    ]

    # Add reload for development
    if not args.prod:
        cmd.append('--reload')

    print(f"Starting server at http://{args.host}:{args.port}")
    print(f"API Docs: http://{args.host}:{args.port}/api/docs\n")

    # Run server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == '__main__':
    main()
