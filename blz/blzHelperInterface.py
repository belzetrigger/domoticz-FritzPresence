import re
def isBlank (myString:str):
    """
    checks a string for empty or blank.
    false: myString is not None AND myString is not empty or blank
    true: myString is None OR myString is empty or blank

    Args:
        myString (str): text to check

    Returns:
        bool: true if blank or empty
    """
    return not (myString and myString.strip())

def isNotBlank (myString:str):
    """checks a string for empty or blank.
    true: myString is not None AND myString is not empty or blank
    false: myString is None OR myString is empty or blank

    Args:
        myString (str): text to check

    Returns:
        bool: true if not blank AND not empty
    """
    return bool(myString and myString.strip())

def isValidMAC(mac:str):
    """checks given string for MAC-Pattern

    Args:
        mac (str): the string to check

    Returns:
        boolean: if string looks like MAC, we return true
    """
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower())

def abstractfunc(func):
    func.__isabstract__ = True
    return func


class Interface(type):
    def __init__(self, name, bases, namespace):
        for base in bases:
            must_implement = getattr(base, "abstract_methods", [])
            class_methods = getattr(self, "all_methods", [])
            for method in must_implement:
                if method not in class_methods:
                    err_str = """Can't create abstract class {name}!
                    {name} must implement abstract method {method} of class {base_class}!""".format(
                        name=name, method=method, base_class=base.__name__
                    )
                    raise TypeError(err_str)

    def __new__(metaclass, name, bases, namespace):
        namespace["abstract_methods"] = Interface._get_abstract_methods(namespace)
        namespace["all_methods"] = Interface._get_all_methods(namespace)
        cls = super().__new__(metaclass, name, bases, namespace)
        return cls

    def _get_abstract_methods(namespace):
        return [
            name
            for name, val in namespace.items()
            if callable(val) and getattr(val, "__isabstract__", False)
        ]

    def _get_all_methods(namespace):
        return [name for name, val in namespace.items() if callable(val)]


class BlzHelperInterface(metaclass=Interface):
    @abstractfunc
    def needsUpdate(self):
        """does some of the devices need an update

        Returns:
            boolean -- if True -> please update the device in domoticz
        """
        pass

    @abstractfunc
    def dumpConfig(self):
        """just print configuration and settings to log"""
        pass

    @abstractfunc
    def reset(self):
        """set all important fields to None"""
        pass

    @abstractfunc
    def reinitData(self):
        """re-init data objects"""
        pass

    @abstractfunc
    def dumpStatus(self):
        """just print current status to log"""
        pass

    @abstractfunc
    def getAlarmLevel(self):
        """calculates alarm level based on nearest waste element

        Returns:
            {int} -- alarm level
        """
        pass

    @abstractfunc
    def getAlarmText(self):
        """only returns latest element like: (date) [optional hint]
        if you want more, look at getSummary()

        Returns:
            {str} -- data from nearest text
        """
        pass

    @abstractfunc
    def getDeviceName(self):
        """calculates a name based on nearest waste element
        form: [image optional] (waste type) (days till collection)

        Returns:
            {str} -- name as string
        """
        pass

    @abstractfunc
    def getSummary(self, seperator: str = "<br>"):
        pass

    @abstractfunc
    def setError(self, error):
        """sets the error msg and put error flag to True

        Arguments:
            error {Exception} -- the caught exception
        """
        pass

    @abstractfunc
    def resetError(self):
        """just removes error flag and deletes last error msg"""
        pass

    @abstractfunc
    def hasErrorX(self):
        """true if there was or still is an error"""
        pass

    @abstractfunc
    def getErrorMsg(self):
        """returns the error message if exists"""
        pass

    @abstractfunc
    def getSummary(self, seperator: str = "<br>"):
        pass
