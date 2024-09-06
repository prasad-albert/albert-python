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
