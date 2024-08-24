import re

def sort_dict_by_values_desc(data):
    """
    Sorts a dictionary by its values in descending order.
    Parameters are the dictionary to sort, returns a new dictionary sorted by values from highest to lowest.
    """
    return dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

def sort_dict_by_values_asc(data):
    """
    Sorts a dictionary by its values in ascending order.
    Parameters are the dictionary to sort, returns a new dictionary sorted by values from lowest to highest.
    """
    return dict(sorted(data.items(), key=lambda item: item[1], reverse=False))

def sort_dict_by_keys_desc(data):
    """
    Sorts a dictionary by its keys in descending order.
    Parameters are the dictionary to sort, returns a new dictionary sorted by keys from highest to lowest.
    """
    return dict(sorted(data.items(), key=lambda item: item[0], reverse=True))

def sort_dict_by_keys_asc(data):
    """
    Sorts a dictionary by its keys in ascending order.
    Parameters are the dictionary to sort, returns a new dictionary sorted by keys from lowest to highest.
    """
    return dict(sorted(data.items(), key=lambda item: item[0], reverse=False))

def sort_dict_alphabetically(data):
    """
    Sorts a dictionary by its keys in alphabetical order.
    """
    return dict(sorted(data.items()))

def filter_dict(data, *conditions):
    """
    Filters the dictionary based on provided conditions.
    Parameters:
    - data: Dictionary to be filtered.
    - conditions: Functions that take a key-value pair and return True if it should be included.
    Returns: A new filtered dictionary.
    """
    filtered_data = {}
    for key, value in data.items():
        if all(condition(key, value) for condition in conditions):
            filtered_data[key] = value
    return filtered_data

def condition_greater_than_threshold(key, value, threshold=10):
    return value > threshold # can also be written as ===> lambda k, v: v >= 100

def condition_starts_with_letter(key, value, letter='J'):
    return key.upper().startswith(letter.upper())

def condition_starts_with_one_of_letter(key, value, letters=['X', 'Y', 'Z']):
    return key.upper()[0] in letters

def condition_name_length_greater_than_threshold(key, value, threshold=10):
    return len(key) > threshold

def condition_filter_out_specific_names(key, value, names=['(?)']):
    return key not in names # allows you to filter out specific patterns, which is useful for old records if a first name isn't actually provided

def trim_sorted_dictionary(dic, top_n_percent=0.1):
    '''
    Assuming a dictionary is sorted by value or name occurrence, we can take the first n occurences
    - example - take the top 10% names based on usage
    - top_n_percent should be written as decimal --> 0.1 = 10%
    '''
    n = round(len(dic) * top_n_percent)
    return dict(list(dic.items())[:n])

def combine_dicts(dict1: dict, dict2: dict):
    '''
    Combines two dictionaries by summing the counts of their common keys while simply concatenating key-value pairs which are unique to each other
    EXAMPLE:
        DICT1 = {'a': 3, 'b': 5, 'c' : 7 }
        DICT2 = {'b' : 1, 'c': 3, 'd': 3}
        combine_dicts(DICT1, DICT2) = {'a': 3, 'b': 6, 'c': 10, 'd': 3}
    '''
    new_dict = {}
    for key, value in dict1.items():
        if key in dict2:
            new_dict[key] = value + dict2[key]
        else:
            new_dict[key] = value
    for key, value in dict2.items():
        if key not in dict1:
            new_dict[key] = value
    return new_dict

def merge_years_into_decade(dict_to_recomp: dict):
    '''
    For a dictionary where the keys are birth years as integers, this function will merge key-value pairs which sit within the same decade
    - returns a dictionary where the key is the year and the value is the list of names born in that year
    '''
    new_dict = {}
    for key, value in dict_to_recomp.items():
        decade = int(key/10) * 10
        if decade in new_dict:
            for name in value:
                new_dict[decade].append(name)
        else:
            new_dict[decade] = value
    return new_dict

def recomp_dict(dict_to_recomp: dict):
    '''
    input: dictionary where key is a year or decade as int and the value is a list of names
    returns:
    - key is the year/decade as a number
    - the value is another dictionary mapping names from that year to their respective number of occurences ==> same structure as the output from get_firstnames
    '''
    new_dict = {}
    for key, value in dict_to_recomp.items():
        if key in new_dict:
            for name in value:
                if name in new_dict[key]:
                    new_dict[key] += 1
                else:
                    new_dict[key] = 0
        else:
            value_dict = {}
            for name in value:
                if name in value_dict:
                    value_dict[name] += 1
                else:
                    value_dict[name] = 1
            new_dict[key] = value_dict
    return new_dict