# 🤖 GitHub Issue Hunter

**AI-Powered Open Source Contribution Agent**

Automatically discover, analyze, and contribute to GitHub "good first issues" using AI. This agent monitors repositories, provides intelligent solution suggestions, and helps you build your open source contribution profile.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- 🔍 **Auto-Discovery**: Scans multiple repositories for "good first issues"
- 🤖 **AI-Powered Analysis**: Uses GPT-4 or Claude to understand issues and suggest solutions
- 💬 **Smart Commenting**: Posts helpful, professional solution suggestions
- 📅 **Automated Scheduling**: Runs twice daily via GitHub Actions
- 📊 **Activity Tracking**: Comprehensive logging of all interactions
- 🎯 **Intelligent Filtering**: Prioritizes suitable beginner-friendly issues
- 🔄 **Multi-Repo Support**: Monitor unlimited repositories simultaneously

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/github-issue-hunter.git
cd github-issue-hunter

# Run interactive setup
python3 setup.py
```

The setup wizard will guide you through:
- Configuring API keys
- Adding repositories
- Installing dependencies
- Running your first test

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Add repositories:**
   ```bash
   # Edit repos.txt or use the import tool
   python3 import_repos.py
   ```

4. **Test the agent:**
   ```bash
   # See a demo
   python3 demo.py
   
   # Dry run (no actual comments)
   python3 agent.py --dry-run --max-issues 2
   
   # Real run
   python3 agent.py
   ```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Detailed step-by-step setup
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to this project
- **Configuration** - See `config.yaml` for all options

## 💡 How It Works

1. **Repository Scanning**: Reads repo list from `repos.txt` or imported from Google Sheets
2. **Issue Discovery**: Searches for issues with labels like "good first issue", "help wanted"
3. **AI Analysis**: Analyzes each issue using GPT-4/Claude to:
   - Understand the problem context
   - Review related code (if applicable)
   - Generate intelligent solution suggestions
4. **Solution Posting**: Comments on the issue with:
   - Clear problem analysis
   - Detailed proposed solution
   - Step-by-step implementation guide
   - Professional request for assignment
5. **Activity Logging**: Records all actions in `logs/` directory with timestamps

## 📁 Project Structure

```
github-issue-hunter/
├── agent.py              # Main orchestration logic
├── issue_analyzer.py     # AI-powered issue analysis
├── github_client.py      # GitHub API wrapper
├── setup.py              # Interactive setup wizard
├── import_repos.py       # Import repos from Google Sheets
├── demo.py               # Demo without API keys
├── verify.py             # Verify setup completeness
├── config.yaml           # Configuration settings
├── repos.txt             # List of repositories to monitor
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .github/
│   └── workflows/
│       └── daily_run.yml # GitHub Actions workflow
└── logs/                 # Activity logs
```

## 🔑 Required API Keys

### GitHub Personal Access Token
Create at: https://github.com/settings/tokens

Required scopes:
- `repo` - Full control of private repositories
- `public_repo` - Access public repositories

### AI Provider (choose one)

**Option 1: OpenAI**
- Get key at: https://platform.openai.com/api-keys
- Recommended model: `gpt-4-turbo-preview` or `gpt-3.5-turbo` (cheaper)

**Option 2: Anthropic Claude**
- Get key at: https://console.anthropic.com/
- Recommended model: `claude-3-sonnet-20240229`

## 🔧 Importing Repositories from Google Sheets

You mentioned you have repositories in a Google Sheets. Here's how to import them:

1. **Copy URLs from your Google Sheet**
2. **Run the import tool:**
   ```bash
   python3 import_repos.py
   ```
3. **Choose option 1** (Paste text directly)
4. **Paste the URLs** and press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows)

The tool will automatically extract all GitHub repository URLs and add them to `repos.txt`.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/YOUR-USERNAME/github-issue-hunter/issues)
- **Documentation**: Check [QUICKSTART.md](QUICKSTART.md) for detailed guides

## ⚠️ Best Practices

1. **Start Small**: Begin with 2-3 repositories to test
2. **Use Dry-Run**: Always test with `--dry-run` first
3. **Be Respectful**: Limit `MAX_ISSUES_PER_RUN` to avoid spamming
4. **Monitor Responses**: Check logs and GitHub notifications regularly
5. **Contribute Genuinely**: Only comment when you can actually help

---

**Happy Contributing!** 🚀

Built with ❤️ for the open source community

