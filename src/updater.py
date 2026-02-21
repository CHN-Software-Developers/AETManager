import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile

RELEASE_API_URL = "https://api.github.com/repos/CHN-Software-Developers/AETManager/releases/latest"
HTTP_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "AETManager-Updater",
}


def _version_tuple(version_text):
    normalized = version_text.strip().lstrip("vV")
    if not normalized:
        return (0,)

    parts = []
    for part in normalized.split("."):
        digits = ""
        for char in part:
            if char.isdigit():
                digits += char
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts) if parts else (0,)


def _is_newer_version(remote_version, current_version):
    remote = _version_tuple(remote_version)
    current = _version_tuple(current_version)
    width = max(len(remote), len(current))
    remote = remote + (0,) * (width - len(remote))
    current = current + (0,) * (width - len(current))
    return remote > current


def _load_latest_release():
    request = urllib.request.Request(RELEASE_API_URL, headers=HTTP_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise RuntimeError(f"Release query failed with HTTP {error.code}.") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Release query failed: {error.reason}.") from error

    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError("Release query returned invalid JSON.") from error


def _copy_release_files(zipball_url, app_dir):
    request = urllib.request.Request(zipball_url, headers=HTTP_HEADERS)
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = os.path.join(temp_dir, "release.zip")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(archive_path, "wb") as archive_file:
                    archive_file.write(response.read())
        except urllib.error.URLError as error:
            raise RuntimeError(f"Release download failed: {error.reason}.") from error

        try:
            with zipfile.ZipFile(archive_path, "r") as release_zip:
                release_zip.extractall(temp_dir)
        except zipfile.BadZipFile as error:
            raise RuntimeError("Downloaded release archive is invalid.") from error

        extracted_dirs = sorted([entry.path for entry in os.scandir(temp_dir) if entry.is_dir()])
        if not extracted_dirs:
            raise RuntimeError("Downloaded release archive is empty.")

        release_root = extracted_dirs[0]
        release_src_dir = os.path.join(release_root, "src")
        release_license = os.path.join(release_root, "LICENSE.txt")

        if not os.path.isdir(release_src_dir):
            raise RuntimeError("Release archive does not contain a src directory.")
        if not os.path.isfile(release_license):
            raise RuntimeError("Release archive does not contain LICENSE.txt.")

        for item_name in os.listdir(release_src_dir):
            source_path = os.path.join(release_src_dir, item_name)
            target_path = os.path.join(app_dir, item_name)
            if os.path.isdir(source_path):
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)

        shutil.copy2(release_license, os.path.join(app_dir, "LICENSE.txt"))


def auto_update_if_available(current_version, app_dir):
    if not os.path.isfile(os.path.join(app_dir, "LICENSE.txt")):
        return False

    try:
        release = _load_latest_release()
    except RuntimeError as error:
        print(f"Update check skipped: {error}")
        return False

    if not release:
        return False

    release_tag = str(release.get("tag_name", "")).strip()
    zipball_url = str(release.get("zipball_url", "")).strip()

    if not release_tag or not zipball_url:
        return False
    if not _is_newer_version(release_tag, current_version):
        return False

    try:
        _copy_release_files(zipball_url, app_dir)
    except (RuntimeError, OSError) as error:
        print(f"Auto-update failed: {error}")
        return False

    print(f"Updated AETManager to {release_tag.lstrip('vV')}. Restarting...")
    return True
