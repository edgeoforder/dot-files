import screeninfo
import subprocess
import json


def read_monitor_infos():
    monitors = {}
    for monitor in screeninfo.get_monitors():
        diagonal = (monitor.width ** 2 + monitor.height ** 2) ** 0.5
        diagonal_mm = (monitor.width_mm ** 2 + monitor.height_mm ** 2) ** 0.5
        monitors[monitor.name] = {
                "width": monitor.width,
                "height": monitor.height,
                "diagonal": round(diagonal),
                "dpi": round(diagonal / diagonal_mm * 25.4),
                "is_primary": monitor.is_primary,
                }
    return monitora

def read_monitor_infos_wayland():
    output = subprocess.run(
            ["wlr-randr", "--json"],
            capture_output=True,
            text=True,
            check=True,
            )
    monitors = json.loads(output.stdout)

    return monitors



if __name__ == "__main__":
    print(read_monitor_infos_wayland())
