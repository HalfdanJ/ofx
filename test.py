import click
import ofx
from click.testing import CliRunner

def test_ofx():

    runner = CliRunner()

    with runner.isolated_filesystem():

        result = runner.invoke(ofx.cli, ['list'])

        print result.output
        print result.exit_code
        assert result.exit_code == 2

if __name__ == '__main__':
    test_ofx()