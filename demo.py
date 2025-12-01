#!/usr/bin/env python3
"""
Demo script to test the GitHub Issue Hunter without actual GitHub actions
Shows what the agent would do with sample data
"""
import json
from datetime import datetime


def demo_issue_analysis():
    """Demonstrate issue analysis capabilities"""
    
    print("=" * 80)
    print("GitHub Issue Hunter - Demo Mode")
    print("=" * 80)
    print()
    
    # Sample issue
    sample_issue = {
        'number': 1234,
        'title': 'Add dark mode support to settings page',
        'body': """
Currently the settings page doesn't support dark mode while the rest of the app does.
It would be great to add dark mode support to maintain consistency.

The settings page is located in `src/components/Settings.js`
        """,
        'labels': ['good first issue', 'enhancement', 'ui'],
        'created_at': '2024-11-15',
        'comments_count': 2,
        'url': 'https://github.com/example/repo/issues/1234'
    }
    
    print("📋 Sample Issue:")
    print(f"   Title: {sample_issue['title']}")
    print(f"   Labels: {', '.join(sample_issue['labels'])}")
    print(f"   URL: {sample_issue['url']}")
    print()
    
    # Simulated AI analysis
    analysis = {
        'analysis': """
This issue requests adding dark mode support to the settings page to match 
the rest of the application. The issue is well-defined with a clear goal and 
even mentions the specific file location (src/components/Settings.js), making 
it an excellent candidate for a first contribution.
        """.strip(),
        
        'solution': """
The solution would involve applying the existing dark mode theme variables 
to the Settings component. Since dark mode is already implemented elsewhere 
in the app, we can follow the same pattern by importing the theme context 
and conditionally applying dark mode CSS classes based on the current theme state.
        """.strip(),
        
        'steps': [
            "Review how dark mode is implemented in other components",
            "Import the theme context/hook in Settings.js",
            "Add conditional CSS classes for dark mode styles",
            "Test the settings page in both light and dark modes",
            "Ensure all UI elements are visible and properly styled"
        ]
    }
    
    print("🤖 AI Analysis:")
    print(f"\n{analysis['analysis']}")
    print()
    
    print("💡 Proposed Solution:")
    print(f"\n{analysis['solution']}")
    print()
    
    print("📝 Implementation Steps:")
    for i, step in enumerate(analysis['steps'], 1):
        print(f"   {i}. {step}")
    print()
    
    # Generate comment
    comment_template = """Hi there! 👋

I've analyzed this issue and would like to contribute a solution. Here's my understanding and proposed approach:

## Problem Analysis
{analysis}

## Proposed Solution
{solution}

## Implementation Steps
{steps}

I'd love to work on this! Could you please assign this issue to me? I'm happy to discuss the approach before starting if you have any suggestions.

Thanks!
"""
    
    steps_formatted = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(analysis['steps'])])
    
    comment = comment_template.format(
        analysis=analysis['analysis'],
        solution=analysis['solution'],
        steps=steps_formatted
    )
    
    print("💬 Generated Comment Preview:")
    print("-" * 80)
    print(comment)
    print("-" * 80)
    print()
    
    # Activity log
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'repo': 'example/repo',
        'issue_number': sample_issue['number'],
        'issue_title': sample_issue['title'],
        'action': 'Analyzed and commented',
        'status': 'success'
    }
    
    print("📊 Activity Log Entry:")
    print(json.dumps(log_entry, indent=2))
    print()
    
    print("=" * 80)
    print("Demo Complete! 🎉")
    print("=" * 80)
    print()
    print("This demonstrates how the agent:")
    print("  ✅ Analyzes GitHub issues")
    print("  ✅ Generates intelligent solution suggestions")
    print("  ✅ Creates helpful, professional comments")
    print("  ✅ Logs all activities")
    print()
    print("To run the actual agent:")
    print("  python agent.py --dry-run    # Test mode (no comments posted)")
    print("  python agent.py              # Real mode (posts comments)")
    print()


if __name__ == "__main__":
    try:
        demo_issue_analysis()
    except Exception as e:
        print(f"Error in demo: {e}")
        import traceback
        traceback.print_exc()
