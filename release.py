import subprocess

# submodules need to be updated, make sure i dont forget
subprocess.run('git add --all', shell=True)

# new version, this makes a git commit and a TAG (triggers docker hub and travisCI builds)
subprocess.run('bumpversion --allow-dirty --tag patch', shell=True)

# TODO: need to set all repos to SSH to use this?
# subprocess.run('git push', shell=True)