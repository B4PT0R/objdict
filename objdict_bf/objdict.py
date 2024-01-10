"""
Module providing an objdict class allowing to conveniently manipulate dictionaries or dict-based JSON nested structures using attribute-like syntax.
Intended mostly to ease manipulation of JSON data, web requests responses, configuration files, fast prototyping...
If the first argument passed at instantiation is a dict, the resulting objdict will use this dict as its internal data storage.
This ensures that any modification on either object is reflected on the other.
Provides utility methods for dict to objdict, and objdict to dict recursive conversion of nested structures.
Supports json and jsonpickle serialization and deserialization:
- from a json string via .dumps() and .loads() methods.
- from a json file via .dump() and load() methods
"""

import jsonpickle
jsonpickle.set_preferred_backend('json')
jsonpickle.set_encoder_options('json', indent=4,ensure_ascii=False)
import json
import re
import os
import inspect
from collections.abc import MutableMapping

def get_keys(obj):
    """
    Get the possible keys or indexes of a subscriptable object (strings excluded)
    """
    if hasattr(obj, 'keys'):
        # This covers dict and dict-like objects
        return list(obj.keys())
    elif isinstance(obj,str):
        return []
    elif hasattr(obj, '__getitem__') and hasattr(obj, '__len__'):
        # For list-like objects, return a list of indices
        return list(range(len(obj)))
    else:
        # Return an empty list otherwise
        return []

def is_valid_key(key):
    """
    Checks if a given key is a valid identifier suitable for attribute-like syntax
    """
    # Regex for valid Python identifiers
    identifier_match = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$').match
    return isinstance(key, str) and identifier_match(key)

def is_valid_dict(dic):
    """
    Checks if a given dict is suitable for objdict conversion
    """
    return isinstance(dic, dict) and all(is_valid_key(key) for key in dic)

