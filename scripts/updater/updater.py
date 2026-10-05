from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
UPDATER_DIR = Path(__file__).resolve().parent

MANIFEST_PATH = UPDATER_DIR / "manifest.json"
DOWNLOADS_DIR = UPDATER_DIR / "downloads"
BACKUPS_DIR = UPDATER_DIR / "backups"
STAGING_DIR = UPDATER_DIR / "staging"


@dataclass
class UpdateInfo:
    app: str
    channel: str
    version: str
    minimum_supported_version: str
    release_url: str
    package_url: str
    sha256: str
    published_at: str


def load_manifest(
    path: Path = MANIFEST_PATH,
) -> UpdateInfo:
    if not path.exists():
        raise FileNotFoundError(
            f"Manifest not found: {path}"
        )

    raw = path.read_text(
        encoding="utf-8-sig"
    )

    data = json.loads(raw)

    return UpdateInfo(
        app=str(data.get("app", "")),
        channel=str(data.get("channel", "")),
        version=str(data.get("version", "")),
        minimum_supported_version=str(
            data.get(
                "minimum_supported_version",
                "",
            )
        ),
        release_url=str(
            data.get("release_url", "")
        ),
        package_url=str(
            data.get("package_url", "")
        ),
        sha256=str(
            data.get("sha256", "")
        ),
        published_at=str(
            data.get("published_at", "")
        ),
    )


def get_current_version() -> str:
    return load_manifest().version


def parse_version(
    version: str,
) -> tuple[int, ...]:
    cleaned = (
        version
        .strip()
        .lstrip("vV")
    )

    if not cleaned:
        raise ValueError(
            "Version cannot be empty."
        )

    parts = cleaned.split(".")

    result: list[int] = []

    for part in parts:
        if not part.isdigit():
            raise ValueError(
                f"Invalid version: {version}"
            )

        result.append(int(part))

    return tuple(result)


def compare_versions(
    current: str,
    remote: str,
) -> int:
    current_parts = parse_version(current)
    remote_parts = parse_version(remote)

    length = max(
        len(current_parts),
        len(remote_parts),
    )

    current_parts += (0,) * (
        length - len(current_parts)
    )

    remote_parts += (0,) * (
        length - len(remote_parts)
    )

    if current_parts < remote_parts:
        return -1

    if current_parts > remote_parts:
        return 1

    return 0


def is_newer_version(
    current: str,
    remote: str,
) -> bool:
    return (
        compare_versions(
            current,
            remote,
        )
        < 0
    )


def load_remote_manifest(
    url: str,
) -> UpdateInfo:
    if not url.strip():
        raise ValueError(
            "Remote manifest URL is empty."
        )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Boss-AYRA-Updater/0.1"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        raw_data = response.read()

    data = json.loads(
        raw_data.decode("utf-8-sig")
    )

    return UpdateInfo(
        app=str(data.get("app", "")),
        channel=str(data.get("channel", "")),
        version=str(data.get("version", "")),
        minimum_supported_version=str(
            data.get(
                "minimum_supported_version",
                "",
            )
        ),
        release_url=str(
            data.get("release_url", "")
        ),
        package_url=str(
            data.get("package_url", "")
        ),
        sha256=str(
            data.get("sha256", "")
        ),
        published_at=str(
            data.get("published_at", "")
        ),
    )



REMOTE_MANIFEST_URL = (
    "https://raw.githubusercontent.com/"
    "swarjunctionmusic-dev/Boss-AYRA/"
    "master/scripts/updater/manifest.json"
)


def check_for_update() -> bool:
    current = load_manifest()

    remote_url = (
        REMOTE_MANIFEST_URL
        + "?cb="
        + str(int(__import__("time").time()))
    )

    remote = load_remote_manifest(remote_url)

    comparison = compare_versions(
        current.version,
        remote.version,
    )

    print("========================================")
    print("        AYRA UPDATE CHECK")
    print("========================================")
    print(f"Current version : {current.version}")
    print(f"Remote version  : {remote.version}")
    print(f"Channel         : {remote.channel}")

    if comparison < 0:
        print("Status          : UPDATE AVAILABLE")
        print(f"Release         : {remote.release_url}")
        print("========================================")
        return True

    if comparison == 0:
        print("Status          : UP TO DATE")
        print("========================================")
        return False

    print("Status          : CURRENT IS NEWER")
    print("========================================")
    return False


