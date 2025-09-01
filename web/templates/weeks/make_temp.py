import toml
with open("../../weeks.toml", 'r') as f:
    weeks_data = toml.load(f)['weeks']

for week in weeks_data:
    out = open(f"{week}.html", 'w') 
    print("""{% extends 'base.html' %}

{% block content %}
<h2>{{ info.title }}</h2>
<p>This is the content for <i>{{ info.title }}</i>, scheduled for {{ info.date }}.</p>
{% endblock %}""", file = out)

    

