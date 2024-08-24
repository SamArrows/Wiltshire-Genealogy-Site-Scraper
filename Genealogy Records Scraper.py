'''
https://www.wiltshirefamilyhistory.org
https://www.wiltshirefamilyhistory.org/master_index.htm

The program being developed is intended to be able to scrape data from this genealogy site from which stats and analysis can be done.
Currently, it is effectively able to utilise threading to count all instances of unique first names and store and output them as a dictionary


'''
from bs4 import BeautifulSoup
from dictionary_funcs import *
from namesnlp import *
import re
import requests
import threading
import matplotlib.pyplot as plt

session = requests.Session() # Create a session object
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)   # Configure connection pool size
session.mount('http://', adapter)
session.mount('https://', adapter)

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

def get_firstnames_with_birthyear(page: BeautifulSoup, exclude_middle_names: bool = False, format_circa: bool = False, dict_to_insert_into: dict = None):
    '''
    Returns a dictionary of birthyear mapped to a list of names for that respective year
    = page: page to search for names
    = exclude_middle_names: if True, will only take the first name of a person, i.e. Mary Lucy Smith ==> Mary, else takes all first names, i.e. Mary Lucy Smith ==> Mary Lucy
    = format_circa: some birth years are rough and not known exactly; for example, c. 1860 could be from 1857-1863 ==> a rough range of birth years around 1860; 
        format_circa will store this in the dictionary as a key unchanged when set to False or will simply display the rough birth year as a number for the key if True
        EXAMPLE WHEN FALSE ==> {'c 1830': ['Mary', 'Ann'], 'c 1796': ['Mary Ann', 'Harriet'] }
        EXAMPLE WHEN TRUE ==> {1830: ['Mary', 'Ann'], 1796: ['Mary Ann', 'Harriet'] }
    = dict_to_insert_into: by default, is None which creates and returns a new dictionary, else will add to an existing one
    Example of the shape of the dictionary would be akin to 
    {
        1860 : ['Mary', 'Edward'],
        1899 : ['Mary', 'Stephen']
    }
    '''
    firstname_containers = page.find_all('dd')
    if dict_to_insert_into == None:
        dict_to_insert_into = {} # map birth years to a list of names registered in that year
    for dd in firstname_containers:
        entries = dd.decode_contents().split('<br/>')
        for entry in entries:
            clean_entry = BeautifulSoup(entry, 'html.parser').get_text(strip=True) # Remove HTML tags and excess whitespace
            if 'b.' in clean_entry: # Split the entry to separate name from birth year
                name_year = clean_entry.split('b.')
                name = name_year[0].strip()

                if exclude_middle_names:
                    name = name.split(" ")[0]

                birth_info = name_year[1].strip().split(',')[0]  # Get only the birth year part
                birth_year = birth_info.strip()
                if format_circa:
                    if 'c' in birth_year:
                        numbers = re.findall(r'\d+', birth_year) # Extract numeric characters using regular expressions
                        birth_year = ''.join(numbers) # Join the list of numbers into a single string (if needed)
                    birth_year = int(birth_year[-4:])
                if birth_year in dict_to_insert_into:
                    dict_to_insert_into[birth_year].append(name)
                else:
                    dict_to_insert_into[birth_year] = [name]
    return dict_to_insert_into

def find_variations_in_name(name: str, all_names: List[str], distance_threshold: float = 0.75, store_as_dict: bool = False):
    '''
    Provided a list of names, this function will find all the variations in the name using a distance metric (Jaro-Winkler)
    and either return a list of variations of the name (i.e. names with a distance above the threshold) or a dictionary where
    the keys are the names and the values are the distances.

    If you want to apply operations to the names before finding variations, such as stemming, you can apply that to the list of names
    separately, then turn the list into a set and back into a list.

    Inputs:
    - name (str) ==> the name you want to find variations for
    - all_names (List[str]) ==> the list of names to search for variations
    - distance_threshold (float) ==> for a name to be identified as a variation, its distance to the input name must be above the threshold specified
    - store_as_dict (bool) ==> as described above, either return list of variations or a dictionary of the variations mapped to their respective distances
    '''
    collection = {}
    for x in all_names:
        #print(jaro_winkler_distance(name,x))
        if(jaro_winkler_distance(name, x) > distance_threshold):
            collection[x] = distance_threshold
    if(store_as_dict):
        return collection
    else:
        return collection.keys()

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


#print(get_firstnames_with_birthyear(get_surname_index_page(22), False, True))

name_dict = {}
#threads = instantiate_threads(4, 79, get_firstnames_with_birthyear, True, True)    # call this function to instantiate dictionary with years as the keys and lists of names as values
threads = instantiate_threads(4, 79, get_firstnames, True, True)   # call this function to instantiate dictionary with names as keys and occurrences represented as integers for values

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