def download_package(
    package_url: str,
    destination: Path,
) -> Path:
    if not package_url.strip():
        raise ValueError(
            "Package URL is empty."
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    request = urllib.request.Request(
        package_url,
        headers={
            "User-Agent":
                "Boss-AYRA-Updater/0.1"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        data = response.read()

    destination.write_bytes(data)

    if destination.stat().st_size == 0:
        raise RuntimeError(
            "Downloaded package is empty."
        )

    return destination


def calculate_sha256(
    file_path: Path,
) -> str:
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def verify_sha256(
    file_path: Path,
    expected_sha256: str,
) -> bool:
    expected = (
        expected_sha256
        .strip()
        .lower()
    )

    if not expected:
        raise ValueError(
            "Expected SHA-256 is empty."
        )

    actual = calculate_sha256(
        file_path
    )

    return actual == expected


def extract_package(
    package_path: Path,
    staging_dir: Path,
) -> Path:
    if not package_path.exists():
        raise FileNotFoundError(
            f"Package not found: {package_path}"
        )

    if not zipfile.is_zipfile(
        package_path
    ):
        raise ValueError(
            "Downloaded package is not a valid ZIP file."
        )

    if staging_dir.exists():
        shutil.rmtree(staging_dir)

    staging_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    package_root = staging_dir.resolve()

    with zipfile.ZipFile(
        package_path,
        "r",
    ) as archive:

        for member in archive.infolist():
            target = (
                staging_dir / member.filename
            ).resolve()

            if (
                target != package_root
                and package_root not in target.parents
            ):
                raise RuntimeError(
                    "Unsafe ZIP path detected: "
                    f"{member.filename}"
                )

        archive.extractall(staging_dir)

    return staging_dir


def backup_directory(
    source_dir: Path,
    backup_dir: Path,
) -> Path:
    if not source_dir.exists():
        raise FileNotFoundError(
            f"Source directory not found: {source_dir}"
        )

    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    backup_dir.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copytree(
        source_dir,
        backup_dir,
    )

    return backup_dir


def rollback_directory(
    backup_dir: Path,
    target_dir: Path,
) -> Path:
    if not backup_dir.exists():
        raise FileNotFoundError(
            f"Backup directory not found: {backup_dir}"
        )

    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copytree(
        backup_dir,
        target_dir,
    )

    return target_dir


def install_staged_update(
    staging_dir: Path,
    target_dir: Path,
) -> Path:
    if not staging_dir.exists():
        raise FileNotFoundError(
            f"Staging directory not found: {staging_dir}"
        )

    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copytree(
        staging_dir,
        target_dir,
    )

    return target_dir


def verify_installed_update(
    target_dir: Path,
    required_files: list[str],
) -> bool:
    if not target_dir.exists():
        return False

    for relative_path in required_files:
        required = (
            target_dir / relative_path
        )

        if not required.is_file():
            return False

    return True


def apply_update(
    package_path: Path,
    expected_sha256: str,
    target_dir: Path,
    backup_dir: Path,
    staging_dir: Path,
    required_files: list[str],
) -> bool:
    print("========================================")
    print("        AYRA UPDATE PIPELINE")
    print("========================================")

    print("[1/6] Verifying package...")

    if not verify_sha256(
        package_path,
        expected_sha256,
    ):
        raise RuntimeError(
            "SHA-256 verification failed."
        )

    print("[1/6] PASS")

    print("[2/6] Extracting to staging...")

    extract_package(
        package_path,
        staging_dir,
    )

    print("[2/6] PASS")

    print("[3/6] Creating backup...")

    backup_directory(
        target_dir,
        backup_dir,
    )

    print("[3/6] PASS")

    try:
        print("[4/6] Installing update...")

        install_staged_update(
            staging_dir,
            target_dir,
        )

        print("[4/6] PASS")

        print("[5/6] Verifying installation...")

        if not verify_installed_update(
            target_dir,
            required_files,
        ):
            raise RuntimeError(
                "Installed update verification failed."
            )

        print("[5/6] PASS")

        print("[6/6] Update successful.")

        return True

    except Exception as exc:
        print(
            f"Update failed: {exc}"
        )

        print(
            "Rolling back..."
        )

        rollback_directory(
            backup_dir,
            target_dir,
        )

        print(
            "Rollback: PASS"
        )

        raise


def print_manifest_status() -> None:
    manifest = load_manifest()

    print(
        "========================================"
    )
    print(
        "        AYRA UPDATER CHECK"
    )
    print(
        "========================================"
    )
    print(
        f"Current version : {manifest.version}"
    )
    print(
        f"Channel         : {manifest.channel}"
    )
    print(
        "Minimum version : "
        f"{manifest.minimum_supported_version}"
    )
    print(
        "Release URL     : "
        f"{manifest.release_url or '(not configured)'}"
    )
    print(
        "Package URL     : "
        f"{manifest.package_url or '(not configured)'}"
    )
    print(
        "SHA-256         : "
        f"{manifest.sha256 or '(not configured)'}"
    )
    print(
        "Published       : "
        f"{manifest.published_at or '(not configured)'}"
    )
    print(
        "========================================"
    )
    print(
        "Manifest check : PASS"
    )


if __name__ == "__main__":
    try:
        check_for_update()

    except Exception as exc:
        print(
            "Update check   : FAIL"
        )
        print(
            f"Error          : {exc}"
        )
        raise
