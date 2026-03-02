#!/usr/bin/env python3
"""
publish-skills - Publish OpenClaw skills to GitHub or ClawHub
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

def get_github_owner():
    """Get GitHub username from gh CLI"""
    try:
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return "vaca22"  # fallback

def publish_to_github(skill_name, all_skills=False):
    """Publish skill(s) to GitHub repository"""
    
    if all_skills:
        # Publish all skills
        repo_name = "openclaw-skills"
        skills_to_publish = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
        print(f"📦 Publishing {len(skills_to_publish)} skills to {repo_name}...")
    else:
        # Publish single skill
        repo_name = f"skill-{skill_name}"
        skills_to_publish = [skill_name]
        print(f"📦 Publishing {skill_name} to {repo_name}...")
    
    # Create temp directory for the repo
    temp_dir = WORKSPACE_DIR / f".tmp-{repo_name}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    try:
        # Copy skills to temp directory
        if all_skills:
            for skill in skills_to_publish:
                src = SKILLS_DIR / skill
                dst = temp_dir / skill
                if src.exists():
                    shutil.copytree(src, dst)
            
            # Create README.md
            readme = temp_dir / "README.md"
            readme.write_text(f"""# OpenClaw Skills Collection

精选的 OpenClaw 技能集合。

## 包含的技能

{chr(10).join([f'- **{s}**' for s in skills_to_publish])}

## 使用方法

### 方式 1：直接复制到你的 skills 目录
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/{get_github_owner()}/{repo_name}.git
# 或者 symlink
ln -s {repo_name}/* ./
```

## 许可证

MIT

---
**作者**: {get_github_owner()}  
**创建**: {datetime.now().strftime('%Y-%m-%d')}
""")
        else:
            src = SKILLS_DIR / skill_name
            if not src.exists():
                print(f"❌ Skill '{skill_name}' not found in {SKILLS_DIR}")
                return False
            shutil.copytree(src, temp_dir / skill_name)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Initial commit: {', '.join(skills_to_publish)}"],
            cwd=temp_dir, check=True, capture_output=True
        )
        
        # Create GitHub repo
        visibility = "--public"
        result = subprocess.run(
            ["gh", "repo", "create", repo_name, visibility, "--source=.", "--remote=origin", "--push"],
            cwd=temp_dir, capture_output=True, text=True
        )
        
        if result.returncode == 0:
            repo_url = f"https://github.com/{get_github_owner()}/{repo_name}"
            print(f"✅ Published to {repo_url}")
            return True
        else:
            print(f"❌ Failed to create repo: {result.stderr}")
            return False
            
    finally:
        # Cleanup temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    return False

def publish_to_clawhub(skill_name):
    """Publish skill to ClawHub platform"""
    print(f"🚀 Publishing {skill_name} to ClawHub...")
    
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        print(f"❌ Skill '{skill_name}' not found")
        return False
    
    # Check for .clawhub directory
    clawhub_dir = skill_dir / ".clawhub"
    if not clawhub_dir.exists():
        print(f"⚠️  No .clawhub directory found. Creating...")
        clawhub_dir.mkdir()
        
        # Create origin.json
        origin_json = clawhub_dir / "origin.json"
        origin_json.write_text(json.dumps({
            "author": get_github_owner(),
            "created": datetime.now().isoformat(),
            "version": "1.0.0"
        }, indent=2))
    
    print(f"✅ Skill ready for ClawHub submission")
    print(f"📂 Location: {skill_dir}")
    print(f"🔗 Submit at: https://clawhub.com/submit")
    return True

def main():
    parser = argparse.ArgumentParser(description="Publish OpenClaw skills")
    parser.add_argument("skill", nargs="?", help="Skill name to publish")
    parser.add_argument("--all", action="store_true", help="Publish all skills")
    parser.add_argument("--clawhub", action="store_true", help="Publish to ClawHub instead of GitHub")
    parser.add_argument("--github", action="store_true", help="Publish to GitHub (default)")
    
    args = parser.parse_args()
    
    if not args.skill and not args.all:
        print("Usage: publish.py <skill-name> [--all] [--github] [--clawhub]")
        print("Examples:")
        print("  publish.py stock-price")
        print("  publish.py --all")
        print("  publish.py stock-price --clawhub")
        sys.exit(1)
    
    if args.clawhub:
        if not args.skill:
            print("❌ --clawhub requires a specific skill name")
            sys.exit(1)
        success = publish_to_clawhub(args.skill)
    else:
        # Default to GitHub
        success = publish_to_github(args.skill, args.all)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
