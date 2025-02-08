import os
import requests


def check_for_updates():
    if not os.path.exists(".git/"):
        print(".git directory not found, could not check for updates.")
    else:
        print("Checking for updates...")

    # Get local commit hash
    f = open(".git/logs/HEAD", "r")
    local_log = f.read().strip().split("\n")
    f.close()

    local_hash = local_log[-1].split(" ")

    # Get remote commit hash
    url = "https://api.github.com/repos/Mihaugoku/fg-input-visualizer/commits/master"
    req = requests.get(url).json()

    remote_hash = req["sha"]

    update_str = ""

    if local_hash[1] != remote_hash:
        update_str = f"A new version is available! {local_hash[0][:7]} -> {remote_hash[:7]}\nGo to https://github.com/Mihaugoku/fg-input-visualizer to download."
        update_len = max([len(x) for x in update_str.split('\n')])
    else:
        update_str = "You are up to date."
        update_len = len(update_str)

    print(f"{'=' * update_len}\n{update_str}\n{'=' * update_len}\n")
