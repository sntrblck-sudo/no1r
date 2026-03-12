#!/bin/bash
# Simple CLI to review elevation JSONs and move approved ones to exchange/approved/
E_DIR=/home/sntrblck/.openclaw/workspace/exchange/elevations
AP_DIR=/home/sntrblck/.openclaw/workspace/exchange/approved
mkdir -p "$AP_DIR"

for f in "$E_DIR"/*.json; do
  [ -e "$f" ] || continue
  echo
  echo "---- Reviewing: $f ----"
  jq . "$f" || cat "$f"
  echo
  echo "Recommend action? (post/edit/reject/skip)";
  read -r action
  case "$action" in
    post)
      mv "$f" "$AP_DIR/"
      echo "Moved to approved: $AP_DIR/";;
    edit)
      ${EDITOR:-vi} "$f";;
    reject)
      mv "$f" "$E_DIR/rejected/" 2>/dev/null || mkdir -p "$E_DIR/rejected" && mv "$f" "$E_DIR/rejected/";;
    skip)
      echo "Skipped";;
    *)
      echo "Unknown command, skipping";;
  esac
done
echo "All done. Approved files are in $AP_DIR"
