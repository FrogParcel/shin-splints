from garminconnect import Garmin

# Mock login details for inspection
api = Garmin("email", "password")

# List all methods of the Garmin class
methods = [method for method in dir(api) if callable(getattr(api, method))]
print(methods)
