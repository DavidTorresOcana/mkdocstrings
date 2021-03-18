"""Module responsible for the objects inventory."""

# Credits to Brian Skinn
# and the sphobjinv project:
# https://github.com/bskinn/sphobjinv

import zlib
from textwrap import dedent
from typing import List, Optional


class InventoryItem:
    """Inventory item."""

    def __init__(self, name: str, domain: str, role: str, uri: str, priority: str = "1", dispname: str = "-"):
        """Initialize the object.

        Arguments:
            name: The item name.
            domain: The item domain, like 'python' or 'crystal'.
            role: The item role, like 'class' or 'method'.
            uri: The item URI.
            priority: The item priority. It can help for inventory suggestions.
            dispname: The item display name.
        """
        self.name: str = name
        self.domain: str = domain
        self.role: str = role
        self.uri: str = uri
        self.priority: str = priority
        self.dispname: str = dispname

    def format_sphinx(self) -> str:
        """Format this item as a Sphinx inventory line.

        Returns:
            A line formatted for an `objects.inv` file.
        """
        uri = self.uri
        name_length = len(self.name)
        if uri[-name_length - 1 :] == "#" + self.name:
            uri = uri[:-name_length] + "$"
        return f"{self.name} {self.domain}:{self.role} {self.priority} {uri} {self.dispname}"


class Inventory(dict):
    """Inventory of collected and rendered objects."""

    HEADER = """
        # Sphinx inventory version 2
        # Project: {project}
        # Version: {version}
        # The remainder of this file is compressed using zlib.
    """

    def __init__(self, items: Optional[List[InventoryItem]] = None, project: str = "project", version: str = "0.0.0"):
        """Initialize the object.

        Arguments:
            items: A list of items.
            project: The project name.
            version: The project version.
        """
        super().__init__()
        items = items or []
        for item in items:
            self[item.name] = item
        self.project = project
        self.version = version

    def register(self, *args, **kwargs):
        """Create and register an item.

        Arguments:
            *args: Arguments passed to [InventoryItem][mkdocstrings.inventory.InventoryItem].
            **kwargs: Keyword arguments passed to [InventoryItem][mkdocstrings.inventory.InventoryItem].
        """
        item = InventoryItem(*args, **kwargs)
        self[item.name] = item

    def format_sphinx(self, compress=True) -> bytes:
        """Format this inventory as a Sphinx `objects.inv` file.

        Arguments:
            compress: Whether to compress the data using zlib.

        Returns:
            The inventory as bytes.
        """
        header = dedent(self.HEADER).format(project=self.project, version=self.version).lstrip().encode("utf8")

        lines = []
        for item in self.values():
            lines.append(item.format_sphinx().encode("utf8"))

        data = b"\n".join(lines)
        if compress:
            data = zlib.compress(data, 9)
        return header + data
