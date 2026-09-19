from django import template

register = template.Library()


@register.filter(name="seconds_to_verbose")
def seconds_to_verbose(run_time):
    if not run_time:
        return ""

    seconds = float(run_time)
    minutes = 0
    if seconds > 60:
        minutes = round(int(seconds / 60))
        seconds = round(int(seconds % 60))

    duration = f"{round(seconds)} secs"
    if minutes:
        duration = f"{round(minutes)} min and {duration}"
    return duration
