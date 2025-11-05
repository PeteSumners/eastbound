#!/usr/bin/env python3
"""
Test script to verify your automation setup.

Usage:
    python scripts/test_setup.py
"""

import os
import sys
from pathlib import Path


def check_env_var(name, required=True):
    """Check if environment variable is set."""
    value = os.getenv(name)
    if value:
        print(f"✅ {name} is set")
        return True
    else:
        if required:
            print(f"❌ {name} is NOT set (required)")
        else:
            print(f"⚠️  {name} is NOT set (optional)")
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    required = ['yaml', 'markdown', 'tweepy']

    print("\n📦 Checking Python dependencies...")
    all_good = True

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            all_good = False

    if not all_good:
        print("\n💡 Install dependencies with: pip install -r requirements.txt")

    return all_good


def check_directory_structure():
    """Check if directory structure exists."""
    print("\n📁 Checking directory structure...")

    required_dirs = [
        'content/drafts',
        'content/scheduled',
        'content/published',
        'templates',
        'scripts',
        '.github/workflows'
    ]

    all_good = True
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ does NOT exist")
            all_good = False

    return all_good


def check_templates():
    """Check if templates exist."""
    print("\n📝 Checking templates...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    required_templates = [
        'templates/weekly-analysis.md',
        'templates/translation.md'
    ]

    all_good = True
    for template_path in required_templates:
        full_path = project_root / template_path
        if full_path.exists():
            print(f"✅ {template_path} exists")
        else:
            print(f"❌ {template_path} does NOT exist")
            all_good = False

    return all_good


def check_scripts():
    """Check if scripts exist."""
    print("\n🔧 Checking scripts...")

    script_dir = Path(__file__).parent
    required_scripts = [
        'create_draft.py',
        'publish_to_substack.py',
        'post_to_twitter.py'
    ]

    all_good = True
    for script_name in required_scripts:
        script_path = script_dir / script_name
        if script_path.exists():
            print(f"✅ scripts/{script_name} exists")
        else:
            print(f"❌ scripts/{script_name} does NOT exist")
            all_good = False

    return all_good


def check_workflows():
    """Check if GitHub Actions workflows exist."""
    print("\n⚙️  Checking GitHub Actions workflows...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    required_workflows = [
        '.github/workflows/publish-scheduled.yml',
        '.github/workflows/manual-publish.yml',
        '.github/workflows/create-draft.yml'
    ]

    all_good = True
    for workflow_path in required_workflows:
        full_path = project_root / workflow_path
        if full_path.exists():
            print(f"✅ {workflow_path} exists")
        else:
            print(f"❌ {workflow_path} does NOT exist")
            all_good = False

    return all_good


def check_substack_config():
    """Check Substack configuration."""
    print("\n📧 Checking Substack configuration...")

    checks = [
        ('SUBSTACK_EMAIL', True),
        ('SMTP_SERVER', True),
        ('SMTP_PORT', True),
        ('SMTP_USERNAME', True),
        ('SMTP_PASSWORD', True)
    ]

    all_good = True
    for var_name, required in checks:
        if not check_env_var(var_name, required):
            all_good = False

    if not all_good:
        print("\n💡 For Substack publishing, set these environment variables:")
        print("   - SUBSTACK_EMAIL: eastboundreports@substack.com")
        print("   - SMTP_SERVER: smtp.gmail.com (or your email provider)")
        print("   - SMTP_PORT: 587")
        print("   - SMTP_USERNAME: your email")
        print("   - SMTP_PASSWORD: your email password or app-specific password")

    return all_good


def check_twitter_config():
    """Check Twitter configuration."""
    print("\n🐦 Checking Twitter configuration...")

    checks = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]

    all_good = True
    for var_name in checks:
        if not check_env_var(var_name, required=True):
            all_good = False

    if not all_good:
        print("\n💡 Get Twitter API credentials from:")
        print("   https://developer.twitter.com/en/portal/dashboard")

    return all_good


def main():
    """Run all checks."""
    print("=" * 60)
    print("🔍 EASTBOUND AUTOMATION SETUP VERIFICATION")
    print("=" * 60)

    checks = [
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directory_structure),
        ("Templates", check_templates),
        ("Scripts", check_scripts),
        ("GitHub Actions Workflows", check_workflows),
        ("Substack Configuration", check_substack_config),
        ("Twitter Configuration", check_twitter_config)
    ]

    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ Error during {check_name} check: {e}")
            results[check_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Your automation is ready.")
        print("\n📚 Next steps:")
        print("1. Push to GitHub")
        print("2. Add secrets in GitHub repository settings")
        print("3. Enable GitHub Actions")
        print("4. Create your first draft!")
        print("\nSee AUTOMATION_SETUP.md for detailed instructions.")
    else:
        print("⚠️  Some checks failed. Review the output above.")
        print("\n💡 Common fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Set environment variables (see AUTOMATION_SETUP.md)")
        print("- Ensure you're running from the project root directory")

    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
