import click

from models import Session
from storage import Storage
from os import environ

from datetime import datetime, date, timedelta


CHOICES = ('squat', 'press', 'deadlift', 'stepdowns', 'pullup', 'pushup',
           'snap', 'goalty', 'run', 'trx', 'bike', 'hike', 'cardio')


@click.group()
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = Storage(environ)


@click.option('-d', '--date', 'session_date',
              type=click.DateTime(), prompt=True)
@click.option('-e', '--exercise', type=click.Choice(CHOICES),
              required=True, prompt=True)
@click.option('-s', '--sets', type=click.INT, prompt=True)
@click.option('-r', '--reps', type=click.INT, prompt=True)
@click.option('-w', '--weight', type=click.FLOAT, prompt=True)
@click.option('-t', '--time', 'duration', prompt=True,
              type=click.DateTime(formats=('%H:%M:%S', '%M:%S')), default=None)
@click.option('-p', '--rpe', 'effort', type=click.IntRange(min=1, max=10), prompt=True)
@click.option('--today',  default=False, is_flag=True)
@cli.command()
@click.pass_obj
def add(storage, **kwargs):
    if 'today' in kwargs and kwargs['today'] and 'date' in kwargs:
        raise click.BadParameter('Must specify exactyl one of date and today')

    if 'today' in kwargs and kwargs['today']:
        kwargs['session_date'] = date.today()

    if kwargs['duration']:
        dt = kwargs['duration']
        kwargs['duration'] = timedelta(
                hours=dt.hour,
                minutes=dt.minute,
                seconds=dt.second)

    del kwargs['today']

    session = Session(**kwargs)
    storage.insert(session)
    click.echo(session.to_dict())


formats = ('%Y', '%Y-%M', '%Y-%M-%d')


def validator(ctx, param, value):
    for f in formats:
        try:
            datetime.strptime(value, f)
            return value
        except ValueError:
            pass

    raise click.BadParameter("date needs to be one of {}".format(formats))


@cli.command()
@click.pass_obj
def list(storage):
    for k in storage.iterate():
        click.echo(k)


cli()
