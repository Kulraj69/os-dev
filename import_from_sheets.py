#!/usr/bin/env python3
"""
Import repositories directly from Google Sheets
Uses service account credentials to access the sheet
"""
import os
import re
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path


def extract_github_urls(text: str) -> list:
    """Extract GitHub repository URLs from text"""
    pattern = r'https?://github\.com/[\w-]+/[\w.-]+'
    urls = re.findall(pattern, text)
    
    # Clean and deduplicate
    cleaned_urls = []
    seen = set()
    
    for url in urls:
        url = url.rstrip('/').rstrip('.git')
        if url not in seen:
            seen.add(url)
            cleaned_urls.append(url)
    
    return cleaned_urls


def import_from_google_sheets(sheet_url: str):
    """Import repositories from Google Sheets"""
    print(f"📊 Connecting to Google Sheets...")
    
    # Load credentials
    creds_file = Path('google_credentials.json')
    if not creds_file.exists():
        print("❌ google_credentials.json not found")
        print("   Place your Google service account credentials in this file")
        return []
    
        # Authenticate
        # Define scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Try loading from environment variable (for GitHub Actions)
        json_creds = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if json_creds:
            import json
            creds_dict = json.loads(json_creds)
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif creds_file.exists():
            creds = Credentials.from_service_account_file(str(creds_file), scopes=scopes)
        else:
            print("❌ google_credentials.json not found and GOOGLE_CREDENTIALS_JSON env var not set")
            return []
            
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)  # First worksheet
        
        print(f"✅ Connected to: {sheet.title}")
        
        # Get all values
        all_values = worksheet.get_all_values()
        
        repos = []
        
        # Check if we have explicit URLs
        all_text = '\n'.join([' '.join(row) for row in all_values])
        explicit_repos = extract_github_urls(all_text)
        
        if explicit_repos:
            print(f"📋 Found {len(explicit_repos)} explicit repository URLs")
            repos.extend(explicit_repos)
        
        # If we have names but no URLs, search for them
        if len(all_values) > 1:
            print("\n🔍 Searching for repositories based on names (using SerpApi)...")
            from serpapi import GoogleSearch
            
            serp_api_key = "a332f44acf4c2fa8ea196642a535584c4812527e01b20a9a572237fa18f6a2ed"
            
            # Assuming Name is in the first column (index 0)
            # Skip header row
            for i, row in enumerate(all_values[1:]):
                name = row[0].strip()
                if not name:
                    continue
                    
                # Skip if we already found a URL for this row (heuristic)
                if any(repo in ' '.join(row) for repo in explicit_repos):
                    continue
                
                print(f"   Searching for: {name}...")
                try:
                    params = {
                        "q": f"github {name} repository",
                        "api_key": serp_api_key,
                        "num": 1
                    }
                    
                    search = GoogleSearch(params)
                    results = search.get_dict()
                    organic_results = results.get("organic_results", [])
                    
                    found = False
                    for result in organic_results:
                        link = result.get("link", "")
                        print(f"     Result: {link}")
                        
                        if "github.com" in link:
                            # Clean URL to get repo root
                            parts = link.split('github.com/')
                            if len(parts) > 1:
                                path_parts = parts[1].split('/')
                                if len(path_parts) >= 1:
                                    # Handle org/repo or just org
                                    owner = path_parts[0]
                                    repo = path_parts[1] if len(path_parts) > 1 else ""
                                    
                                    # Clean up repo name
                                    if repo:
                                        repo = repo.split('?')[0].replace('.git', '')
                                        repo_url = f"https://github.com/{owner}/{repo}"
                                    else:
                                        # It's an org URL, try to guess or just use it
                                        repo_url = f"https://github.com/{owner}"
                                    
                                    if repo_url not in repos:
                                        repos.append(repo_url)
                                        print(f"   ✅ Found: {repo_url}")
                                        
                                        # Update the sheet with the found URL
                                        try:
                                            # Column D is index 4 (1-based)
                                            # Row index is i + 2 (1-based, +1 for header, +1 for 0-index loop)
                                            row_idx = i + 2
                                            worksheet.update_cell(row_idx, 4, repo_url)
                                            print(f"      Updated sheet row {row_idx}")
                                        except Exception as e:
                                            print(f"      ⚠️ Could not update sheet: {e}")
                                            
                                        found = True
                                        break
                    
                    if not found:
                        print(f"   ❌ No GitHub URL found for {name}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error searching for {name}: {e}")
        
        return repos
        
    except Exception as e:
        print(f"❌ Error accessing Google Sheets: {e}")
        return []


def save_repositories(repos: list, append: bool = True):
    """Save repositories to repos.txt"""
    if not repos:
        print("⚠️  No repositories to save")
        return
    
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
        print("⚠️  No new repositories (all already exist in repos.txt)")
        return
    
    # Write to file
    mode = 'a' if append else 'w'
    with open(repos_path, mode) as f:
        if append and repos_path.stat().st_size > 0:
            f.write('\n')
        
        for repo in new_repos:
            f.write(f"{repo}\n")
    
    print(f"✅ Added {len(new_repos)} new repositories")
    print(f"   Total repositories: {len(existing) + len(new_repos)}")


def main():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║        Import Repositories from Google Sheets                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    # Default sheet URL from user's request
    default_sheet_url = "https://docs.google.com/spreadsheets/d/1LTlr3ITW3KVZYRly603WO-BVt3hCSIy-HZJyOEqGnmk/edit"
    
    print(f"Default sheet: {default_sheet_url}")
    use_default = input("\nUse this sheet? (Y/n): ").strip().lower()
    
    if use_default != 'n':
        sheet_url = default_sheet_url
    else:
        sheet_url = input("\nEnter Google Sheets URL: ").strip()
    
    # Import repositories
    repos = import_from_google_sheets(sheet_url)
    
    if repos:
        print(f"\n📋 Found repositories:")
        for i, repo in enumerate(repos[:10], 1):
            print(f"  {i}. {repo}")
        if len(repos) > 10:
            print(f"  ... and {len(repos) - 10} more")
        
        response = input(f"\nAdd these {len(repos)} repositories to repos.txt? (Y/n): ").strip()
        if response.lower() != 'n':
            save_repositories(repos, append=True)
    else:
        print("\n⚠️  No repositories found")
        print("\nMake sure:")
        print("  1. The Google Sheet is shared with the service account email")
        print("  2. The sheet contains GitHub repository URLs")
        print(f"  3. Service account email: kulraj@hackathon-bot-479820.iam.gserviceaccount.com")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nImport cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
