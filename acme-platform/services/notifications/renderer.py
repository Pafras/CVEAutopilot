from jinja2 import Environment
from markupsafe import Markup, escape

env = Environment(autoescape=True)

BADGE = env.from_string('<span{{ attrs|xmlattr }}>{{ label }}</span>')


def render_badge(label, attrs):
    return BADGE.render(label=label, attrs=attrs)


def bold(text):
    return Markup("<b>%s</b>") % escape(text)
