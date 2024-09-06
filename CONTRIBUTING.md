## Installation for Local Development

The package is built using the [Poetry](https://python-poetry.org/) build tool.
To get started, install Poetry on your system by running

```
curl -sSL https://install.python-poetry.org | python3 -
```

After that, the package and its dependencies can be installed
in your local virtual environment by running

```
poetry lock && poetry install
```

Follow the documentation on the Poetry website for additional features such as
[managing dependencies](https://python-poetry.org/docs/managing-dependencies/),
[managing environments](https://python-poetry.org/docs/managing-environments/),
and [configuring the Python project metadata](https://python-poetry.org/docs/pyproject/).

### Dynamic Versioning

The package version is defined in the `src/albert/__init__.py` file.
However, Poetry requires that all project metadata is defined statically within the `pyproject.toml` file.
Because of this, we use the [Poetry dynamic versioning](https://pypi.org/project/poetry-dynamic-versioning/) plugin
to load the version variable when building the package.

To install the plugin, run

```
poetry self add "poetry-dynamic-versioning[plugin]"
```

This will allow for running the version to be loaded dynamically
when running command such as `poetry build`.

### Publishing

TODO

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for both formatting and linting.
Formatting and linting rules are enforced in the CI process.

To check (or fix) your code formatting, you can run the commands

```
# Check
ruff format . --check

# Fix
ruff format .
```

To check (or fix) your code linting, you can run the commands

```
# Check
ruff check .

# Fix
ruff check . --fix
```

For VSCode users, there is also base workspace settings defined in `.vscode/settings.json` that enable
automatic fomatting and import sorting on-save using the
[Ruff for VSCode](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) extension.