set -g fish_greeting

set -gx EDITOR nvim
set -gx VISUAL nvim
set -gx PAGER less
set -gx MANPAGER "sh -c 'col -bx | bat -l man -p'"

set -gx FZF_DEFAULT_COMMAND "fd --type f --hidden --follow --exclude .git"
set -gx FZF_CTRL_T_COMMAND "$FZF_DEFAULT_COMMAND"
set -gx FZF_ALT_C_COMMAND "fd --type d --hidden --follow --exclude .git"

if status is-interactive
    if command -q zoxide
        zoxide init fish | source
    end

    if command -q starship
        starship init fish | source
    end

    if command -q fzf
        fzf --fish | source
    end
end

if command -q eza
    alias ls "eza --group-directories-first --icons=auto"
    alias la "eza -a --group-directories-first --icons=auto"
    alias ll "eza -lah --group-directories-first --icons=auto"
    alias lt "eza --tree --level=2 --group-directories-first --icons=auto"
end

if command -q bat
    alias cat "bat --paging=never --style=plain"
end

abbr -a g git
abbr -a gst "git status -sb"
abbr -a gl "git log --oneline --graph --decorate -20"
abbr -a ga "git add"
abbr -a gc "git commit"
abbr -a gp "git push"
abbr -a ff fastfetch
abbr -a v nvim
abbr -a c clear

function mkcd --description "Create a directory and enter it"
    mkdir -p $argv[1]
    and cd $argv[1]
end
