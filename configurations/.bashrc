#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ $DISPLAY ]] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
  exec tmux new-session -A -s $HOSTNAME
fi

alias ls='ls --color=auto'
alias grep='grep --color=auto'

alias yay-drop-caches='sudo paccache -rk3; yay -Sc --aur --noconfirm'
alias yay-update-all='export TMPFILE="$(mktemp)"; \
	sudo true; \
	rate-mirrors --entry-country=DE --save=$TMPFILE arch --max-delay=21600 \
	&& sudo mv /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup \
	&& sudo mv $TMPFILE /etc/pacman.d/mirrorlist \
	&& yay-drop-caches \
	&& yay -Syyu --noconfirm'


PS1='[\u@\h \W]\$ '
eval "$(starship init bash)"
