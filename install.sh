#!/usr/bin/env bash
set -Eeuo pipefail

readonly REPOSITORY="fexapk/redact"
readonly VERSION="${REDACT_VERSION:-v0.1.0}"
readonly INSTALL_ROOT="${REDACT_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/redact}"
readonly BIN_DIR="${REDACT_BIN_DIR:-${XDG_BIN_HOME:-$HOME/.local/bin}}"
readonly ARCHIVE_NAME="redact-${VERSION}.tar.gz"
readonly RELEASE_URL="https://github.com/${REPOSITORY}/releases/download/${VERSION}"

die() {
    printf 'redact installer: %s\n' "$*" >&2
    exit 1
}

[[ "$(uname -s)" == "Linux" ]] || die "Linux is required."
[[ "$(uname -m)" == "x86_64" ]] || die "64-bit x86 Linux is required."
[[ -f /etc/debian_version ]] || die "a Debian-based Linux distribution is required."
command -v apt-get >/dev/null 2>&1 || die "apt-get is required."
command -v dpkg-query >/dev/null 2>&1 || die "dpkg is required."

missing_packages=()
for package in python3 python3-venv python3-pip curl ca-certificates; do
    if ! dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q 'install ok installed'; then
        missing_packages+=("$package")
    fi
done

if ((${#missing_packages[@]})); then
    if [[ "$(id -u)" -eq 0 ]]; then
        apt_get=(apt-get)
    elif command -v sudo >/dev/null 2>&1; then
        apt_get=(sudo apt-get)
    else
        die "missing packages: ${missing_packages[*]}; install sudo or run apt-get as an administrator."
    fi
    printf 'Installing system packages: %s\n' "${missing_packages[*]}"
    "${apt_get[@]}" update
    "${apt_get[@]}" install -y "${missing_packages[@]}"
fi

command -v python3 >/dev/null 2>&1 || die "python3 is unavailable after installation."
python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' ||
    die "Python 3.11 or newer is required."

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
archive="$tmp_dir/$ARCHIVE_NAME"
checksum="$tmp_dir/$ARCHIVE_NAME.sha256"

curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
    "$RELEASE_URL/$ARCHIVE_NAME" --output "$archive" ||
    die "could not download release $VERSION."
curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
    "$RELEASE_URL/$ARCHIVE_NAME.sha256" --output "$checksum" ||
    die "could not download the release checksum."
(cd "$tmp_dir" && sha256sum --check "$(basename "$checksum")") ||
    die "release checksum verification failed."

extract_dir="$tmp_dir/extracted"
mkdir -p "$extract_dir"
tar -xzf "$archive" -C "$extract_dir"
# Release archives are created with the matching "redact-${VERSION}/" prefix.
source_dir="$extract_dir/redact-${VERSION}"
[[ -f "$source_dir/pyproject.toml" ]] || die "release archive is missing pyproject.toml."

target_dir="$INSTALL_ROOT/$VERSION"
mkdir -p "$INSTALL_ROOT" "$BIN_DIR"
rm -rf "$target_dir"
python3 -m venv "$target_dir/.venv"
"$target_dir/.venv/bin/python" -m pip install --disable-pip-version-check "$source_dir"

cat > "$BIN_DIR/redact" <<EOF
#!/usr/bin/env bash
exec "$target_dir/.venv/bin/python" -m redact_app "\$@"
EOF
chmod 755 "$BIN_DIR/redact"

printf 'Redact %s installed. Run: %s/redact\n' "$VERSION" "$BIN_DIR"
[[ ":$PATH:" == *":$BIN_DIR:"* ]] ||
    printf 'Add %s to PATH to run `redact` directly.\n' "$BIN_DIR"
