"""
GitHub API Client
Handles all interactions with the GitHub API
"""
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from github import Github, GithubException
from github.Issue import Issue
from github.Repository import Repository

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, token: str):
        """Initialize GitHub client with authentication token"""
        self.github = Github(token)
        self.user = self.github.get_user()
        logger.info(f"Authenticated as: {self.user.login}")
        
    def parse_repo_url(self, url: str) -> tuple:
        """Parse GitHub URL to extract owner and repo name"""
        # Remove trailing slashes and .git
        url = url.rstrip('/').rstrip('.git')
        
        # Handle different URL formats
        if 'github.com/' in url:
            parts = url.split('github.com/')[-1].split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def get_repositories_from_url(self, url: str) -> List[Repository]:
        """Get list of repositories from a URL (single repo or organization)"""
        repos = []
        url = url.rstrip('/').rstrip('.git')
        
        try:
            if 'github.com/' in url:
                parts = url.split('github.com/')[-1].split('/')
                
                if len(parts) == 1:
                    # It's an organization or user
                    name = parts[0]
                    try:
                        # Try as organization first
                        org = self.github.get_organization(name)
                        # Get top 5 repos by stars to avoid overwhelming
                        org_repos = org.get_repos(sort='stars', direction='desc')
                        for repo in org_repos[:5]:
                            repos.append(repo)
                        logger.info(f"Fetched top 5 repositories for organization: {name}")
                    except GithubException:
                        # Try as user
                        try:
                            user = self.github.get_user(name)
                            user_repos = user.get_repos(sort='stars', direction='desc')
                            for repo in user_repos[:5]:
                                repos.append(repo)
                            logger.info(f"Fetched top 5 repositories for user: {name}")
                        except GithubException:
                            logger.error(f"Could not find organization or user: {name}")
                            
                elif len(parts) >= 2:
                    # It's a specific repository
                    repo_name = f"{parts[0]}/{parts[1]}"
                    repo = self.github.get_repo(repo_name)
                    repos.append(repo)
                    logger.info(f"Fetched repository: {repo.full_name}")
                    
        except GithubException as e:
            logger.error(f"Error fetching repositories from {url}: {e}")
            
        return repos

    def get_repository(self, repo_url: str) -> Optional[Repository]:
        """Legacy method for backward compatibility"""
        repos = self.get_repositories_from_url(repo_url)
        return repos[0] if repos else None
    
    def get_good_first_issues(
        self, 
        repository: Repository, 
        labels: List[str],
        exclude_labels: List[str] = None,
        max_age_days: int = 90
    ) -> List[Issue]:
        """Get open issues with specified labels"""
        issues = []
        exclude_labels = exclude_labels or []
        
        try:
            # Search for issues with any of the target labels
            for label in labels:
                try:
                    repo_issues = repository.get_issues(
                        state='open',
                        labels=[label],
                        sort='created',
                        direction='desc'
                    )
                    
                    for issue in repo_issues:
                        # Skip pull requests
                        if issue.pull_request:
                            continue
                        
                        # Check age
                        age = datetime.now() - issue.created_at.replace(tzinfo=None)
                        if age.days > max_age_days:
                            continue
                        
                        # Check exclude labels
                        issue_labels = [l.name for l in issue.labels]
                        if any(ex_label in issue_labels for ex_label in exclude_labels):
                            continue
                        
                        # Check if already assigned
                        if issue.assignee or issue.assignees:
                            continue
                        
                        # Avoid duplicates (issue may have multiple target labels)
                        if issue not in issues:
                            issues.append(issue)
                            
                except GithubException as e:
                    logger.warning(f"Error fetching issues with label '{label}': {e}")
                    continue
            
            logger.info(f"Found {len(issues)} good first issues in {repository.full_name}")
            return issues
            
        except GithubException as e:
            logger.error(f"Error fetching issues from {repository.full_name}: {e}")
            return []
    
    def get_issue_context(self, issue: Issue, max_files: int = 5) -> Dict:
        """Get relevant context about an issue"""
        context = {
            'title': issue.title,
            'body': issue.body or '',
            'labels': [l.name for l in issue.labels],
            'created_at': issue.created_at,
            'comments_count': issue.comments,
            'comments': [],
            'related_files': []
        }
        
        # Get recent comments
        try:
            if issue.comments > 0:
                comments = issue.get_comments()
                context['comments'] = [
                    {
                        'author': c.user.login,
                        'body': c.body,
                        'created_at': c.created_at
                    }
                    for c in list(comments)[-5:]  # Last 5 comments
                ]
        except GithubException as e:
            logger.warning(f"Error fetching comments: {e}")
        
        return context
    
    def has_bot_commented(self, issue: Issue, bot_username: str, hours: int = 168) -> bool:
        """Check if bot has already commented on this issue recently"""
        try:
            if issue.comments == 0:
                return False
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            comments = issue.get_comments()
            
            for comment in comments:
                if (comment.user.login == bot_username and 
                    comment.created_at.replace(tzinfo=None) > cutoff_time):
                    return True
            
            return False
            
        except GithubException as e:
            logger.error(f"Error checking comments: {e}")
            return True  # Err on side of caution
    
    def post_comment(self, issue: Issue, comment: str, dry_run: bool = False) -> bool:
        """Post a comment on an issue"""
        if dry_run:
            logger.info(f"[DRY RUN] Would post comment on issue #{issue.number}:")
            logger.info(f"--- Comment Preview ---\n{comment}\n--- End Preview ---")
            return True
        
        try:
            issue.create_comment(comment)
            logger.info(f"Posted comment on issue #{issue.number}: {issue.title}")
            return True
        except GithubException as e:
            logger.error(f"Error posting comment: {e}")
            return False
    
    def get_file_content(self, repository: Repository, file_path: str) -> Optional[str]:
        """Get content of a file from repository"""
        try:
            content = repository.get_contents(file_path)
            if isinstance(content, list):
                return None
            return content.decoded_content.decode('utf-8')
        except GithubException:
            return None
    
    def search_related_files(
        self, 
        repository: Repository, 
        keywords: List[str],
        extensions: List[str] = None
    ) -> List[str]:
        """Search for files related to the issue"""
        related_files = []
        extensions = extensions or ['.py', '.js', '.ts', '.go', '.java']
        
        try:
            # Search in repository
            for keyword in keywords[:3]:  # Limit keywords
                for ext in extensions[:3]:  # Limit extensions
                    query = f"{keyword} extension:{ext[1:]} repo:{repository.full_name}"
                    try:
                        results = self.github.search_code(query=query)
                        for result in list(results)[:2]:  # Limit results per search
                            if result.path not in related_files:
                                related_files.append(result.path)
                                if len(related_files) >= 5:
                                    return related_files
                    except GithubException:
                        continue
        except Exception as e:
            logger.warning(f"Error searching files: {e}")
        
        return related_files
