#!/usr/bin/env bash

set -euo pipefail

OWNER="${DOTFILES_OWNER:-ratchanonth60}"
REPO="${DOTFILES_REPO:-dotfiles}"
BRANCH="${DOTFILES_BRANCH:-main}"
BACKUP_ROOT="${HOME}/.config-backups/dotfiles-$(date +%Y%m%d-%H%M%S)"
TMP_DIR=""

cleanup() {
  if [[ -n "${TMP_DIR}" && -d "${TMP_DIR}" ]]; then
    rm -rf "${TMP_DIR}"
  fi
}

trap cleanup EXIT

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

need_cmd curl
need_cmd tar
need_cmd mktemp

TMP_DIR="$(mktemp -d)"
ARCHIVE_URL="https://github.com/${OWNER}/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"
ARCHIVE_PATH="${TMP_DIR}/dotfiles.tar.gz"

echo "Downloading ${OWNER}/${REPO}@${BRANCH}..."
curl -fsSL "${ARCHIVE_URL}" -o "${ARCHIVE_PATH}"
tar -xzf "${ARCHIVE_PATH}" -C "${TMP_DIR}"

SOURCE_DIR="$(find "${TMP_DIR}" -mindepth 1 -maxdepth 1 -type d -name "${REPO}-*" | head -n 1)"
if [[ -z "${SOURCE_DIR}" || ! -d "${SOURCE_DIR}/.config" ]]; then
  echo "Failed to unpack dotfiles archive." >&2
  exit 1
fi

mkdir -p "${HOME}/.config"

backup_path() {
  local target="$1"
  local relative="${target#"${HOME}/"}"
  local destination="${BACKUP_ROOT}/${relative}"
  mkdir -p "$(dirname "${destination}")"
  cp -a "${target}" "${destination}"
}

install_dir() {
  local source="$1"
  local name
  name="$(basename "${source}")"
  local target="${HOME}/.config/${name}"

  if [[ -e "${target}" ]]; then
    backup_path "${target}"
    rm -rf "${target}"
  fi

  cp -a "${source}" "${target}"
}

for source in "${SOURCE_DIR}"/.config/*; do
  [[ -d "${source}" ]] || continue
  install_dir "${source}"
done

find "${HOME}/.config/waybar/scripts" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} +
[[ -f "${HOME}/.config/eww/start-hud.sh" ]] && chmod +x "${HOME}/.config/eww/start-hud.sh"
[[ -f "${HOME}/.config/eww/stop-hud.sh" ]] && chmod +x "${HOME}/.config/eww/stop-hud.sh"

echo
echo "Installed dotfiles into ${HOME}/.config"
if [[ -d "${BACKUP_ROOT}" ]]; then
  echo "Backup saved to ${BACKUP_ROOT}"
fi
echo
echo "Suggested next steps:"
echo "  hyprctl reload"
echo "  omarchy restart waybar"
