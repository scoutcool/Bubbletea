import click
import os


@click.command()
@click.argument("target", required=True)
def main(target):
    pass
    # click.echo(f'RUNNING STREAM LIT {target}')
    # os.system(f'streamlit run {target}')

@click.command()
@click.argument("target", required=True)
def run(target):
    click.echo(f'RUNNING STREAM LIT {target}')
    os.system(f'streamlit run {target}')


if __name__ == '__main__':
    main()