class objdict(MutableMapping):
    """
    Class implementing an attribute-style access dictionary.
    Provides support for converting nested structures to and from objdict and dict.
    Provides support for json de/serialization to and from a json string or a json file. 
    """

    @staticmethod
    def to_objdict(item):
        """
        Converts to objdict if item is a valid dict 
        """
        if is_valid_dict(item):
            return objdict(item)
        else:
            return item
        
    @staticmethod
    def to_dict(item):
        """
        Converts to dict if item is an objdict
        """
        if isinstance(item,objdict):
            return item._data_dict
        else:
            return item

    @staticmethod
    def to_dict_rec(item):
        """
        Converts all objdicts found in a nested data structure to their respective _data_dict, recursively.
        """
        if isinstance(item, objdict):
            # Convert objdict to dict and 
            return objdict.to_dict_rec(item._data_dict)
        elif isinstance(item, str):
            # Do not convert strings
            return item
        elif hasattr(item, '__iter__') and hasattr(item, '__getitem__') and hasattr(item, '__setitem__'):
            # This will handle both dict-like and list-like objects
            for key in get_keys(item):
                item[key] = objdict.to_dict_rec(item[key])
        return item
    
    @staticmethod
    def to_objdict_rec(item):
        """
        Converts all convertible dicts found in a nested data structure to their objdict version, recursively.
        Ensures that dictionary keys are suitable for attribute-like access before converting.
        """
        if is_valid_dict(item):
            # Convert dict to objdict if keys are valid identifiers
            for key in get_keys(item):
                item[key] = objdict.to_objdict_rec(item[key])
            return objdict(item)
        elif isinstance(item, str):
            # Do not convert strings
            return item
        elif hasattr(item, '__iter__') and hasattr(item, '__getitem__') and hasattr(item, '__setitem__'):
            # This will handle both dict-like and list-like objects
            for key in get_keys(item):
                item[key] = objdict.to_objdict_rec(item[key])
        return item

    def __init__(self, *args,_use_default=False,_default=None,_file=None,_auto_self=False,_use_jsonpickle=False, **kwargs):
        """
        Initialize the objdict with key-value pairs as kwargs, or dicts/objdicts/iterables passed as args.
        If the fisrt unamed arg is a dict or objdict object, it will be permanently synchronized (same object adress) to the internal _data_dict.
        """
        self._use_default=_use_default # use the default value generator
        self._default=_default # default value or default value generator function
        self._file=_file #optional json file path for direct dumping
        self._auto_self=_auto_self #allows to auto-pass the objdict instance to callable items, mimicking object methods behavior
        self._use_jsonpickle=_use_jsonpickle
        if args:
            if isinstance(args[0], dict):
                if is_valid_dict(args[0]):
                    self._data_dict = args[0]
                else:
                    raise KeyError("All keys of a dict must be valid identifiers to support objdict conversion.")
            elif isinstance(args[0],objdict):
                self._data_dict=args[0]._data_dict
            else:
                #otherwise initialize an empty dict and attempt to update with the first arg (possibly an iterator over key/value pairs)
                self._data_dict={}
                self.update(args[0])
        else:
            self._data_dict={}
            

        #attempt to update with remaining args
        for arg in args[1:]:
            self.update(arg)
        
        #update with kwargs
        self.update(kwargs)
    
    @staticmethod
    def default(key,_default):
        """
        Special method used internaly to deal with setting default values.
        if _default is a callable, uses this callable to generate default values depending on the key passed
        else use _default as the default value for all keys
        """
        if callable(_default):
            return _default(key)
        else:
            return _default

    def to_dict(self):
        """
        Converts objdict to dict, recursively.
        """
        return objdict.to_dict_rec(self)
    
    def set_data_dict(self,dic):
        """
        Set the internal _data_dict to a dict if suitable
        """
        if is_valid_dict(dic):
            self._data_dict=dic
        else:
            raise ValueError("Internal data dict can only be set to a dict with valid identifiers as keys.")
        
    def set_json_file(self,file):
        """
        Set the internal _file reference to a json file path
        """
        if isinstance(file,str) and file.endswith(".json"):
            self._file=file
        else:
            raise ValueError("The internal file reference must be the path to a json file.")

    def __getitem__(self, key):
        if key in self._data_dict:
            item=self._data_dict[key]
        else:
            if self._use_default:
                item=objdict.default(key,self._default)
                self[key]=item
            else:
                raise KeyError(f"Invalid key: '{key}'")
        if callable(item) and self._auto_self:
            sig = inspect.signature(item)
            params = list(sig.parameters.values())
            if params and params[0].name == 'self':
                def wrapper(*args,**kwargs):
                    return item(self,*args,**kwargs)
                return wrapper
            else:
                return item
        else:
            return objdict.to_objdict_rec(item)

    def __setitem__(self, key, value):
        if is_valid_key(key):
            self._data_dict[key] = value
        else:
            raise KeyError(f"The key must be a valid identifier: {key}")

    def __delitem__(self, key):
        if key in self._data_dict:
            del self._data_dict[key]

    def __getattr__(self, key):
        """
        Support for attribute-style access to key:value pairs.
        """
        if key in self.__dict__:
            # First, check if it's an instance attribute
            return getattr(self, key)
        elif key.startswith('__'):
            # delegate to super for any special attribute
            return super().__getattribute__(key)
        else:
            # Then, check in the dictionary
            return self[key]

    def __setattr__(self, key, value):
        """
        Support for attribute-style setting of key:value pairs
        """
        if key =='_use_default':
            if isinstance(value,bool):
                super().__setattr__(key,value)
            else:
                raise TypeError("The '_use_default' attribute must be set to a boolean value.")
        elif key =='_auto_self':
            if isinstance(value,bool):
                super().__setattr__(key,value)
            else:
                raise TypeError("The '_auto_self' attribute must be set to a boolean value.")
        elif key =='_use_jsonpickle':
            if isinstance(value,bool):
                super().__setattr__(key,value)
            else:
                raise TypeError("The '_use_jsonpickle' attribute must be set to a boolean value.")
        elif key=='_default':
            super().__setattr__(key,value)
        elif key=='_file':
            if value is not None:
                if isinstance(value,str) and os.path.isdir(os.path.dirname(value)) and value.endswith(".json"):
                    super().__setattr__(key,value)
                else:
                    raise ValueError(" _file attribute must be a json file path.")
        elif key == "_data_dict":
            if is_valid_dict(value):
                super().__setattr__(key, value)
            else:
                raise TypeError("The '_data_dict' attribute must be set to a dict object with valid identifiers as keys.")
        elif hasattr(super(),key) or key.startswith('__'):
            super().__setattr__(key,value)
        else:
            self[key] = value

    def __delattr__(self, key):
        del self[key]

    def keys(self):
        return self._data_dict.keys()

    def values(self):
        return (self[key] for key in self._data_dict)

    def items(self):
        return ((key, self[key]) for key in self._data_dict)

    def update(self, other=None,**kwargs):
        if other:
            if hasattr(other, 'keys'):
                for key in other.keys():
                    self[key] = other[key]
            elif hasattr(other, "__iter__"):
                for key, value in other:
                    self[key] = value
            else:
                raise ValueError("Can only update with a dict-like object or an iterable of key/value pairs.")
        for key in kwargs:
            self[key]=kwargs[key]

    def pop(self, key, default=None):
        default=default or self._default
        value=self._data_dict.pop(key, objdict.default(key,default))
        return objdict.to_objdict_rec(value)

    def clear(self):
        self._data_dict.clear()

    def copy(self):
        return objdict(self._data_dict.copy())

    def deepcopy(self):
        from copy import deepcopy
        return objdict(deepcopy(self._data_dict))

    def __eq__(self, other):
        if isinstance(other, objdict) or isinstance(other, dict):
            return self.to_dict() == objdict.to_dict_rec(other)
        return False

    def __str__(self):
        return str(self._data_dict)

    def __repr__(self):
        return repr(self._data_dict)

    def __len__(self):
        return len(self._data_dict)

    def __iter__(self):
        return iter(self._data_dict)
    
    def __contains__(self,key):
        return key in self._data_dict

    def setdefault(self, key, default=None):
        default=default or self._default
        if key not in self:
            self[key] = objdict.default(key,default)
        return self[key]

    def popitem(self):
        key, value = self._data_dict.popitem()
        return key, objdict.to_objdict_rec(value)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        return cls({key: objdict.default(key,value) for key in iterable})

    # Python 3.9 and newer
    def __ior__(self, other):
        self.update(other)
        return self

    def __iand__(self, other):
        common_keys = self.keys() & other.keys()
        for key in list(self):  # List conversion to avoid runtime error due to size change
            if key not in common_keys:
                del self[key]
        return self
    
    def __or__(self, other):
        new_dict = objdict()
        new_dict.update(self)
        new_dict.update(other)
        return new_dict

    def __ror__(self, other):
        new_dict = objdict()
        new_dict.update(other)
        new_dict.update(self)
        return new_dict
    
    def __reversed__(self):
        return reversed(self._data_dict)
    
    @classmethod
    def loads(cls,json_string,use_jsonpickle=False):
        """
        Creates a new objdict instance by deserializing a dict-like json string
        """
        if use_jsonpickle:
            data=jsonpickle.decode(json_string)
        else:
            data=json.loads(json_string)
            
        if is_valid_dict(data):
            return cls(data,_use_jsonpickle=use_jsonpickle)
        else:
            raise ValueError("The json data must be a valid dict to be deserialized into an objdict.")
    
    def dumps(self,use_jsonpickle=False):
        """
        Serializes an objdict into a json string
        """
        self._use_jsonpickle=use_jsonpickle or self._use_jsonpickle
        if self._use_jsonpickle:
            return jsonpickle.encode(self.to_dict())
        else:
            return json.dumps(self.to_dict(),indent=4,ensure_ascii=False)
    
    @classmethod
    def load(cls,file,use_jsonpickle=False):
        """
        Creates a new objdict instance by deserializing a json file
        """
        if isinstance(file,str) and os.path.isfile(file) and file.endswith(".json"):
            if use_jsonpickle:
                with open(file,'r') as f:
                    data=jsonpickle.decode(f.read())
            else:
                with open(file,'r') as f:
                    data=json.load(f)

            if is_valid_dict(data):
                return cls(data,_file=file,_use_jsonpickle=use_jsonpickle)
            else:
                raise ValueError("The json data must be a valid dict to be deserialized into an objdict.")
        else:
            raise ValueError("You must provide a valid json file path before loading from a file.")
        
    def dump(self, file=None,use_jsonpickle=False):
        """
        Serializes the objdict into a json file 
        """
        self._use_jsonpickle=use_jsonpickle or self._use_jsonpickle
        self._file = file or self._file
        if isinstance(self._file, str) and os.path.isdir(os.path.dirname(self._file)) and self._file.endswith(".json"):
            if self._use_jsonpickle:
                with open(self._file, 'w', encoding='utf-8') as f:
                    f.write(jsonpickle.encode(self.to_dict()))  
            else:  
                with open(self._file, 'w', encoding='utf-8') as f:
                    json.dump(self.to_dict(), f, indent=4,ensure_ascii=False)
        else:
            raise ValueError("You must provide a valid json file path before dumping to a file.")

    
MutableMapping.register(objdict)

if __name__=='__main__':
    def default(key):
         return objdict(_auto_self=True,_default=default,_use_default=True)
    obj=objdict(_auto_self=True, _default=default,_use_default=True)
    obj.a.value=2
    def add(self, x):
        self.value+=x
    obj.a.add=add
    obj.b.value=5
    obj.b.add=add
    obj.b.add(4)
    obj.a.add(3)
    print(obj)