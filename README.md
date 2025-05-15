# Albert SDK
The Albert SDK provides a comprehensive and easy-to-use interface for interacting with the Albert API. The SDK is designed to simplify the process of working with various resources such as inventories, projects, companies, and tags by providing Resource Collections and Resource Models.

> [!WARNING]
> The Albert SDK is still in the early phases of development. As such, patterns may change, and methods may not work as expected. Do not use this package unless you are comfortable with these limitations.

## Installation

TODO: Add installation instructions from PyPI once published

For developers, please see the [contributing guide](CONTRIBUTING.md) for local installation instructions.

## Quick Start

```python

from albert import Albert

client = Albert()
projects = client.projects.list()

```

## Documentation

[Full Documentation can be found here](https://glowing-sniffle-8jy8mwz.pages.github.io/)