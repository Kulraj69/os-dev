#!/usr/bin/env python3
"""
Google Sheets Repository Importer
Helps import repository URLs from Google Sheets into repos.txt
"""
import sys
import re
from pathlib import Path


def extract_github_urls(text: str) -> list:
    """Extract GitHub repository URLs from text"""
    # Pattern to match GitHub repository URLs
    pattern = r'https?://github\.com/[\w-]+/[\w.-]+'
    urls = re.findall(pattern, text)
    
    # Clean and deduplicate
    cleaned_urls = []
    seen = set()
    
    for url in urls:
        # Remove trailing slashes and .git
        url = url.rstrip('/').rstrip('.git')
        
        # Skip if already seen
        if url in seen:
            continue
        
        seen.add(url)
        cleaned_urls.append(url)
    
    return cleaned_urls


def import_from_clipboard():
    """Import repositories from clipboard"""
    try:
        import pyperclip
        text = pyperclip.paste()
        return extract_github_urls(text)
    except ImportError:
        print("⚠️  pyperclip not installed. Install with: pip install pyperclip")
        return []
    except Exception as e:
        print(f"❌ Error reading clipboard: {e}")
        return []


def import_from_file(file_path: str):
    """Import repositories from a file"""
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        return extract_github_urls(text)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []


def import_from_text():
    """Import repositories from pasted text"""
    print("\nPaste your text (contains GitHub URLs), then press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows):")
    print("-" * 60)
    
    try:
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        
        text = '\n'.join(lines)
        return extract_github_urls(text)
    except KeyboardInterrupt:
        print("\n\nImport cancelled")
        return []


def save_repositories(repos: list, append: bool = True):
    """Save repositories to repos.txt"""
    repos_path = Path('repos.txt')
    
    # Load existing repos if appending
    existing = set()
    if append and repos_path.exists():
        with open(repos_path, 'r') as f:
            existing = {
                line.strip() 
                for line in f 
                if line.strip() and not line.strip().startswith('#')
            }
    
    # Filter out duplicates
    new_repos = [repo for repo in repos if repo not in existing]
    
    if not new_repos:
        print("\n⚠️  No new repositories to add (all already exist)")
        return
    
    # Write to file
    mode = 'a' if append else 'w'
    with open(repos_path, mode) as f:
        if append and repos_path.stat().st_size > 0:
            f.write('\n')
        
        for repo in new_repos:
            f.write(f"{repo}\n")
    
    print(f"\n✅ Added {len(new_repos)} new repositories to repos.txt")
    print(f"   Total repositories: {len(existing) + len(new_repos)}")


def main():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║           Google Sheets Repository Importer                  ║
╚══════════════════════════════════════════════════════════════╝

This tool helps you import GitHub repository URLs from:
  • Google Sheets (via copy-paste)
  • Text files
  • Clipboard
  • Direct text input

"""
    print(banner)
    
    print("How would you like to import repositories?")
    print("  1. Paste text directly (from Google Sheets, etc.)")
    print("  2. Import from file")
    print("  3. Import from clipboard")
    print("  4. Cancel")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    repos = []
    
    if choice == '1':
        repos = import_from_text()
    elif choice == '2':
        file_path = input("Enter file path: ").strip()
        repos = import_from_file(file_path)
    elif choice == '3':
        repos = import_from_clipboard()
    elif choice == '4':
        print("Import cancelled")
        sys.exit(0)
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    if not repos:
        print("\n⚠️  No GitHub repository URLs found")
        print("\nMake sure your text contains URLs like:")
        print("  https://github.com/facebook/react")
        sys.exit(0)
    
    print(f"\n📋 Found {len(repos)} repository URLs:")
    for i, repo in enumerate(repos[:10], 1):
        print(f"  {i}. {repo}")
    if len(repos) > 10:
        print(f"  ... and {len(repos) - 10} more")
    
    response = input(f"\nAdd these {len(repos)} repositories? (Y/n): ").strip()
    if response.lower() != 'n':
        save_repositories(repos, append=True)
        print("\n✅ Done! You can now run the agent with: python agent.py --dry-run")
    else:
        print("Import cancelled")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nImport cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
