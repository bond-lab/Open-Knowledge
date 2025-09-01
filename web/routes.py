"""Route declaration."""
from flask import current_app as app
from flask import render_template, g
import os
import toml
from datetime import datetime, timedelta


# Load the weeks data from the TOML file
toml_path = os.path.join(app.root_path, 'weeks.toml')
with open(toml_path, 'r') as f:
    weeks_data = toml.load(f)['weeks']

@app.before_request
def before_request():
    # Make weeks_data available in all templates
    g.weeks = weeks_data


    
@app.route('/')
def index():
    # Render the index page with the weeks data
    return render_template('index.html',
                           week='index',
                           weeks=g.weeks)

@app.route('/week/<week_key>/')
def week(week_key):
    if week_key in g.weeks:
        # Pass the data for the specific week to the template
        week_info = weeks_data[week_key]
        return render_template(f'weeks/{week_key}.html',
                               weeks=g.weeks,
                               week=week_key,
                               info=week_info)
    else:
        return "Week not found", 404
