#!/bin/bash
# Builds an ad-hoc signed Release Frost.app and packages it as Frost.zip.
# Used by both the Build and Release workflows.
#
# Usage: Scripts/build.sh [output-dir]   (default: build)
set -euo pipefail

out="${1:-build}"
app="$out/Build/Products/Release/Frost.app"

# Ad-hoc signed (no team). The hardened runtime is disabled because, with an
# ad-hoc signature, its library validation rejects Sparkle.framework on a
# normal Mac and the app aborts at launch. It's only needed for notarization,
# which ad-hoc builds can't get anyway.
status=0
xcodebuild build \
    -project Ice.xcodeproj \
    -scheme Ice \
    -configuration Release \
    -destination "generic/platform=macOS" \
    -derivedDataPath "$out" \
    -skipPackagePluginValidation \
    -skipMacroValidation \
    CODE_SIGN_IDENTITY="-" \
    CODE_SIGN_STYLE=Manual \
    DEVELOPMENT_TEAM="" \
    ENABLE_HARDENED_RUNTIME=NO \
    > build.log 2>&1 || status=$?
grep -E "error:|BUILD (SUCCEEDED|FAILED)" build.log || true
if [ "$status" -ne 0 ]; then
    grep -E -B2 -A6 "error:" build.log | head -300 || tail -200 build.log
    exit "$status"
fi

codesign --verify --deep --verbose=2 "$app"

# GitHub's macOS runners have SIP disabled, so library validation isn't
# enforced there and a launch test can't catch this. Check the flags directly.
flags=$(codesign -dv "$app" 2>&1 | grep -E "flags")
echo "$flags"
if grep -q "adhoc" <<<"$flags" && grep -q "runtime" <<<"$flags"; then
    echo "::error::Ad-hoc signed with the hardened runtime; dyld will refuse to load Sparkle.framework"
    exit 1
fi

ditto -c -k --keepParent "$app" Frost.zip
echo "Built $app and Frost.zip"
