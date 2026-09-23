"""Route declaration."""
from flask import current_app as app
from flask import render_template, g
import os
import toml
from datetime import datetime, timedelta


# The timetable: one source for the site and, via make_dates.py, the slides.
toml_path = os.path.join(app.root_path, 'weeks.toml')
with open(toml_path, 'r') as f:
    course_data = toml.load(f)

# Sorted by date, so the file can list sessions in any order.
weeks_data = dict(sorted(course_data['weeks'].items(),
                         key=lambda item: item[1]['date']))
course_year = course_data.get('year', datetime.now().year)
deadlines_data = course_data.get('deadlines', {})
breaks_data = course_data.get('breaks', [])


def build_schedule() -> list[dict]:
    """Interleave classes and breaks into one date-ordered timetable.

    Returns:
        One dict per row: the week or break itself under 'info', its 'kind'
        ('week' or 'break'), its 'key', and for classes the teaching-week
        'number' (breaks are not numbered).
    """
    rows = [{'kind': 'week', 'key': key, 'info': week}
            for key, week in weeks_data.items()]
    rows += [{'kind': 'break', 'key': b.get('key', ''), 'info': b}
             for b in breaks_data]
    rows.sort(key=lambda row: row['info']['date'])
    number = 0
    for row in rows:
        if row['kind'] == 'week':
            number += 1
            row['number'] = number
    return rows


schedule_data = build_schedule()


@app.template_filter('pretty')
def pretty_date(value: str, style: str = 'long') -> str:
    """Render a weeks.toml date as it should read on the page.

    Args:
        value: A date as "MM-DD" (the course year is assumed) or
            "YYYY-MM-DD" (for deadlines that fall in the next calendar year).
        style: "long" for "13 October", "short" for "13 Oct" (used in the
            timetable, where the column has to stay narrow).

    Returns:
        The formatted date, or the value unchanged if it cannot be parsed, so
        a typo in the TOML shows up on the page rather than breaking the build.
    """
    parts = value.split('-')
    try:
        if len(parts) == 3:
            when = datetime(*(int(p) for p in parts))
        else:
            when = datetime(course_year, *(int(p) for p in parts))
    except (TypeError, ValueError):
        return value
    return f'{when.day} {when:%b}' if style == 'short' else f'{when.day} {when:%B}'


@app.before_request
def before_request():
    # Make the timetable available in all templates
    g.weeks = weeks_data
    g.deadlines = deadlines_data


@app.context_processor
def inject_dates():
    """Give every template the deadlines, as `weeks` is already injected."""
    return {'deadlines': deadlines_data, 'course_year': course_year,
            'schedule': schedule_data}


    
@app.route('/')
def index():
    # Render the index page with the weeks data
    return render_template('index.html',
                           week='index',
                           weeks=g.weeks)

@app.route('/assessment/')
def assessment():
    # The single source of truth for what is due, how it is marked, the
    # citation style, and the rules on using AI.  Week pages link here.
    return render_template('assessment.html',
                           week='assessment',
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
