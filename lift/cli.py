import click
import csv
import sys

from lift.models import Session
from lift import core
from lift import util


from datetime import datetime, date, timedelta

formats = util.listing_query_date_formats


@click.group()
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = core.create()


@click.option('-t', '--time', 'duration',
              type=click.DateTime(formats=util.duration_formats),
              default=None)
@click.option('-p', '--rpe', 'effort',
              type=click.IntRange(
                  min=util.rpe_range[0],
                  max=util.rpe_range[1]
              ),
              default=None)
@click.option('-s', '--sets',
              type=click.INT,
              default=None)
@click.option('-r', '--reps', type=click.INT, default=None)
@click.option('-w', '--weight', type=click.FLOAT, default=None)
@click.option('-d', '--date', 'session_date',
              type=click.DateTime())
@click.option('-e', '--exercise', type=str)
@click.option('--today',  default=False, is_flag=True)
@click.option('-i', '--interactive', default=False)
@cli.command()
@click.pass_obj
def log(core, **kwargs):
    interactive = kwargs.pop('interactive', False)
    params = {k: v for k, v in kwargs.items() if v}

    if 'today' in params and 'date' in params:
        raise click.BadParameter('Must specify exactyl one of date and today')

    if 'today' in params:
        params['session_date'] = date.today()
        del params['today']

    if 'exercise' not in params:
        interactive = True
        params['exercise'] = click.prompt(
                'enter an exercise (existing options: {})'.format(
                    ', '.join(core.all_exercises())), str)

    if interactive or ('session_date' not in params
                       or not params['session_date']):
        if (click.prompt(
                "Did you do the workout today?",
                default=False, type=bool
           )):
            params['session_date'] = date.today()
        else:
            params['session_date'] = click.prompt(
                    "When did you do the workout?",
                    type=click.DateTime()
            )

    if interactive and 'sets' not in params:
        reps = click.prompt("sets?", type=int, default=0)
        if reps:
            params['reps'] = reps

    if interactive and 'reps' not in params:
        c = click.prompt("reps per set?", type=int, default=0)
        if c:
            params['reps'] = c

    if interactive and 'duration' not in params:
        c = click.prompt("duration?", type=str, default=0)
        if c:
            params['duration'] = validator(core, "duration", c)

    if interactive and 'failure' not in params:
        c = click.prompt("failure", type=bool, default=False)
        if c:
            params['failure'] = c

    if params.get('duration', None):
        dt = params['duration']
        params['duration'] = timedelta(
                hours=dt.hour,
                minutes=dt.minute,
                seconds=dt.second)

    session = Session(**params)
    if click.confirm('save ' + str(session) + '?"'):
        for result in core.insert(session):
            click.echo(result)
    else:
        click.echo('aborted')


def validator(ctx, param, value):
    if not value:
        return value
    for f in formats:
        try:
            dt = datetime.strptime(value, f)
            return dt
        except ValueError:
            pass

    raise click.BadParameter("date needs to be one of {}".format(formats))


@cli.command()
@click.option(
    '-s', '--start', 'start_date',
    callback=validator,
    type=str
)
@click.option(
    '-e', '--end', 'end_date',
    callback=validator,
    type=str
)
@click.option(
    '-e', '--end', 'end_date',
    callback=validator,
    type=str
)
@click.option(
    '-l', '--limit',
    type=int)
@click.pass_obj
def list(core, start_date, end_date, limit):
    iterable = core.iterate(start_date, end_date, limit)

    writer = csv.DictWriter(
        sys.stdout,
        Session.NAMES,
        delimiter='\t'
     )

    i = 0
    for i, k in enumerate(iterable):
        writer.writerow(k.to_dict())
    else:
        if not i:
            click.echo("No results.")


@cli.command()
@click.pass_obj
def export(core):
    core.export()


def tsvLoad(history):
    with open(history) as history:
        reader = csv.DictReader(history, delimiter='\t')
        for line in reader:
            try:
                yield Session.from_dict(line)
            except (TypeError, ValueError):
                yield Session(**line)


@cli.command()
@click.pass_obj
@click.argument('history')
def load(core, history):
    try:
        sessions = tsvLoad(history)
        core.batch(sessions)
    except (TypeError, ValueError):
        click.echo(
                'tsv headers must be {}'.format(
                    ', '.join(
                        {'{} or {}'.format(h, c)
                            for h, c in Session.NAMES}
                    )
                ), err=True)


if __name__ == '__main__':
    cli()
