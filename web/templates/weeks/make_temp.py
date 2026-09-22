"""Create a placeholder page for any week in weeks.toml that has none.

Run from this directory.  It will NOT touch a page that already exists --
five of these pages have real content, and an earlier version of this script
would have overwritten them.
"""
import os
import toml

with open("../../weeks.toml", encoding="utf-8") as f:
    weeks_data = toml.load(f)["weeks"]

STUB = """{% extends 'base.html' %}

{% block content %}
<h2>{{ info.title }}</h2>
<p>This is the content for <i>{{ info.title }}</i>, scheduled for {{ info.date }}.</p>
{% endblock %}
"""

for week in weeks_data:
    path = f"{week}.html"
    if os.path.exists(path):
        print(f"skipping {path}: already exists")
        continue
    with open(path, "w", encoding="utf-8") as out:
        out.write(STUB)
    print(f"wrote {path}")