dics = []

for thread in threads:
    dics.append(thread.dic)

data = {}

for i in range(0, len(dics)):
    data = combine_dicts(data, dics[i])

#for key, value in data.items():
#    print(f"{key}: {value}")

target_name = "Marie"
print(target_name)

data = list(set(data.keys()))
print(data)
variations = find_variations_in_name(target_name, data, 0.6, True)


print(f"Target name: {target_name}")
for key,value in variations.items():
    print(f"Name: {name}; Distance: {value}")

#data = recomp_dict(merge_years_into_decade(data))

#for key, value in data.items():
#    print(key, ": ", value, "\n")


def format_plot_for_getFirstNamesWithBirthYearAsInt(data: dict, number_of_names_to_plot: int = 1):
    '''
    Call this function if your dictionary was created using the function get_firstnames_with_birthyear
    where the birthyear was inserted as an integer --> i.e. years with circa or a full birth day must be formatted to a single year
    - dictionary should be of the form key : val ==> int : List[string]
        where the key is a year and the val is the list of names in that year

    Aim of plot is to have decades on the x-axis in chronological order, number of name occurrences on the y-axis; three bars will be allocated on each decade, representing the 
        top three most common given first names in that decade, with the names written at the top of the bars

    = First, we need to sort the dictionary by keys from lowest to highest for the years/decades to be in chronological order
    = Next, we need to sort the values' dictionaries from highest to lowest by values - these dictionaries have names for keys and number of uses for values
    = We then need to label on the x-axis: the keys representing decades; the y-axis: number of occurrences for names; and the bars: most common names each decade

    STILL NEED TO ADD FUNCTIONALITY TO PLOT A NUMBER OF TOP POPULAR NAMES, I.E. TOP TWO, THREE, FOUR ETC.
    https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
    USE THIS WEBSITE FOR GUIDANCE
    '''
    # Set default font sizes
    plt.rcParams['font.size'] = 14               # Default font size for all text
    plt.rcParams['axes.titlesize'] = 16          # Size for axes titles
    plt.rcParams['axes.labelsize'] = 14          # Size for axes labels
    plt.rcParams['xtick.labelsize'] = 12         # Size for x-tick labels
    plt.rcParams['ytick.labelsize'] = 12         # Size for y-tick labels
    plt.title('Most popular first names recorded at birth per decade in Stourton, Mere, Kilmington and Wiltshire 17-19th Centuries')

    chronological = sort_dict_by_keys_desc(data)
    decades = list(chronological.keys())
    top_names = []
    respective_counts = []     
    for key, name_dict in chronological.items():
        max_val = max(name_dict.values())
        top_names.append(f"{', '.join(name for name, count in name_dict.items() if count == max_val)}")
        respective_counts.append(max_val)
    '''
    OLD METHOD, SEE ABOVE FOR NEW METHOD
    for key, name_dict in chronological.items():
        # now we need to get the values sorted by value in descending order
        name_dict_sorted = sort_dict_by_values_desc(name_dict)
        top_names.append(list(name_dict_sorted.keys())[0])
        respective_counts.append(list(name_dict_sorted.values())[0])   
        # these lines can be used to double check extracted values for debugging purposes -> i.e. seeing what happens if two names have the same count
        #top_name = list(name_dict_sorted.keys())[0]
        #top_names.append(top_name)
        #count = list(name_dict_sorted.values())[0]
        #respective_counts.append(count)
        #print(f"{name_dict_sorted} \n{top_name} \n{count}\n\n")
    '''
    
    # plot just the top name for now, add functionality for choosing top three or five or however many later on
    bar_width = 3
    bars = plt.bar(decades, respective_counts, color='purple', width=bar_width)

    for i in range(0,len(bars)):
        height = bars[i].get_height()
        plt.annotate(f'{top_names[i]}\n{height}',
                    xy=(bars[i].get_x() + bars[i].get_width() / 2, height),
                    xytext=(0, 1),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',
                    rotation=90,
                    fontsize=8)

    plt.xlabel('Decade')
    plt.ylabel('Total occurrences of most popular name')
    plt.xticks(rotation=90)
    #plt.ylim(0, max(respective_counts) + 5)
    #plt.grid(True)

    plt.show()

def format_plot_for_getFirstNames(data: dict):
    '''
    Call this function if your dictionary was created using the function get_firstnames
    - dictionary should be of the form key : val ==> string : int
        where the key is a name and the val is the count for that name
    '''
    # data = trim_sorted_dictionary(filter_dict(sort_dict_by_values_desc(complete_dictionary), condition_filter_out_specific_names))
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

#format_plot_for_getFirstNamesWithBirthYearAsInt(data)