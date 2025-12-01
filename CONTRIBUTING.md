# Contributing to GitHub Issue Hunter

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Clear description of the feature
- Use case and motivation
- Example of how it would work

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/github-issue-hunter.git
cd github-issue-hunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and concise
- Write descriptive variable names

## Testing

Before submitting a PR:

1. Test in dry-run mode:
```bash
python agent.py --dry-run --max-issues 3
```

2. Test with real execution (use a test repository):
```bash
python agent.py --max-issues 1
```

3. Check for errors in logs:
```bash
cat logs/agent.log
```

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- [ ] Add support for more AI providers (Google Gemini, local models)
- [ ] Improve issue relevance scoring
- [ ] Add metrics dashboard
- [ ] Better error handling and retry logic

### Medium Priority
- [ ] Support for GitLab and Bitbucket
- [ ] Web UI for configuration
- [ ] Database for tracking processed issues
- [ ] Slack/Discord notifications

### Documentation
- [ ] Video tutorial
- [ ] More code examples
- [ ] Translation to other languages
- [ ] FAQ section

## Questions?

Feel free to open an issue with the "question" label if you need help!

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help each other learn and grow

Thank you for contributing! 🚀
