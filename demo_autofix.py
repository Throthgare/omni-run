#!/usr/bin/env python3
"""
Demo script for OmniRun autofix workflow.

This script creates a sample project with missing dependencies and demonstrates
the autofix capabilities of OmniRun.

Usage:
    python demo_autofix.py

This will:
1. Create a temporary demo project with missing dependencies
2. Run OmniRun in auto-fix mode
3. Show the complete workflow
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def create_demo_project():
    """Create a demo project with missing dependencies."""
    # Create temp directory
    demo_dir = Path(tempfile.mkdtemp(prefix="omnirun_demo_"))
    print(f"Creating demo project in: {demo_dir}")

    # Create a Python Flask app with missing dependencies
    app_py = demo_dir / "app.py"
    app_py.write_text("""from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from OmniRun Demo!"

if __name__ == '__main__':
    app.run(debug=True)
""")

    # Create requirements.txt (but don't install dependencies)
    requirements = demo_dir / "requirements.txt"
    requirements.write_text("""flask==2.3.3
requests==2.31.0
""")

    # Create a Node.js app
    package_json = demo_dir / "package.json"
    package_json.write_text("""{
  "name": "omnirun-demo",
  "version": "1.0.0",
  "description": "Demo app for OmniRun",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21"
  }
}""")

    server_js = demo_dir / "server.js"
    server_js.write_text("""const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello from OmniRun Node.js Demo!');
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
""")

    return demo_dir

def run_demo():
    """Run the OmniRun demo."""
    print("🚀 OmniRun Auto-Fix Demo")
    print("=" * 50)

    # Create demo project
    demo_dir = create_demo_project()

    try:
        # Change to demo directory
        original_dir = os.getcwd()
        os.chdir(demo_dir)

        print(f"\n📁 Demo project created at: {demo_dir}")
        print("📋 Project contains:")
        print("   - Python Flask app (app.py + requirements.txt)")
        print("   - Node.js Express app (server.js + package.json)")
        print("   - Missing dependencies (not installed)")

        print("\n🔧 Running OmniRun in auto-fix mode...")
        print("   (This will detect missing dependencies and offer to install them)")
        # Import and run OmniRun
        sys.path.insert(0, original_dir)
        from omni_run import OmniRun

        # Create OmniRun instance with auto-fix enabled
        runner = OmniRun(".", verbose=True, config_file=None)

        # Override config to enable auto-fix
        runner.config = {
            'auto_fix': True,
            'confirm_each_command': False,  # Auto-confirm for demo
            'timeout': 300,
            'max_depth': 3
        }

        # Scan for programs
        print("\n🔍 Scanning for executable programs...")
        runner.scan_for_executables()

        if not runner.discovered_programs:
            print("❌ No programs found!")
            return

        print(f"✅ Found {len(runner.discovered_programs)} programs:")
        for i, prog in enumerate(runner.discovered_programs, 1):
            status = "[OK] Ready" if not any(d.required and not d.available for d in prog.dependencies) else "[FIX] Needs fixing"
            print(f"   {i}. {prog.name} ({prog.type}) - {status}")

        # Show dependency issues
        print("\n📊 Dependency Analysis:")
        for prog in runner.discovered_programs:
            missing = [d for d in prog.dependencies if d.required and not d.available]
            if missing:
                print(f"   {prog.name}: {len(missing)} missing dependencies")
                for dep in missing:
                    print(f"     - {dep.name}: {dep.message}")
            else:
                print(f"   {prog.name}: All dependencies available")

        # Attempt auto-fix
        print("\n🔧 Starting auto-fix process...")
        fixed_any = False
        for prog in runner.discovered_programs:
            missing_deps = [d for d in prog.dependencies if d.required and not d.available]
            if missing_deps:
                print(f"   Fixing dependencies for {prog.name}...")
                success = runner.auto_fix_dependencies(prog, interactive=False)
                if success:
                    fixed_any = True
                    print(f"   ✅ Successfully fixed dependencies for {prog.name}")
                else:
                    print(f"   ❌ Failed to fix some dependencies for {prog.name}")

        # Final status
        print("\n📈 Final Status:")
        runner.scan_for_executables()  # Re-scan after fixes
        ready_count = sum(1 for prog in runner.discovered_programs
                         if not any(d.required and not d.available for d in prog.dependencies))
        total_count = len(runner.discovered_programs)

        print(f"   Programs ready to run: {ready_count}/{total_count}")

        if ready_count == total_count:
            print("   🎉 All programs are now ready to execute!")
        else:
            print("   ⚠️  Some programs still have issues")

        # Generate report
        report_file = demo_dir / "demo_report.html"
        runner.generate_html_report(str(report_file))
        print(f"   📄 HTML report generated: {report_file}")

    finally:
        # Cleanup
        os.chdir(original_dir)
        print(f"\n🧹 Demo complete. Temporary files in: {demo_dir}")
        print("   (Delete this directory when done viewing the results)")

if __name__ == "__main__":
    run_demo()