import os
import json
import hashlib
import subprocess

repos = [
    "/home/tk/release-Poker44-gen14heur1",
    "/home/tk/release-Poker44-gen14heur2",
    "/home/tk/release-Poker44-gen14heur3"
]

required_files = [
    "models/gen14_profile.json",
    "neurons/miner.py",
    "poker44/base/miner.py",
    "poker44/base/neuron.py",
    "poker44/miner_heuristics.py",
    "poker44/utils/config.py",
    "poker44/utils/misc.py",
    "poker44/utils/model_manifest.py",
    "poker44/validator/synapse.py"
]

def get_head_hash(repo_path):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path).decode().strip()

def compute_sha256(repo_path, files):
    sha = hashlib.sha256()
    for f in files:
        full_path = os.path.join(repo_path, f)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Missing file: {full_path}")
        with open(full_path, "rb") as file_obj:
            sha.update(file_obj.read())
    return sha.hexdigest()

results = []

for repo in repos:
    manifest_path = os.path.join(repo, "models/model_manifest.json")
    try:
        head_hash = get_head_hash(repo)
        
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        manifest["implementation_files"] = required_files
        manifest["repo_commit"] = head_hash
        
        new_sha = compute_sha256(repo, required_files)
        manifest["implementation_sha256"] = new_sha
        
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            f.write('\n')
            
        # Verify
        with open(manifest_path, "r") as f:
            verify_manifest = json.load(f)
        verify_sha = compute_sha256(repo, verify_manifest["implementation_files"])
        verification = "pass" if verify_sha == verify_manifest["implementation_sha256"] else "fail"
        
        # Git operations
        subprocess.check_call(["git", "add", "models/model_manifest.json"], cwd=repo)
        subprocess.check_call(["git", "commit", "-m", "include gen14 profile in implementation files and refresh sha"], cwd=repo)
        subprocess.check_call(["git", "push", "origin", "main"], cwd=repo)
        
        new_head = get_head_hash(repo)
        
        results.append({
            "repo": repo,
            "pushed_commit_hash": new_head,
            "final_sha_prefix": new_sha[:8],
            "verification": verification,
            "first_file": verify_manifest["implementation_files"][0]
        })
    except Exception as e:
        results.append({"repo": repo, "error": str(e)})

print(json.dumps(results, indent=2))
