import hashlib
import json
import pathlib
import subprocess
import os

def get_sha_validator_style(repo_dir, impl_files):
    digest = hashlib.sha256()
    # Validator style: sort relative path strings, update with string then file bytes
    for rel in sorted(impl_files):
        rel_str = str(rel)
        p = pathlib.Path(repo_dir) / rel_str
        digest.update(rel_str.encode("utf-8"))
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    return digest.hexdigest()

repos = [
    "/home/tk/release-Poker44-gen14heur1",
    "/home/tk/release-Poker44-gen14heur2",
    "/home/tk/release-Poker44-gen14heur3"
]

results = []

for repo_dir in repos:
    print(f"\nProcessing {repo_dir}...")
    repo_path = pathlib.Path(repo_dir)
    
    # 1. Edit poker44/utils/model_manifest.py
    utils_path = repo_path / "poker44/utils/model_manifest.py"
    with open(utils_path, "r") as f:
        content = f.read()
    
    # Refined replacement for _sha256_for_files
    # We want it to use repo_root to create relative paths for sorting and hashing keys
    new_func = '''def _sha256_for_files(files: list[Path], repo_root: Path | None = None) -> str:
    """Calculates SHA256 of the given files."""
    hasher = hashlib.sha256()
    
    # Map absolute paths to repo-relative strings if repo_root is provided
    # Otherwise use the filename/path as provided.
    path_map = {}
    for p in files:
        if repo_root and p.is_absolute():
            try:
                rel_str = str(p.relative_to(repo_root))
            except ValueError:
                rel_str = str(p)
        else:
            rel_str = str(p)
        path_map[rel_str] = p

    for rel_str in sorted(path_map.keys()):
        p = path_map[rel_str]
        hasher.update(rel_str.encode("utf-8"))
        with open(p, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
    return hasher.hexdigest()'''

    import re
    # Find the function and replace it
    pattern = r'def _sha256_for_files\(files: list\[Path\]\) -> str:.*?return hasher\.hexdigest\(\)'
    content = re.sub(pattern, new_func, content, flags=re.DOTALL)
    
    # Also need to update the call site in load_from_repo if it exists
    # Or ensure it passes repo_root.
    # Looking at the file content (the previous cat output), let's check the callers.
    
    with open(utils_path, "w") as f:
        f.write(content)
        
    # 2. Update load_from_repo callers to pass repo_root
    with open(utils_path, "r") as f:
        content = f.read()
    
    # Find call to _sha256_for_files(impl_files) and change to _sha256_for_files(impl_files, repo_root=repo_path)
    # Actually in ModelManifest.load_from_repo:
    # sha = _sha256_for_files(impl_files) -> sha = _sha256_for_files(impl_files, repo_root=repo_path)
    content = content.replace('_sha256_for_files(impl_files)', '_sha256_for_files(impl_files, repo_root=repo_path)')
    
    with open(utils_path, "w") as f:
        f.write(content)

    # 3. Verification and Manifest Update
    manifest_path = repo_path / "models" / "model_manifest.json"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    impl_files = manifest["implementation_files"]
    validator_sha = get_sha_validator_style(repo_dir, impl_files)
    
    # Get helper sha using the newly written module
    import sys
    sys.path.insert(0, repo_dir)
    import poker44.utils.model_manifest
    import importlib
    importlib.reload(poker44.utils.model_manifest)
    
    # Prepare Path objects
    from pathlib import Path
    abs_impl_files = [repo_path / f for f in impl_files]
    helper_sha = poker44.utils.model_manifest._sha256_for_files(abs_impl_files, repo_root=repo_path)
    sys.path.remove(repo_dir)
    
    verification = "pass" if validator_sha == helper_sha else "fail"
    
    head_before = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_dir).decode().strip()
    
    # Update manifest
    manifest["implementation_sha256"] = helper_sha
    manifest["repo_commit"] = head_before
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
        
    # 5. Commit and Push
    subprocess.run(["git", "add", "poker44/utils/model_manifest.py", "models/model_manifest.json"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "align dynamic sha computation with validator semantics"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
    
    head_after = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_dir).decode().strip()
    
    results.append({
        "repo": repo_dir,
        "changed_files": ["poker44/utils/model_manifest.py", "models/model_manifest.json"],
        "head_before": head_before,
        "head_after": head_after,
        "helper_sha": helper_sha,
        "validator_sha": validator_sha,
        "verification": verification
    })

print(json.dumps(results, indent=2))
