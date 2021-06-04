import click
import os


@click.command()
@click.argument("target", required=True)
def main(target):
    click.echo(f'RUNNING STREAM LIT {target}')
    raise ValueError('The graph query must have one and only definition.')
    # os.system(f'streamlit run {target}')

if __name__ == '__main__':
    main()