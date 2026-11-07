def demo(**kwargs):

    print(type(kwargs))
    print(kwargs.get("json"))
    print(kwargs.get("banana"))

# demo(json={0:"on"})

mydict = {
    "state": "on",
    "name": "",
    "age": 30,
}

demo(json=mydict)