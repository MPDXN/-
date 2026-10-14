#!/usr/bin/env python3
"""Adapt an upstream Jev iOS checkout for an independent Apple developer team.

Inputs contain public identifiers and provisioning profile NAMES only.
No certificates, private keys, or chat content are written to source.
"""
from __future__ import annotations

import argparse
import json
import plistlib
import re
from pathlib import Path


def replace_once(path: Path, before: str, after: str, count: int = 1) -> None:
    original = path.read_text(encoding="utf-8")
    hits = original.count(before)
    if hits != count:
        raise RuntimeError(f"{path}: expected {count} matches, got {hits}: {before[:60]}")
    path.write_text(original.replace(before, after), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--group", required=True)
    parser.add_argument("--app-profile", required=True)
    parser.add_argument("--keyboard-profile", required=True)
    parser.add_argument("--build", type=int, required=True)
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Z0-9]{10}", args.team):
        parser.error("Apple Team ID must be 10 uppercase letters or digits")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*(?:\.[A-Za-z0-9-]+)+", args.bundle):
        parser.error("Invalid reverse-DNS app bundle ID")
    if not re.fullmatch(r"group\.[A-Za-z][A-Za-z0-9-]*(?:\.[A-Za-z0-9-]+)+", args.group):
        parser.error("Invalid App Group ID")
    if args.build < 1 or args.build > 2000000000:
        parser.error("Invalid build number")
    if not args.app_profile.strip() or not args.keyboard_profile.strip():
        parser.error("Provisioning profile names required")

    root = args.source.resolve()
    project = root / "project.yml"
    if not project.is_file():
        parser.error("Source does not contain Jev iOS project.yml")
    replace_once(project, "bundleIdPrefix: com.jevchat",
                 "bundleIdPrefix: " + args.bundle.rsplit(".", 1)[0])
    replace_once(project, "DEVELOPMENT_TEAM: 75LZ93U5CF", "DEVELOPMENT_TEAM: " + args.team)
    replace_once(project, "CODE_SIGN_STYLE: Automatic", "CODE_SIGN_STYLE: Manual")
    replace_once(project, 'CURRENT_PROJECT_VERSION: "2"',
                 'CURRENT_PROJECT_VERSION: "' + str(args.build) + '"')
    for old, new in (
        ("com.jevchat.jarvis.keyboard", args.bundle + ".keyboard"),
        ("com.jevchat.jarvis.uitests", args.bundle + ".uitests"),
        ("com.jevchat.jarvis", args.bundle),
    ):
        replace_once(project, "PRODUCT_BUNDLE_IDENTIFIER: " + old,
                     "PRODUCT_BUNDLE_IDENTIFIER: " + new)
    replace_once(project, "group.com.jevchat.jarvis", args.group, count=2)
    replace_once(project, "CODE_SIGN_ENTITLEMENTS: App/JevJarvis.entitlements",
                 "CODE_SIGN_ENTITLEMENTS: App/JevJarvis.entitlements\n"
                 "        PROVISIONING_PROFILE_SPECIFIER: " + json.dumps(args.app_profile, ensure_ascii=False))
    replace_once(project, "CODE_SIGN_ENTITLEMENTS: Keyboard/JevKeyboard.entitlements",
                 "CODE_SIGN_ENTITLEMENTS: Keyboard/JevKeyboard.entitlements\n"
                 "        PROVISIONING_PROFILE_SPECIFIER: " + json.dumps(args.keyboard_profile, ensure_ascii=False))
    replace_once(project, "CFBundleDisplayName: Jev Jarvis",
                 'CFBundleDisplayName: "翼聊 AI"')
    replace_once(project, "CFBundleDisplayName: Jev 键盘",
                 'CFBundleDisplayName: "翼聊键盘"')

    for rel, before, after in [
        ("App/Info.plist", "<string>Jev Jarvis</string>", "<string>翼聊 AI</string>"),
        ("Keyboard/Info.plist", "<string>Jev 键盘</string>", "<string>翼聊键盘</string>"),
        ("App/JevJarvis.entitlements", "group.com.jevchat.jarvis", args.group),
        ("Keyboard/JevKeyboard.entitlements", "group.com.jevchat.jarvis", args.group),
        ("Shared/JevModel.swift", 'static let appGroupID = "group.com.jevchat.jarvis"',
         'static let appGroupID = "' + args.group + '"'),
    ]:
        replace_once(root / rel, before, after)

    # Required-reason API declaration: shared UserDefaults.
    # Apple App Store Connect privacy disclosure must be reviewed separately.
    privacy = {
        "NSPrivacyAccessedAPITypes": [
            {
                "NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryUserDefaults",
                "NSPrivacyAccessedAPITypeReasons": ["CA92.1"],
            }
        ],
        "NSPrivacyTracking": False,
    }
    for folder in (root / "App/Sources", root / "Keyboard/Sources"):
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / "PrivacyInfo.xcprivacy").open("wb") as f:
            plistlib.dump(privacy, f, fmt=plistlib.FMT_XML)
    print("Prepared independent bundle IDs, App Group, manual signing, privacy manifests.")
    print("No Apple signing or TestFlight upload performed.")


if __name__ == "__main__":
    main()
