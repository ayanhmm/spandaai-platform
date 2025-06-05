#!/bin/bash
echo "🧹 Cleaning up debug and inventory logs..."
find . -type f \( -name "git_debug_*" -o -name "git_inventory_*" \) -exec rm -v {} \;

