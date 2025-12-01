#!/usr/bin/env python3
"""
Verify that the GitHub Issue Hunter setup is complete and working
"""
import os
import sys
from pathlib import Path


def check_mark(condition, message):
    """Print check mark or X based on condition"""
    symbol = "✅" if condition else "❌"
    print(f"{symbol} {message}")
    return condition


def verify_setup():
    """Verify all required components are in place"""
    
    print("=" * 70)
    print("GitHub Issue Hunter - Setup Verification")
    print("=" * 70)
    print()
    
    all_good = True
    
    # Check files
    print("📁 Checking required files...")
    required_files = [
        'agent.py',
        'github_client.py',
        'issue_analyzer.py',
        'config.yaml',
        'requirements.txt',
        'repos.txt'
    ]
    
    for file in required_files:
        exists = Path(file).exists()
        all_good &= check_mark(exists, f"{file}")
    print()
    
    # Check directories
    print("📂 Checking directories...")
    required_dirs = [
        'logs',
        '.github/workflows'
    ]
    
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        all_good &= check_mark(exists, f"{dir_path}/")
    print()
    
    # Check environment file
    print("🔐 Checking environment configuration...")
    env_exists = Path('.env').exists()
    if env_exists:
        check_mark(True, ".env file exists")
        
        # Check required variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['GITHUB_TOKEN', 'GITHUB_USERNAME']
        optional_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'AZURE_OPENAI_API_KEY']
        
        for var in required_vars:
            value = os.getenv(var)
            all_good &= check_mark(value is not None and value.strip() != '', f"{var} is set")
        
        # At least one AI provider
        has_ai = any(os.getenv(var) for var in optional_vars)
        all_good &= check_mark(has_ai, "AI provider API key (OpenAI, Azure, or Anthropic)")
    else:
        check_mark(False, ".env file (run setup.py to create)")
        all_good = False
    print()
    
    # Check repositories
    print("📚 Checking repositories list...")
    repos_file = Path('repos.txt')
    if repos_file.exists():
        with open(repos_file, 'r') as f:
            repos = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        has_repos = len(repos) > 0
        check_mark(has_repos, f"Found {len(repos)} repositories")
        if not has_repos:
            print("   ⚠️  Add repositories to repos.txt or run import_repos.py")
    else:
        check_mark(False, "repos.txt file")
        all_good = False
    print()
    
    # Check Python version
    print("🐍 Checking Python environment...")
    version_ok = sys.version_info >= (3, 9)
    check_mark(version_ok, f"Python {sys.version.split()[0]} (3.9+ required)")
    all_good &= version_ok
    print()
    
    # Check dependencies
    print("📦 Checking Python packages...")
    packages = {
        'github': 'PyGithub',
        'openai': 'openai',
        'yaml': 'pyyaml',
        'dotenv': 'python-dotenv'
    }
    
    for module, package in packages.items():
        try:
            __import__(module)
            check_mark(True, f"{package}")
        except ImportError:
            check_mark(False, f"{package} (run: pip install -r requirements.txt)")
            all_good = False
    print()
    
    # Summary
    print("=" * 70)
    if all_good:
        print("🎉 Setup verification PASSED!")
        print()
        print("You're ready to run the agent:")
        print("  python3 demo.py          # See a demo")
        print("  python3 agent.py --dry-run --max-issues 2  # Test run")
        print("  python3 agent.py         # Real run")
    else:
        print("⚠️  Setup verification FAILED")
        print()
        print("Please fix the issues above, then:")
        print("  Run: python3 setup.py    # For interactive setup")
        print("  Or: python3 verify.py    # To check again")
    print("=" * 70)
    
    return all_good


if __name__ == "__main__":
    try:
        success = verify_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
