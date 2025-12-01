import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from github import Github, GithubException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_sheets_client():
    """Setup Google Sheets client"""
    creds_file = Path("google_credentials.json")

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # Try loading from environment variable (for GitHub Actions)
        json_creds = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if json_creds:
            import json
            creds_dict = json.loads(json_creds)
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif creds_file.exists():
            creds = Credentials.from_service_account_file(str(creds_file), scopes=scopes)
        else:
            logger.error("google_credentials.json not found and GOOGLE_CREDENTIALS_JSON env var not set")
            return None
            
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Error authenticating with Google Sheets: {e}")
        return None

def get_repo_stats(github_client, repo_url):
    """Get stats for a repository"""
    try:
        # Parse URL
        if 'github.com/' not in repo_url:
            return None
            
        parts = repo_url.split('github.com/')[-1].split('/')
        
        repo = None
        if len(parts) == 1:
            # Organization URL
            try:
                org_name = parts[0]
                # Try as org
                try:
                    org = github_client.get_organization(org_name)
                    # Get top repo by stars
                    repos = org.get_repos(sort='stars', direction='desc')
                    if repos.totalCount > 0:
                        repo = repos[0]
                        logger.info(f"Using top repo {repo.full_name} for org {org_name}")
                except:
                    # Try as user
                    user = github_client.get_user(org_name)
                    repos = user.get_repos(sort='stars', direction='desc')
                    if repos.totalCount > 0:
                        repo = repos[0]
            except Exception as e:
                logger.warning(f"Could not resolve org/user {parts[0]}: {e}")
                return None
        else:
            # Specific repo
            repo_name = f"{parts[0]}/{parts[1]}"
            repo = github_client.get_repo(repo_name)
            
        if not repo:
            return None
        
        # Get stats
        stats = {
            'last_pushed': repo.pushed_at,
            'open_issues': repo.open_issues_count,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
        }
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # New issues in last 7 days
        new_issues = repo.get_issues(state='all', since=seven_days_ago)
        stats['new_issues_7d'] = new_issues.totalCount
        
        # Active contributors (from commits in last 7 days)
        commits = repo.get_commits(since=seven_days_ago)
        contributors = set()
        for commit in commits:
            if commit.author:
                contributors.add(commit.author.login)
        stats['active_contributors_7d'] = len(contributors)
        
        # Get good first issues count
        good_first_issues = 0
        try:
            # Common labels for beginner issues
            labels = ['good first issue', 'good-first-issue', 'beginner', 'help wanted', 'up-for-grabs']
            for label in labels:
                try:
                    issues = repo.get_issues(state='open', labels=[label])
                    good_first_issues += issues.totalCount
                except:
                    pass
        except:
            pass
            
        stats['good_first_issues'] = good_first_issues
        
        return stats
        
    except GithubException as e:
        logger.error(f"Error fetching stats for {repo_url}: {e}")
        return None

def update_sheet_headers(worksheet):
    """Ensure headers exist"""
    headers = worksheet.row_values(1)
    required_headers = ['Last Scanned', 'Latest Activity', 'New Issues (7d)', 'Active Contributors (7d)', 'Stars', 'Good First Issues']
    
    # Check if headers exist, if not add them
    for header in required_headers:
        if header not in headers:
            # Add to next available column
            col_idx = len(headers) + 1
            worksheet.update_cell(1, col_idx, header)
            headers.append(header)
            logger.info(f"Added header column: {header}")
            
    return headers

def main():
    load_dotenv()
    
    # Setup GitHub client
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("GITHUB_TOKEN not found")
        sys.exit(1)
    
    gh = Github(github_token)
    
    # Setup Sheets client
    gc = setup_sheets_client()
    if not gc:
        sys.exit(1)
        
    # Open sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1LTlr3ITW3KVZYRly603WO-BVt3hCSIy-HZJyOEqGnmk/edit"
    try:
        sh = gc.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0) # First sheet
    except Exception as e:
        logger.error(f"Error opening sheet: {e}")
        sys.exit(1)
        
    # Ensure headers
    headers = update_sheet_headers(worksheet)
    
    # Map headers to column indices
    header_map = {h: i+1 for i, h in enumerate(headers)}
    
    # Get all values
    rows = worksheet.get_all_values()
    
    logger.info(f"Scanning {len(rows)-1} repositories...")
    
    # Process each row
    for i, row in enumerate(rows[1:], start=2): # Start at row 2
        # Assuming 'Repo' is in column 4 (D) based on previous interaction
        # Better to find it dynamically
        repo_col_idx = header_map.get('Repo')
        if not repo_col_idx:
            logger.error("'Repo' column not found")
            break
            
        repo_url = row[repo_col_idx-1] if len(row) >= repo_col_idx else ""
        
        if not repo_url or 'github.com' not in repo_url:
            continue
            
        logger.info(f"Checking {repo_url}...")
        stats = get_repo_stats(gh, repo_url)
        
        if stats:
            # Prepare row data
            # We need to preserve existing data in other columns
            # So we'll construct a list of values for the specific columns we want to update
            
            # Find the range of columns we are updating
            # We are updating: Last Scanned, Latest Activity, New Issues (7d), Active Contributors (7d), Stars, Good First Issues
            # These might not be contiguous, so batch update of a range is tricky if they are scattered.
            # However, usually they are appended at the end.
            
            # Let's try to update cells individually but with a sleep to avoid rate limit?
            # Or better, use batch_update.
            
            cells = []
            updates = [
                ('Last Scanned', datetime.now().strftime('%Y-%m-%d %H:%M')),
                ('Latest Activity', stats['last_pushed'].strftime('%Y-%m-%d')),
                ('New Issues (7d)', stats['new_issues_7d']),
                ('Active Contributors (7d)', stats['active_contributors_7d']),
                ('Stars', stats['stars']),
                ('Good First Issues', stats['good_first_issues'])
            ]
            
            for col_name, value in updates:
                col_idx = header_map.get(col_name)
                if col_idx:
                    # Create a Cell object
                    cells.append(gspread.Cell(i, col_idx, value))
            
            try:
                if cells:
                    worksheet.update_cells(cells)
                    import time
                    time.sleep(1.5) # Sleep to respect rate limit (60/min = 1/sec)
            except Exception as e:
                logger.error(f"Error updating cells: {e}")
            
            logger.info(f"✅ Updated stats for {repo_url}")
        else:
            logger.warning(f"Could not fetch stats for {repo_url}")

if __name__ == "__main__":
    main()
