#!/usr/bin/env bash
set -euo pipefail

DEFAULT_SUFFIX=".log"

usage() {
  cat >&2 <<USAGE
Usage: $(basename "$0") [-e suffix] DIR

Open the newest file in DIR whose name ends with suffix.
Default suffix: ${DEFAULT_SUFFIX}

Examples:
  $(basename "$0") /path/to/logs
  $(basename "$0") -e .txt /path/to/logs
USAGE
}

suffix="${DEFAULT_SUFFIX}"

while getopts ":e:h" opt; do
  case "${opt}" in
    e)
      suffix="${OPTARG}"
      ;;
    h)
      usage
      exit 0
      ;;
    :)
      printf 'Error: -%s requires an argument.\n' "${OPTARG}" >&2
      usage
      exit 2
      ;;
    \?)
      printf 'Error: unknown option -%s.\n' "${OPTARG}" >&2
      usage
      exit 2
      ;;
  esac
done

shift $((OPTIND - 1))

if [[ "$#" -ne 1 ]]; then
  usage
  exit 2
fi

target_dir="$1"

if [[ ! -d "${target_dir}" ]]; then
  printf 'Error: directory does not exist: %s\n' "${target_dir}" >&2
  exit 1
fi

if [[ -z "${suffix}" ]]; then
  printf 'Error: suffix must not be empty.\n' >&2
  exit 2
fi

printf '[open_latest_log] target directory: %s\n' "${target_dir}" >&2
printf '[open_latest_log] suffix: %s\n' "${suffix}" >&2

matches_file="$(mktemp)"
trap 'rm -f "${matches_file}"' EXIT

find "${target_dir}" -maxdepth 1 -type f -name "*${suffix}" -printf '%T@ %p\n' |
  sort -nr > "${matches_file}"

matched_count="$(wc -l < "${matches_file}")"
printf '[open_latest_log] matched files: %s\n' "${matched_count}" >&2

if [[ "${matched_count}" -gt 0 ]]; then
  printf '[open_latest_log] newest candidates:\n' >&2
  head -n 5 "${matches_file}" | cut -d ' ' -f 2- | sed 's/^/[open_latest_log]   /' >&2
fi

latest_file="$(
  head -n 1 "${matches_file}" |
    cut -d ' ' -f 2-
)"

if [[ -z "${latest_file}" ]]; then
  printf 'No matching files ending with %s in %s\n' "${suffix}" "${target_dir}" >&2
  exit 1
fi

printf '[open_latest_log] selected file: %s\n' "${latest_file}" >&2
printf '[open_latest_log] launching vim\n' >&2
printf 'Opening latest file: %s\n' "${latest_file}"
vim "${latest_file}"
