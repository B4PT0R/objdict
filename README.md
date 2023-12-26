# objdict-bf

`objdict-bf` is a Python module that provides a wrapper class for conveniently manipulating dictionaries or dict-based JSON nested structures using attribute-like syntax. It is intended mostly to ease manipulation of JSON data, web requests responses, configuration files...

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

Here's an example of how to use the `objdict` wrapper:

```python
from objdict_bf import objdict

# Create an objdict with some initial data
data = objdict(
    name='John',
    age=30,
    location='New York'
)

#Or synchronize with an existing dict
d={'name': 'John', 'age': 30, 'location': 'New York'}
data = objdict(d)

# Access data using attribute-style access
print(data.name)  # Output: John
print(data.age)   # Output: 30

# Modify data
data.age = 31

#Changes are reflected on the original dict
print(d['age']) #Ouput: 31

#Support for nested structures involving lists
d={
    'profile':{
        'name':'John',
        'hobbies':[
            {'type':'sport','title':'tennis'},
            {'type':'music','title':'guitar playing'}
        ]
    }
}
data = objdict(d)

print(data.profile.hobbies[1].title) #Output: guitar playing

#Conversion of dict items to their objdict version is automatic.
#The objdict being essentially a wrapper interface on the initial dict,  
#this conversion is reflected in the initial dict content as well

print(isinstance(data.profile.hobbies[1],objdict)) #Output: True
print(isinstance(d['profile']['hobbies'][1],objdict)) #Output: True

#to_dict returns the underlying dict, converting recursively all objdicts found in the nested structure back to dicts
print(d is data.to_dict()) #Ouptut: True
print(isinstance(d['profile']['hobbies'][1], dict) #Output: True 

# Serialize to JSON string
json_string = data.dumps()

#dump to a JSON file
data.dump("my_json_file.json")

#Or set a file reference and dump (the reference to the file is kept in the objdict instance)
data.set_json_file("my_json_file.json")
data.dump()

# Deserialize from JSON string (creates a new instance)
data = objdict.loads(json_string)

# Deserialize from a JSON file (new instance keeping reference to the json file)
data = objdict.load("my_json_file.json")

#update data
data.email="dummy.email@gmail.com"
data.user="dummy_username"

#dump changes to 'my_json_file.json'
data.dump()

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.