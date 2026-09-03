#!/bin/sh
# Called by the collector as: notify <filename> <summary>
#
# The oven cannot tell anyone anything during a run -- the radio may not be
# up while a profile is running, because an SPI call can block for 227 ms
# against a 250 ms control deadline. So notification happens when the run
# is handed over afterwards, which is the earliest moment it can.
#
# Point this at whatever you actually read. Three that need no account:
#
#   ntfy.sh:   curl -d "$2" ntfy.sh/your-topic-name
#   email:     printf '%s\n' "$2" | mail -s "oven: $1" you@example.com
#   a file:    the default below, which is at least greppable
#
# A summary looks like:
#   SAC305 (this oven) | 2026-09-03T01-19-09Z | peak=236.4 tal=97 | 1149 rows
# and a run that faulted will say so, because faults are in the log.

set -eu
NAME="${1:-unknown}"
SUMMARY="${2:-no summary}"

case "$SUMMARY" in
  *FAILED*|*fault*) URGENCY="CHECK THIS" ;;
  *)                URGENCY="ok" ;;
esac

printf '%s  [%s]  %s  %s\n' \
  "$(date '+%Y-%m-%d %H:%M:%S')" "$URGENCY" "$NAME" "$SUMMARY" \
  >> "${OVEN_NOTIFY_LOG:-$HOME/oven-notifications.log}"
