#!/bin/bash
set -euo pipefail

echo "🧹 Cleaning old generated OWNERS files"
rm -rf local-output
mkdir local-output

repos=$(python3 scripts/get_changed_repos.py previous.yaml config/access-control.yaml | jq -r '.[]')

if [ -z "$repos" ]; then
    echo "✅ No changes detected. Nothing to generate."
    exit 0
fi

for repo in $repos; do
    echo "🔵 Generating OWNERS for $repo..."

    mkdir -p local-output/$repo
    (
      cd local-output/$repo
      python3 ../../scripts/generate_owners.py "$repo"
    )

    echo "📄 Generated OWNERS file for $repo:"
    cat local-output/$repo/OWNERS
    echo "--------------------------------"
done

echo "🎉 Local test completed!"
