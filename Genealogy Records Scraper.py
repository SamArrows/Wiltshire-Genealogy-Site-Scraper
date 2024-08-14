'''
https://www.wiltshirefamilyhistory.org
https://www.wiltshirefamilyhistory.org/master_index.htm

The program being developed is intended to be able to scrape data from this genealogy site from which stats and analysis can be done.
Currently, it is effectively able to utilise threading to count all instances of unique first names and store and output them as a dictionary


'''

import requests
from bs4 import BeautifulSoup
import threading
import matplotlib.pyplot as plt

session = requests.Session() # Create a session object
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)   # Configure connection pool size
session.mount('http://', adapter)
session.mount('https://', adapter)

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

def get_surname_index_page(index: int):
    try:
        if 0 < index < 80:
            URL = f"https://www.wiltshirefamilyhistory.org/i{index}.htm"
            page = session.get(URL) # use session.get to make use of connection pooling, otherwise use page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            return soup
        else:
            raise PageNumberNotInRangeException
    except PageNumberNotInRangeException as e:
        print(e)

def get_firstnames(page: BeautifulSoup, count_members: bool = True, exclude_middle_names: bool = False, dict_to_insert_into: dict = None):
    '''
    Returns dictionary of firstnames and their occurrences 
    = page: page to search for names
    = count_members: if True, counts how many occurrences of a name else returns a set of the unique first names used
    = exclude_middle_names: if True, will only take the first name of a person, i.e. Mary Lucy Smith ==> Mary, else takes all first names, i.e. Mary Lucy Smith ==> Mary Lucy
    = dict_to_insert_into: by default, is None which creates and returns a new dictionary, else will add to an existing one
    '''
    names = [name.get_text() if not exclude_middle_names else name.get_text().split(" ")[0] for name in page.find_all('dl')[0].find_all('a')]
    if count_members:
        if dict_to_insert_into == None:
            dict_to_insert_into = {} # Count instances of each name using a dictionary
        for name in names:
            if name in dict_to_insert_into:
                dict_to_insert_into[name] += 1
            else:
                dict_to_insert_into[name] = 1
        return dict_to_insert_into
    else:
        return set(names)

def instantiate_threads(thread_count: int = 4, total_pages: int = 79, target_function = get_firstnames, *args_for_target):
    '''
    Creates threads with as evenly distributed a workload as possible
    = target_function: the function for each thread to use
    = thread_count: how many threads to create
    = total_pages: number of pages on the genealogy page (79 is the current number but if this changes in future with any updates to the site, it can be updated here easily)
    '''
    threads = []
    pages_per_thread = round(float(total_pages) / thread_count)
    if pages_per_thread != total_pages / thread_count:
        for i in range(0, thread_count-1):
            threads.append(WebScrapeThread(i*pages_per_thread+1, pages_per_thread, target_function, *args_for_target))
        pages_remaining = 79 - (thread_count-1) * pages_per_thread
        threads.append(WebScrapeThread((thread_count-1)*pages_per_thread+1, pages_remaining, target_function, *args_for_target))
    else:
        for i in range(0, thread_count):
            threads.append(WebScrapeThread(i*pages_per_thread+1, pages_per_thread, target_function, *args_for_target))
    return threads

class PageNumberNotInRangeException(Exception):
    def __init__(self, message="The index of the page requested is not in the required range (1 - 79)"):
        self.message = message
        super().__init__(self.message)

class WebScrapeThread(threading.Thread):
    def __init__(self, start_idx, pages_to_scrape, target_function, *args, **kwargs):
        super(WebScrapeThread, self).__init__()
        self.start_idx = start_idx
        self.pages_to_scrape = pages_to_scrape
        self.target = target_function
        self.args = args
        self.kwargs = kwargs
        self.dic = {}

    def run(self):
        for i in range(self.start_idx, self.start_idx + self.pages_to_scrape):
            page = get_surname_index_page(i)
            self.dic = combine_dicts(self.target(page, *self.args, **self.kwargs), self.dic)



name_dict = {}

threads = instantiate_threads(4, 79, get_firstnames, True, True)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

dics = []

for thread in threads:
    dics.append(thread.dic)

complete_dictionary = {}

for i in range(0, len(dics)):
    complete_dictionary = combine_dicts(complete_dictionary, dics[i])

#for key, value in complete_dictionary.items():
#    print(f"{key}: {value}")

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

data = trim_sorted_dictionary(filter_dict(sort_dict_by_values_desc(complete_dictionary), condition_filter_out_specific_names))
# data = filter_dict(sort_dict_by_values_asc(complete_dictionary), condition_starts_with_one_of_letter)
# any of the conditions can be applied in the filter_dict function to customize the plot

keys = list(data.keys())
values = list(data.values())

plt.bar(keys, values, color='purple')

# Set default font sizes
plt.rcParams['font.size'] = 14               # Default font size for all text
plt.rcParams['axes.titlesize'] = 16          # Size for axes titles
plt.rcParams['axes.labelsize'] = 14          # Size for axes labels
plt.rcParams['xtick.labelsize'] = 12         # Size for x-tick labels
plt.rcParams['ytick.labelsize'] = 12         # Size for y-tick labels

plt.title('First Names recorded at birth in Stourton, Mere, Kilmington and Wiltshire 17-19th Centuries')

# Add exact numbers above the bars
for i, value in enumerate(values):
    plt.text(i, 
            value + 0.5, 
            str(value), 
            ha='center', 
            va='bottom',
            rotation=45,  
            fontsize=8)

plt.xlabel('Names')
plt.ylabel('Total')
plt.xticks(rotation=90)
#plt.grid(True)

plt.show()