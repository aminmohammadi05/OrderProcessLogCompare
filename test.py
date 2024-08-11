import re

def remove_alphanumeric_suffix(input_string):
    return re.sub(r'[a-zA-Z0-9]+$', '', input_string)

# Examples
print(remove_alphanumeric_suffix("reviewStars_24601"))  # Output: reviewStars_
print(remove_alphanumeric_suffix("zoodfood_sess_47955728397af2705d9939463fdc78d7"))  # Output: zoodfood_sess_