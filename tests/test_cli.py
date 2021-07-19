import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import sys
# from pathlib import Path
# sys.path.insert(0, Path(__file__).parent / "lib")
# print(sys.path)


from click.testing import CliRunner
import lib.bubbletea.cli as cli

def test():
  runner = CliRunner()
  result = runner.invoke(cli.run, args=['aave.py'], catch_exceptions=True, prog_name="bubbletea_test")
  print(result.exit_code)
  assert result.exit_code == 0

# test()
if __name__ == "__main__":
    test()
    print("Everything passed")