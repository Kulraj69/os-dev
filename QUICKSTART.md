# Quick Start Guide

Get your GitHub Issue Hunter agent up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- GitHub account
- OpenAI API key (or Anthropic API key)

## Step 1: Initial Setup

Run the interactive setup script:

```bash
python setup.py
```

This will guide you through:
- Creating your `.env` file with API keys
- Adding repositories to monitor
- Installing dependencies
- Testing your configuration

## Step 2: Configure Repositories

### Option A: Manual Entry
Edit `repos.txt` and add GitHub repository URLs (one per line):

```
https://github.com/facebook/react
https://github.com/microsoft/vscode
https://github.com/tensorflow/tensorflow
```

### Option B: Import from Google Sheets
1. Open your Google Sheets with repository URLs
2. Copy the URLs
3. Paste them into `repos.txt`

## Step 3: Test Run

Test the agent in dry-run mode (no comments will be posted):

```bash
python agent.py --dry-run --max-issues 2
```

This will:
- Scan repositories for good first issues
- Analyze issues with AI
- Show you what comments would be posted
- NOT actually post anything

## Step 4: First Real Run

Once you're happy with the dry-run results:

```bash
python agent.py --max-issues 5
```

This will:
- Find and analyze up to 5 issues
- Post helpful solution comments
- Request assignment on suitable issues
- Log all activity to `logs/`

## Step 5: Automate with GitHub Actions

### 5.1 Create a GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit: GitHub Issue Hunter"
git remote add origin https://github.com/YOUR-USERNAME/github-issue-hunter.git
git push -u origin main
```

### 5.2 Add Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `GH_PAT`: Your GitHub Personal Access Token
- `OPENAI_API_KEY`: Your OpenAI API key (or `ANTHROPIC_API_KEY`)

### 5.3 Enable GitHub Actions

The workflow in `.github/workflows/daily_run.yml` will automatically:
- Run twice daily (8 AM and 8 PM UTC)
- Process up to 10 issues per run
- Upload logs as artifacts
- Commit activity logs back to the repository

## Step 6: Monitor Activity

### View Logs Locally
```bash
cat logs/agent.log
cat logs/processed_issues_*.log
```

### View in GitHub Actions
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click on a workflow run to see details

## Customization

### Adjust Agent Behavior

Edit `config.yaml` to customize:

```yaml
# Change which labels to search for
target_labels:
  - "good first issue"
  - "help wanted"
  - "your-custom-label"

# Adjust AI temperature for more/less creative responses
ai_settings:
  temperature: 0.7  # 0.0 = deterministic, 1.0 = creative

# Modify comment template
comment_template: |
  Your custom comment template here...
```

## Troubleshooting

### "GitHub token not found"
Make sure you've created `.env` file with your `GITHUB_TOKEN`

### "OpenAI API error"
- Check your API key is correct in `.env`
- Ensure you have credits in your OpenAI account
- Try using `gpt-3.5-turbo` instead of `gpt-4` in config

### "No issues found"
- Check that repositories in `repos.txt` are valid and public
- Verify they have open issues with "good first issue" label
- Try adding more popular repositories

### Rate Limiting
If you hit GitHub API rate limits:
- Reduce `MAX_ISSUES_PER_RUN` in `.env`
- Increase time between runs in workflow

## Best Practices

1. **Start Small**: Begin with 2-3 repositories you're interested in
2. **Test First**: Always do a dry-run before real runs
3. **Be Respectful**: Don't spam projects - keep MAX_ISSUES_PER_RUN low
4. **Monitor Results**: Check logs to see which issues get responses
5. **Iterate**: Adjust comment template based on feedback from maintainers

## Advanced Usage

### Run for Specific Repositories
Create a custom repos list:
```bash
echo "https://github.com/your/favorite-repo" > my-repos.txt
python agent.py --repos-file my-repos.txt
```

### Different AI Models
In `.env`:
```bash
# Use GPT-3.5 (cheaper)
LLM_MODEL=gpt-3.5-turbo

# Use Claude
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=your_key_here
```

### Schedule Custom Times
Edit `.github/workflows/daily_run.yml`:
```yaml
schedule:
  # Run at 6 AM and 6 PM UTC
  - cron: '0 6,18 * * *'
```

## What's Next?

- ⭐ Star repositories you contribute to
- 📧 Watch for email notifications when maintainers respond
- 🔧 Submit PRs for issues you've analyzed
- 📈 Track your contributions growing!

Happy contributing! 🚀
