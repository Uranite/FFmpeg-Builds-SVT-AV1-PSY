import os
import sys
import asyncio
import re
import glob
from pathlib import Path
import tempfile
import shutil
from typing import Optional, Dict, List

async def run_command(cmd: List[str], cwd: Optional[str] = None) -> Optional[str]:
    """Run a command asynchronously and return its output."""
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            print(f"Error running command {' '.join(cmd)}: {stderr.decode()}")
            return None
            
        return stdout.decode().strip()
    except Exception as e:
        print(f"Error running command {' '.join(cmd)}: {e}")
        return None

async def get_git_default_branch(repo_url: str) -> Optional[str]:
    """Get the default branch name for a git repository."""
    try:
        output = await run_command(['git', 'remote', 'show', repo_url])
        if output:
            for line in output.splitlines():
                if "HEAD branch:" in line:
                    return line.split(":", 1)[1].strip()
    except Exception as e:
        print(f"Error getting default branch: {e}")
    return None

async def check_svn_repo(repo: str, current_rev: str) -> Optional[str]:
    """Check SVN repository for updates."""
    print(f"Checking svn rev for {repo}...")
    cmd = ['svn', '--non-interactive', 'info',
           '--username', 'anonymous', '--password', '', repo]
    output = await run_command(cmd)
    
    if output:
        for line in output.splitlines():
            if line.startswith('Revision:'):
                new_rev = line.split()[1].strip()
                if new_rev != current_rev:
                    return new_rev
    return None

async def check_hg_repo(repo: str, current_hgrev: str) -> Optional[str]:
    """Check Mercurial repository for updates."""
    print(f"Checking hg rev for {repo}...")
    async with tempfile.TemporaryDirectory() as tmphgrepo:
        await run_command(['hg', 'init'], cwd=tmphgrepo)
        output = await run_command(
            ['hg', 'in', '-f', '-n', '-l', '1', repo],
            cwd=tmphgrepo
        )
        
        if output:
            for line in output.splitlines():
                if 'changeset' in line:
                    new_hgrev = line.split(':')[2].strip()
                    if new_hgrev != current_hgrev:
                        return new_hgrev
    return None

async def check_git_repo(
    repo: str,
    current_commit: str,
    current_branch: Optional[str],
    current_tagfilter: Optional[str]
) -> Optional[str]:
    """Check Git repository for updates."""
    if current_tagfilter:
        cmd = ['git', 'ls-remote', '--exit-code', '--tags', '--refs',
               '--sort=v:refname', repo, f'refs/tags/{current_tagfilter}']
        output = await run_command(cmd)
        if output:
            return output.splitlines()[-1].split('/')[2].strip()
    else:
        if not current_branch:
            current_branch = await get_git_default_branch(repo)
            if current_branch:
                print(f"Found default branch {current_branch}")
            
        if current_branch:
            cmd = ['git', 'ls-remote', '--exit-code', '--heads', '--refs',
                  repo, f'refs/heads/{current_branch}']
            output = await run_command(cmd)
            if output:
                new_commit = output.split()[0]
                if new_commit != current_commit:
                    return new_commit
    return None

async def update_script(script_path: str):
    """Process and update a single script file asynchronously."""
    print(f"Processing {script_path}")
    
    # Read the script content
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Extract variables from the script
    script_vars = {}
    for line in content.splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            script_vars[key.strip()] = value.strip().strip('"\'')
    
    if script_vars.get('SCRIPT_SKIP'):
        return
    
    # Process multiple repository configurations
    content_modified = False
    
    for i in [''] + list(range(2, 10)):
        suffix = str(i) if i else ''
        repo_var = f'SCRIPT_REPO{suffix}'
        commit_var = f'SCRIPT_COMMIT{suffix}'
        rev_var = f'SCRIPT_REV{suffix}'
        hgrev_var = f'SCRIPT_HGREV{suffix}'
        branch_var = f'SCRIPT_BRANCH{suffix}'
        tagfilter_var = f'SCRIPT_TAGFILTER{suffix}'
        
        repo = script_vars.get(repo_var)
        if not repo:
            if not suffix:  # First iteration with no suffix
                with open(script_path, 'a') as f:
                    f.write("\nxxx_CHECKME_xxx\n")
                print("Needs manual check.")
            break
        
        current_commit = script_vars.get(commit_var)
        current_rev = script_vars.get(rev_var)
        current_hgrev = script_vars.get(hgrev_var)
        current_branch = script_vars.get(branch_var)
        current_tagfilter = script_vars.get(tagfilter_var)
        
        # Check repository based on type
        new_value = None
        
        if current_rev:
            new_value = await check_svn_repo(repo, current_rev)
            if new_value:
                content = re.sub(
                    f'{rev_var}=.*',
                    f'{rev_var}="{new_value}"',
                    content,
                    flags=re.MULTILINE
                )
                content_modified = True
                
        elif current_hgrev:
            new_value = await check_hg_repo(repo, current_hgrev)
            if new_value:
                content = re.sub(
                    f'{hgrev_var}=.*',
                    f'{hgrev_var}="{new_value}"',
                    content,
                    flags=re.MULTILINE
                )
                content_modified = True
                
        elif current_commit:
            new_value = await check_git_repo(
                repo, current_commit, current_branch, current_tagfilter
            )
            if new_value:
                content = re.sub(
                    f'{commit_var}=.*',
                    f'{commit_var}="{new_value}"',
                    content,
                    flags=re.MULTILINE
                )
                content_modified = True
                
        else:
            # Unknown repository type
            with open(script_path, 'a') as f:
                f.write("\nxxx_CHECKME_UNKNOWN_xxx\n")
            print("Unknown layout. Needs manual check.")
            break
    
    # Write updated content back to file if modified
    if content_modified:
        print(f"Updating {script_path}")
        with open(script_path, 'w') as f:
            f.write(content)
    print()

async def main():
    # Change to the parent directory of the script
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Set locale to C
    os.environ['LC_ALL'] = 'C'
    
    # Get all script paths
    script_paths = glob.glob('scripts.d/**/*.sh', recursive=True)
    
    # Process all scripts concurrently
    await asyncio.gather(*[update_script(path) for path in script_paths])

if __name__ == '__main__':
    asyncio.run(main())
