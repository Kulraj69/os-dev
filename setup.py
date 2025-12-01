#!/usr/bin/env python3
"""
Setup script for GitHub Issue Hunter
Helps configure the agent for first-time setup
"""
import os
import sys
from pathlib import Path


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          GitHub Issue Hunter Setup                           ║
║          AI-Powered Open Source Contribution Agent            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")


def create_env_file():
    """Guide user through creating .env file"""
    env_path = Path('.env')
    
    if env_path.exists():
        response = input("\n.env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return
    
    print("\n" + "="*60)
    print("Setting up environment variables")
    print("="*60)
    
    print("\n📝 You'll need:")
    print("   1. GitHub Personal Access Token (with 'repo' scope)")
    print("      Create one at: https://github.com/settings/tokens")
    print("   2. OpenAI API Key (or Anthropic API Key)")
    print("      Get one at: https://platform.openai.com/api-keys")
    
    github_token = input("\nEnter your GitHub Personal Access Token: ").strip()
    if not github_token:
        print("❌ GitHub token is required")
        sys.exit(1)
    
    github_username = input("Enter your GitHub username: ").strip()
    github_email = input("Enter your GitHub email: ").strip()
    
    print("\nChoose AI provider:")
    print("  1. OpenAI (GPT-4)")
    print("  2. Anthropic (Claude)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        api_key = input("Enter your OpenAI API Key: ").strip()
        model = "gpt-4-turbo-preview"
        provider = "OPENAI"
    elif choice == '2':
        api_key = input("Enter your Anthropic API Key: ").strip()
        model = "claude-3-sonnet-20240229"
        provider = "ANTHROPIC"
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    # Create .env file
    env_content = f"""# GitHub Configuration
GITHUB_TOKEN={github_token}
GITHUB_USERNAME={github_username}
GITHUB_EMAIL={github_email}

# AI Configuration
{provider}_API_KEY={api_key}
LLM_MODEL={model}

# Agent Configuration
MAX_ISSUES_PER_RUN=10
DRY_RUN=false
VERBOSE=true
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully")


def add_repositories():
    """Guide user through adding repositories"""
    repos_path = Path('repos.txt')
    
    print("\n" + "="*60)
    print("Adding repositories to monitor")
    print("="*60)
    
    if repos_path.exists():
        with open(repos_path, 'r') as f:
            existing = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if existing:
            print(f"\nFound {len(existing)} existing repositories:")
            for repo in existing[:5]:
                print(f"  - {repo}")
            if len(existing) > 5:
                print(f"  ... and {len(existing) - 5} more")
    
    response = input("\nDo you want to add more repositories now? (y/N): ")
    if response.lower() == 'y':
        print("\nEnter repository URLs (one per line, empty line to finish):")
        print("Example: https://github.com/facebook/react")
        
        new_repos = []
        while True:
            repo = input("Repository URL: ").strip()
            if not repo:
                break
            if 'github.com/' in repo:
                new_repos.append(repo)
            else:
                print("❌ Invalid GitHub URL")
        
        if new_repos:
            with open(repos_path, 'a') as f:
                f.write('\n')
                for repo in new_repos:
                    f.write(f"{repo}\n")
            print(f"\n✅ Added {len(new_repos)} repositories")
    
    # Show instructions
    print("\n💡 Tip: You can manually edit repos.txt to add/remove repositories")
    print("   Or import from your Google Sheets by copying URLs into this file")


def install_dependencies():
    """Install Python dependencies"""
    print("\n" + "="*60)
    print("Installing dependencies")
    print("="*60)
    
    response = input("\nInstall dependencies now? (Y/n): ")
    if response.lower() != 'n':
        print("\nInstalling packages...")
        os.system("pip install -r requirements.txt")
        print("\n✅ Dependencies installed")
    else:
        print("\n⚠️  Remember to run: pip install -r requirements.txt")


def test_configuration():
    """Test if configuration is working"""
    print("\n" + "="*60)
    print("Testing configuration")
    print("="*60)
    
    response = input("\nRun a test (dry-run mode)? (Y/n): ")
    if response.lower() != 'n':
        print("\nRunning test...")
        os.system("python agent.py --dry-run --max-issues 1")
    else:
        print("\n⚠️  You can test with: python agent.py --dry-run")


def show_next_steps():
    """Show what to do next"""
    next_steps = """
╔══════════════════════════════════════════════════════════════╗
║                      Setup Complete! 🎉                       ║
╚══════════════════════════════════════════════════════════════╝

Next steps:

1. Test the agent:
   python agent.py --dry-run --max-issues 2

2. Run the agent:
   python agent.py

3. Set up GitHub Actions for automated runs:
   - Push this repository to GitHub
   - Add secrets in repository settings:
     * GH_PAT (your GitHub token)
     * OPENAI_API_KEY (or ANTHROPIC_API_KEY)
   - The agent will run automatically twice daily

4. Monitor activity:
   - Check logs/ directory for activity logs
   - View logs in GitHub Actions runs

5. Customize:
   - Edit config.yaml to adjust behavior
   - Modify comment_template in config.yaml
   - Add more repositories to repos.txt

📚 Documentation: See README.md for more details

Happy contributing! 🚀
    """
    print(next_steps)


def main():
    print_banner()
    
    try:
        check_python_version()
        create_env_file()
        add_repositories()
        install_dependencies()
        test_configuration()
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
