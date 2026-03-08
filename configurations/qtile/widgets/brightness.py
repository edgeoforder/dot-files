import json

import libqtile.widget.base


class WidgetBrightness(libqtile.widget.base.BackgroundPoll):
    def __init__(self, r, target_value=None, highlight_color="#00FF00", warning_color="#ff0000", **config):
        libqtile.widget.base.InLoopPollText.__init__(self, **config)
        self.r = r

        self.target_value = target_value
        self.warning_color = warning_color
        self.highlight_color = highlight_color

    def poll(self):
        if self.r is None:
            return ""
        data = self.r.xrevrange("brightness", count=1)
        try:
            eid, payload = data[-1]
        except IndexError:
            return ""
        measurement = json.loads(payload.get(b"measurement").decode("utf-8"))

        if self.target_value is not None:
            if self.target_value != measurement["current"]:
                return f"<span color='{self.warning_color}'>󰃠</span>"
            else:
                return f"<span color='{self.highlight_color}'>󰃠</span>"
        else:
            return "/".join([str(measurement["current"]), str(measurement["max"])])

