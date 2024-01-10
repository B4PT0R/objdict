# objdict-bf

`objdict-bf` is a Python module that provides a wrapper class for conveniently manipulating dictionaries or dict-based JSON nested structures using attribute-like syntax. It is intended mostly to ease manipulation of JSON data, web requests responses, configuration files, dynamic prototyping...

## Features

- Attribute-style access to dictionary items (e.g., `obj.key` instead of `obj['key']`).
- Synchronization with the original dictionary if passed at instantiation.
- Utility methods for recursive conversion of nested structures to and from `objdict` and `dict`.
- JSON serialization and deserialization methods for both strings and files with optional jsonpickle support.
- Advanced default value attribution features for missing keys. 
- optional object-like behavior, by auto-passing the instance as 'self' to callable attributes with 'self' in their signature.

## Installation

```bash
pip install objdict-bf
```

## Signature of the constructor

```python
objdict(*args,_use_default=False,_default=objdict.default_default,_file=None,_use_jsonpickle=False,_auto_self=False,**kwargs)
```

Parameters:
- `*args`: either dicts, objdicts or iterables on key:value pairs. If the first arg is a dict, it will serve as the internal _data_dict of the objdict instance.
- `_use_default`: boolean, determines if a default value is attributed to missing keys
- `_default`: can be any value or callable. If callable, the callable will be used to handle default values generation. If ommited, falls back to the objdict.default_default static method: automatically generate a child objdict instance when accessing a missing key. 
- `_file`: reference to a json file path for dumping
- `_use_jsonpicke`: boolean. Determines if jsonpickle is used for serialization when dumping.
- `_auto_self`: boolean. Determines if the instance is auto-passed a 'self' to its callable attributes with 'self' in their signature (mocked object behavior).
- `**kwargs`: key value pairs passed as kwargs to update the objdict


## Usage

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

#-----------------------------JSON serialization-------------------------------

# Serialize to JSON string
json_string = data.dumps()
#or use jsonpickle for advanced serialization 
json_string=data.dumps(use_jsonpickle=True)

#dump to a JSON file
data.dump("my_json_file.json")
#or
data.dump("my_json_file.json",use_jsonpickle=True)

#make some more changes
data.email="dummy.email@gmail.com

#the reference to the file and jsonpickle usage preference from the last dump is kept in the objdict instance so you don't have to pass them again
data.dump()

# Deserialize from JSON string (creates a new instance)
data = objdict.loads(json_string)
#or
data = objdict.loads(json_string,use_jsonpickle=True)

# Deserialize from a JSON file (new instance keeping reference to the json file)
data = objdict.load("my_json_file.json")
#or
data = objdict.load("my_json_file.json",use_jsonpickle=True)

#update data
data.email="dummy.email@gmail.com"
data.user="dummy_username"

#dump changes to 'my_json_file.json' 
data.dump()

#-------------------Working with default value generators-------------------


#Default value when accessing a missing key
obj=objdict(_use_default=True,_default=3)
print(obj.a) #Output: 3

#Or pass a default value generator depending on the key (must have 'key' in its signature)
default_gen=lambda key: f"Missing key: {key}" 
obj=objdict(_use_default=True,_default=default_gen)
print(obj.a) #Output: "Missing key: a"

#Or pass a default value generator whose output depends on the current state/content of the objdict
#must have 'self' in its signature
#use 'self' as the keyword refering to the current objdict instance
def default_gen(self):
    if a in self:
        return self.a.value
    else:
        return objdict(value=5)
        
obj=objdict(_use_default=True,_default=default_gen)
print(obj.a) #Output: {'value':5}
print(obj.b) #Output: 5

#Accepted signature of default value generators are () ; (self,); (key,) ; (self,key)
#This allows implementing complex context aware and key-dependant logic for default value attribution. 
#Any other signature will be considered invalid and will fall back to assign the callable itself as the default value for all keys.

#Using a default value generator to create new child objdict instances inheriting the parent's setting when accessing missing keys
def default_default(self):
    return objdict(_use_default=True,_default=default_default,_use_jsonpickle=self._use_jsonpickle,_auto_self=self._auto_self)

obj=objdict(_use_default=True,_default=default_default,_use_jsonpickle=True)
obj.a.b.c=3
print(obj) #Output: {'a':{'b':{'c':3}}}
#child elements inherit the chosen parent properties
print(obj.a.b._use_jsonpickle) #Output: True
print(obj.a.b._auto_self) #Output: False

#This last behavior is the default one (implemented by the objdict.default_default static method) if you set _use_default to True without specifying a _default parameter
#Choose explicitely _default=None if you want to pass None as a default value

obj=objdict(_use_default=True)
print(isinstance(obj.a),objdict)) #Output: True

obj=objdict(_use_default=True,_default=None)
print(obj.a is None) #Output: True

#--------------------------------Mock objects-------------------------------

#Using the objdict as a mocked object with context aware methods thanks to the _auto_self parameter which automatically passes the objdict instance as 'self' to callable attributes having 'self' as first parameter in their signature.

obj=objdict(_auto_self=True)
obj.a=2

#create a function with 'self' as first parameter (any other name won't receive the instance)
def add_to_a(self,b):
    self.a+=b

#attach the function as attribute
obj.add_to_a=add_to_a
obj.add_to_a(3)
print(obj.a) #output 5

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.