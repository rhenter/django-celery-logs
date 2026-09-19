import json

from django.forms import Textarea


class PrettyJSONWidget(Textarea):
    def format_value(self, value):
        if value in ("", None):
            return ""

        try:
            if isinstance(value, str):
                value = json.loads(value)
            return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
        except (TypeError, ValueError):
            return super().format_value(value)
