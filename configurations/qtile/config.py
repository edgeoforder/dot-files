import os
import json
import subprocess
import screeninfo

import libqtile.resources
from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Key, KeyChord,  Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal, send_notification

try:
    import redis

    pool = redis.ConnectionPool(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        db=int(os.environ.get("REDIS_DB", 1)),
        socket_connect_timeout=0.5,  # connect phase
        socket_timeout=0.5,          # read/write phase
        health_check_interval=30,
        )
    r = redis.Redis(connection_pool=pool)
except ImportError:
    r = None
except redis.exceptions.ConnectionError:
    r = None

import widgets.power_supply

monitors_path = os.path.expanduser(os.path.join("~", ".config", "qtile", "monitors.json"))
monitors = json.load(open(monitors_path, "r"))

@hook.subscribe.startup_once
def autostart():
    subprocess.Popen(["autorandr", "-c"])

mod = "mod4"
terminal = guess_terminal()

colors = {
        "dark_black": "#322f2f",
        "grey": "#8d8989",
        "dark_white": "#d5d1d1",
        "medium_red": "#cd6869",
        "light_red": "#ffd9e1",
        "medium_purple": "#b66cac",
        "light_purple": "#f9a8ee",
        "medium_green": "#77c087",
        "light_blue": "#95ceff",
        "medium_blue": "#4d91c7"
        }

theme = {
        "background": colors["dark_black"],
        "foreground": colors["grey"],
        "highlight": colors["dark_white"],
        "notification": colors["medium_blue"],
        "warning": colors["light_blue"],
        "failure": colors["medium_red"],
        "success": colors["medium_green"],
        }

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawn("rofi -show run"), desc="Spawn a command using a prompt widget"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


characters_subscript = ["<sub>h</sub>", "<sub>j</sub>", "<sub>k</sub>", "<sub>l</sub>"]
characters = ["h", "j", "k", "l"]
monitor_symbol = "󰍹 "
group_symbol = "●"
groups = []
for i, monitor in enumerate(sorted(monitors, key=lambda monitor: monitor["position"]["x"])):
    groups += [
            Group(
                str(j),
                label=f"{group_symbol}{characters_subscript[(j - 1) % len(characters_subscript)]}",
                ) for j in range(1 + i * len(characters_subscript), len(characters_subscript) + 1 + i * len(characters_subscript), )
            ]
@hook.subscribe.startup_complete
def send_to_screens():
    for i in range(len(monitors)):
        for j in range(1 + i * len(characters_subscript), len(characters_subscript) + i * len(characters_subscript) + 1):
            qtile.groups_map(str(j)).toscreen(i)
        qtile.groups_map[str(1 + i * len(characters_subscript))].toscreen(i)


group_chords = []
group_chords_move = []
for i, monitor in enumerate(sorted(monitors, key=lambda monitor: monitor["position"]["x"])):
    tmp = []
    tmp_move = []
    for j in range(1 + i * len(characters_subscript), len(characters_subscript) + 1 + i * len(characters_subscript)):
        tmp.append(
                Key(
                    [],
                    characters[(j - 1) % len(characters_subscript)],
                    lazy.group[str(j)].toscreen(i),
                    desc=f"switch to group {j} on monitor {characters[i]}"
                    )
                )
        tmp_move.append(
                Key(
                    [],
                    characters[(j - 1) % len(characters_subscript)],
                    lazy.window.togroup(str(j), switch_group=False),
                    desc=f"move focused window to group {j} on monitor {characters[i]}"
                    )
                )
        group_chords.append(
                KeyChord([], characters[i], tmp, name=f"switch group on screen {characters[i]}")
                )
        group_chords_move.append(
                KeyChord([], characters[i], tmp_move, name=f"move focused window to screen {characters[i]}")
                )

tmp_focus = []
for i, monitor in enumerate(sorted(monitors, key=lambda monitor: monitor["position"]["x"])):
    tmp_focus.append(
            Key(
                [],
                characters[i],
                lazy.to_screen(i),
                desc=f"move to screen {characters[i]}"
                )
            )

keys.extend(
        [
            KeyChord(
                [mod],
                "d",
                tmp_focus,
                name="move to screen",
                desc="move to screen",
                )
            ]
        )

keys.extend(
        [
            KeyChord(
                [mod],
                "f",
                group_chords,
                name="switch to group",
                desc="switch to group",
                )
            ]
        )

keys.extend(
        [
            KeyChord(
                [mod],
                "g",
                group_chords_move,
                name="move window to group",
                desc="move window to group",
                )
            ]
        )

layouts = [
    layout.Columns(
        border_width=0,
        margin=[10, 10, 20, 10],
        initial_ratio=16/9),
    layout.Max(
        border_width=0,
        margin=[10, 10, 20, 10]),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

extensions_default = dict(
    font="sans",
    fontsize=12,
    padding=3,
)

logo = None # os.path.join(os.path.dirname(libqtile.resources.__file__), "logo.png")

screens = []
for i, monitor in enumerate(sorted(monitors, key=lambda monitor: monitor["position"]["x"])):
    monitor_width_mm = monitor["physical_size"]["width"]
    monitor_height_mm = monitor["physical_size"]["height"]
    for mode in monitor["modes"]:
        if mode["current"]:
            monitor_width_px = mode["width"]
            monitor_height_px = mode["height"]
    monitor_diagonal_mm = (monitor_width_mm ** 2 + monitor_height_mm ** 2) ** 0.5
    monitor_diagonal_px = (monitor_width_px ** 2 + monitor_height_px ** 2) ** 0.5
    dpi = monitor_diagonal_px / (monitor_diagonal_mm / 25.4)
    font_size = round(dpi / 10)
    widget_defaults = dict(
            foreground=theme["foreground"],
            font="OverpassM Nerd Font",
            fontsize=round(dpi / 10),
            padding=round(dpi / 30),
            )
    screen = Screen(
        top=bar.Bar(
            [
                widget.TextBox(f"{monitor_symbol}{characters_subscript[i % len(characters_subscript)]}"),
                widget.GroupBox(markup=True, hide_unused=False, highlight_method="text", urgent_alert_method="text", this_current_screen_border=theme["notification"], active=theme["highlight"], inactive=theme["foreground"], urgent_text=theme["warning"], urgent_border=theme["warning"], visible_groups=list(map(str, range(1 + i * len(characters_subscript), len(characters_subscript) + 1 + i * len(characters_subscript))))),
                widget.TaskList(
                    icon_size=0,
                    highlight_method="block",
                    borderwidth=0,
                    border=theme["notification"],
                    urgent_border=theme["warning"],
                    markup_focused="<span foreground='" + theme["background"] + "'>{}</span>",
                    padding_x=round(dpi / 10),
                    padding_y=round(dpi / 20),
                ),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widgets.power_supply.WidgetPowerSupply(
                    r=r,
                    warning_color=theme["warning"],
                ),
                widget.Clock(format="%Y-%m-%d %a %H:%M:%S"),
            ],
            round(dpi / 2),
            background=theme["background"],
            margin=[0, 0, 0, 0],
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
        background=theme["background"],
        wallpaper=logo,
        wallpaper_mode="center",
    )
    screens.append(screen)

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = True
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
focus_previous_on_window_remove = False
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
# wl_input_rules = {
#         "type:keyboard": InputConfig(
#             kb_layout="de",
#             kb_variant="nodeadkeys",
#             kb_options="caps:escape"
#             )
#         }

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

idle_inhibitors = []  # type: list

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
