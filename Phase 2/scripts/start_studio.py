"""One-click local server launcher for VARANASI Quantum Optimization Studio.

Usage:
    python scripts/start_studio.py [--port 5173]
"""
from __future__ import annotations
import argparse
import functools
import http.server
import os
import socketserver
import sys
import webbrowser

def main():
    parser = argparse.ArgumentParser(description="Start VARANASI Studio local server")
    parser.add_argument("--port", type=int, default=5173, help="Port to serve on (default: 5173)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Check if web/dist exists (production build), otherwise serve web/
    dist_dir = os.path.join(repo_root, "web", "dist")
    if os.path.exists(dist_dir) and os.path.exists(os.path.join(dist_dir, "index.html")):
        serve_dir = dist_dir
    else:
        serve_dir = os.path.join(repo_root, "web")

    os.chdir(serve_dir)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir)

    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            url = f"http://localhost:{args.port}"
            print("=" * 70)
            print("  VARANASI QUANTUM OPTIMIZATION STUDIO")
            print("  Qiskit Fall Fest 2026 — Problem Statement PS-O1")
            print("=" * 70)
            print(f"  Serving directory: {serve_dir}")
            print(f"  Studio URL:        {url}")
            print("  Press Ctrl+C to terminate.")
            print("=" * 70)

            if not args.no_browser:
                try:
                    webbrowser.open(url)
                except Exception as e:
                    print(f"  Note: Could not open browser automatically: {e}")

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStudio server stopped gracefully.")
        sys.exit(0)
    except OSError as e:
        print(f"Error starting server on port {args.port}: {e}")
        print("Try running on an alternative port, e.g.: python scripts/start_studio.py --port 8080")
        sys.exit(1)

if __name__ == "__main__":
    main()
