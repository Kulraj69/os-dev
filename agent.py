"""
GitHub Issue Hunter - Main Agent
Monitors repositories for good first issues and suggests solutions
"""
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List
import yaml
from dotenv import load_dotenv

from github_client import GitHubClient
from issue_analyzer import IssueAnalyzer

# Load environment variables
load_dotenv()

# Setup logging
def setup_logging(config: dict):
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_config.get('file', 'logs/agent.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from config.yaml"""
    config_path = Path('config.yaml')
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_repositories() -> List[str]:
    """Load repository URLs from repos.txt"""
    repos_path = Path('repos.txt')
    if not repos_path.exists():
        raise FileNotFoundError("repos.txt not found")
    
    with open(repos_path, 'r') as f:
        repos = [
            line.strip() 
            for line in f 
            if line.strip() and not line.strip().startswith('#')
        ]
    
    return repos


def save_activity_log(issue_data: dict):
    """Save activity log for processed issues"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"processed_issues_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(log_file, 'a') as f:
        timestamp = datetime.now().isoformat()
        f.write(f"{timestamp} | {issue_data['repo']} | Issue #{issue_data['number']} | {issue_data['action']}\n")


def main():
    """Main agent logic"""
    parser = argparse.ArgumentParser(description='GitHub Issue Hunter Agent')
    parser.add_argument('--dry-run', action='store_true', help='Run without posting comments')
    parser.add_argument('--max-issues', type=int, help='Maximum issues to process per run')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    logger = setup_logging(config)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 80)
    logger.info("GitHub Issue Hunter Agent Starting")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Dry Run: {args.dry_run or os.getenv('DRY_RUN', 'false').lower() == 'true'}")
    logger.info("=" * 80)
    
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("GITHUB_TOKEN not found in environment variables")
        sys.exit(1)
    
    llm_model = os.getenv('LLM_MODEL', config['ai_settings']['model'])
    
    # Initialize clients
    try:
        github_client = GitHubClient(github_token)
        analyzer = IssueAnalyzer(
            model=llm_model,
            temperature=config['ai_settings']['temperature']
        )
    except Exception as e:
        logger.error(f"Error initializing clients: {e}")
        sys.exit(1)
    
    # Load repositories
    try:
        repo_urls = load_repositories()
        logger.info(f"Loaded {len(repo_urls)} repositories to monitor")
    except FileNotFoundError as e:
        logger.error(f"Error loading repositories: {e}")
        sys.exit(1)
    
    # Process repositories
    max_issues = args.max_issues or int(os.getenv('MAX_ISSUES_PER_RUN', 10))
    dry_run = args.dry_run or os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    total_issues_found = 0
    total_comments_posted = 0
    total_issues_analyzed = 0
    
    for repo_url in repo_urls: # Changed from `repos` to `repo_urls` to match existing variable
        logger.info("\n" + "=" * 60)
        logger.info(f"Processing URL: {repo_url}")
        logger.info("=" * 60)
        
        try:
            # Get repositories (could be one or multiple if org)
            target_repos = github_client.get_repositories_from_url(repo_url) # Changed `client` to `github_client`
            
            if not target_repos:
                logger.warning(f"Skipping {repo_url} - could not fetch repository info")
                continue
                
            for repository in target_repos:
                if total_issues_analyzed >= max_issues: # Changed `issues_processed` to `total_issues_analyzed`
                    break
                    
                logger.info(f"Scanning repository: {repository.full_name}")
                
                # Find good first issues
                issues = github_client.get_good_first_issues( # Changed `client` to `github_client`
                    repository, 
                    config['target_labels'], # Changed `config['labels']` to `config['target_labels']`
                    config.get('exclude_labels', []),
                    config.get('max_issue_age_days', 90)
                )
                
                if not issues:
                    logger.info(f"Found 0 potential issues in {repository.full_name}")
                    continue
                    
                logger.info(f"Found {len(issues)} potential issues in {repository.full_name}")
                
                for issue in issues:
                    if total_issues_analyzed >= max_issues: # Changed `issues_processed` to `total_issues_analyzed`
                        break
                        
                    logger.info(f"\n--- Issue #{issue.number}: {issue.title}")
                    
                    # Check if already commented
                    bot_username = github_client.user.login
                    if github_client.has_bot_commented(
                        issue, 
                        bot_username, 
                        hours=config.get('min_comment_interval_hours', 168)
                    ):
                        logger.info(f"Already commented on this issue recently, skipping")
                        continue
                    
                    # Get issue context
                    issue_context = github_client.get_issue_context(issue)
                    
                    # Check if suitable
                    should_attempt, reason = analyzer.should_attempt_issue(issue_context)
                    if not should_attempt:
                        logger.info(f"Skipping issue: {reason}")
                        continue
                    
                    logger.info("Issue appears suitable, analyzing...")
                    total_issues_analyzed += 1
                    
                    # Analyze issue
                    analysis = analyzer.analyze_issue(issue_context)
                    if not analysis:
                        logger.warning("Failed to analyze issue, skipping")
                        continue
                    
                    logger.info(f"Analysis: {analysis['analysis'][:100]}...")
                    
                    # Generate comment
                    comment = analyzer.generate_comment(
                        analysis=analysis,
                        template=config['comment_template'],
                        issue_title=issue.title
                    )
                    
                    # Post comment
                    success = github_client.post_comment(issue, comment, dry_run=dry_run)
                    
                    if success:
                        total_comments_posted += 1
                        action = "Would comment" if dry_run else "Commented"
                        logger.info(f"✅ {action} on issue #{issue.number}")
                        
                        # Log activity
                        save_activity_log({
                            'repo': repository.full_name, # Changed `repo.full_name` to `repository.full_name`
                            'number': issue.number,
                            'title': issue.title,
                            'action': action,
                            'url': issue.html_url
                        })
                    
                    # Be respectful - don't spam
                    if total_comments_posted >= max_issues:
                        break # Break from inner issue loop
            
        except Exception as e:
            logger.error(f"Error processing {repo_url}: {e}")
            continue
            if total_issues_analyzed >= max_issues:
                logger.info("Reached maximum issues limit")
                break
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Agent Run Summary")
    logger.info("=" * 80)
    logger.info(f"Repositories scanned: {len(repo_urls)}")
    logger.info(f"Issues found: {total_issues_found}")
    logger.info(f"Issues analyzed: {total_issues_analyzed}")
    logger.info(f"Comments {'would be ' if dry_run else ''}posted: {total_comments_posted}")
    logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAgent stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
