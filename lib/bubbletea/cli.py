import click
import os


@click.group()
def main():
    pass
    # click.echo(f'RUNNING STREAM LIT {target}')
    # os.system(f'streamlit run {target}')

@click.command()
@click.argument("target", required=True)
def run(target):
    # click.echo(f'RUNNING STREAMLIT {target}')
    os.system(f'streamlit run {target}')
    # cli._main_run()


if __name__ == '__main__':
    run()