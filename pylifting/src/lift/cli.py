import click

from models import Session
from storage import Storage
from os import environ

from datetime import datetime, date, timedelta, MINYEAR, MAXYEAR


CHOICES = ('squat', 'press', 'deadlift', 'stepdowns', 'pullup', 'pushup',
           'snap', 'goalty', 'run', 'trx', 'bike', 'hike', 'cardio')


@click.group()
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = Storage(environ)
    CHOICES = ctx.obj.all_exercises()


@click.option('-t', '--time', 'duration',
              type=click.DateTime(formats=('%H:%M:%S', '%M:%S')), default=None)
@click.option('-p', '--rpe', 'effort', type=click.IntRange(min=1, max=10), default=None)
@click.option('-s', '--sets', type=click.INT, default=None)
@click.option('-r', '--reps', type=click.INT, default=None)
@click.option('-w', '--weight', type=click.FLOAT, default=None)
@click.option('-d', '--date', 'session_date',
              type=click.DateTime())
@click.argument('exercise', type=click.Choice(CHOICES), required=True)
@click.option('--today',  default=False, is_flag=True)
@cli.command()
@click.pass_obj
def add(storage, **kwargs):
    params = {k: v for k, v in kwargs.items() if v}

    if 'today' in params and 'date' in params:
        raise click.BadParameter('Must specify exactyl one of date and today')

    if 'today' in params:
        params['session_date'] = date.today()
        del params['today']

    if 'session_date' not in params or not params['session_date']:
        raise click.BadParameter('Must specify exactyl one of date and today')

    if params.get('duration', None):
        dt = params['duration']
        params['duration'] = timedelta(
                hours=dt.hour,
                minutes=dt.minute,
                seconds=dt.second)


    session = Session(**params)
    if click.confirm('save ' + str(session) + '?"'):
        storage.insert(session)
    else:
        click.echo('aborted')


formats = ('%Y', '%Y-%m', '%Y-%m-%d')


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
def list(storage, start_date, end_date, limit):
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date


    done = False
    for i, k in enumerate(storage.iterate(**params)):
        if done:
            return
        if (limit and i == limit):
            done = True
        click.echo(k)
        click.echo


if __name__ == '__main__':
    cli()
