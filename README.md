# Albert SDK
The Albert SDK provides a comprehensive and easy-to-use interface for interacting with the Albert API. The SDK is designed to simplify the process of working with various resources such as inventories, projects, companies, and tags by providing Resource Collections and Resource Models.

## Installation

TODO: Add installation instructions from PyPI once published

For developers, please see the [contributing guide](CONTRIBUTING.mD) for local installation instructions.

## Overview
The SDK is built around two main concepts:

1. *Resource Models*: Represent individual entities like InventoryItem, Project, Company, and Tag. These are all controlled using Pydantic.

2. *Resource Collections*: Provide methods to interact with the API endpoints related to a specific resource, such as listing, creating, updating, and deleting resources.

### Resource Models
Resource Models represent the data structure of individual resources. They encapsulate the attributes and behaviors of a single resource. For example, an `InventoryItem` has attributes like `name`, `description`, `category`, and `tags`.

### Resource Collections
Resource Collections act as managers for Resource Models. They provide methods for performing CRUD operations (Create, Read, Update, Delete) on the resources. For example, the `InventoryCollection` class has methods like create, `get_by_id()`, `list()`, `update()`, and `delete()`. `list()` methods generally accept parameters to narrow the query to use it like a search.

## Usage
### Initialization
To use the SDK, you need to initialize the Albert client with your base URL and bearer token.
By default, the client Albert class will use the environment varribale `ALBERT_BEARER_TOKEN` and base_url `https://dev.albertinventdev.com`

```python
from albert.albert import Albert

# Initialize the client
client = Albert(
    base_url="https://dev.albertinventdev.com", # default value
    bearer_token = os.getenv("ALBERT_BEARER_TOKEN") # default value
    )
```

## Working with Resource Collections and Models
### Inventory Collection
You can interact with inventory items using the InventoryCollection class. Here is an example of how to create a new inventory item, list all inventory items, and fetch an inventory item by its ID.

```python
from albert.albert import Albert
from albert.resources.inventory import InventoryItem, InventoryCategory, UnitCategory
from albert.collections.base import OrderBy

client = Albert()

# Create a new inventory item
new_inventory = InventoryItem(
    name="Goggles",
    description="Safety Equipment",
    category=InventoryCategory.EQUIPMENT,
    unit_category=UnitCategory.UNITS,
    tags=["safety", "equipment"],
    company="Company ABC"
)
created_inventory = client.inventory.create(inventory=new_inventory)

# List all inventory items
all_inventories = client.inventory.list()

# Fetch an inventory item by ID
inventory_id = "INVE1"
inventory_item = client.inventory.get_by_id(inventory_id=inventory_id)

# Search an inventory item by name
inventory_id = "INVE1"
inventory_item = inventory_collection.list(name="Acetone", order=OrderBy.ACCENDING)
```