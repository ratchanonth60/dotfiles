# dotfiles

Personal Linux desktop configuration.

Included:

- `.config/hypr`
- `.config/waybar`
- `.config/walker`
- `.config/eww`
- `.config/cava`
- `.config/fish`
- `.config/fastfetch`

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/ratchanonth60/dotfiles/main/install.sh | bash
```

The installer downloads the repo, backs up existing managed config directories into
`~/.config-backups/dotfiles-*`, and then installs the tracked dotfiles into `~/.config/`.
