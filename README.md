# objdict

`objdict-bf` is a Python module that provides a class for conveniently manipulating dictionaries or dict-based JSON nested structures using attribute-like syntax. It is intended mostly to ease the manipulation of JSON data, web requests responses, configuration files, and more.

## Features

- Attribute-style access to dictionary items (e.g., `obj.key` instead of `obj['key']`).
- Synchronization with the original dictionary if passed at instantiation.
- Utility methods for recursive conversion of nested structures to and from `objdict` and `dict`.
- JSON serialization and deserialization methods for both strings and files.

## Installation

```bash
pip install objdict-bf
```

## Usage

Here's a simple example of how to use `objdict`:

```python
from objdict_bf import objdict

# Create an objdict with some initial data
data = objdict({'name': 'John', 'age': 30, 'location': 'New York'})

# Access data using attribute-style access
print(data.name)  # Output: John
print(data.age)   # Output: 30

# Modify data
data.age = 31

# Serialize to JSON string
json_string = data.dumps()

# Deserialize from JSON string
new_data = objdict.loads(json_string)
```

## Methods

- `to_objdict()`: Convert a dictionary to `objdict` if keys are valid identifiers.
- `to_dict()`: Convert an `objdict` to a dictionary, recursively.
- `loads()`, `dumps()`: Load from and dump to JSON strings.
- `load()`, `dump()`: Load from and dump to JSON files.

... and many more.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.