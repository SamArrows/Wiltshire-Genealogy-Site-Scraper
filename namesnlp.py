'''
General outline:
- to be able to find variations of names which have the same base, such as mary and marie, sara and sarah, adam and addam, etc.
- abbreviations and variations on stems, such as charles and charlie = charl- + ie or es ; or sam ==> sam-my or sam-uel
- search for vowel/vowel sound substrings in a name and find possible variants of the name by replacing the sound, as with mary and marie
- search for consonant substitutions such as jacob and jakob where the vowel succeeding c determines whether it sounds like k or s and thus whether the name has variations
'''
from typing import List
import re

def replace_strings(strings_replacements: dict):
    '''
    Replace letters with other corresponding letters by feeding in a one-to-one dictionary of strings to strings, specifying what to replace
    - uses regex to systematically replace each substring key by its corresponding value before moving on to the next key-value substring pair
    '''
    return 


def stemmatization(x: str, letters_to_strip_from_end: List[str] = [], remove_sequential_duplicates: bool = False):
    '''
    Apply stemming following the rules you define in the params, which should be self-explanatory
    '''
    stem = x
    if letters_to_strip_from_end != []:
        keep_stripping = True
        i = -1
        while keep_stripping:
            if x[i] in letters_to_strip_from_end:
                stem = stem[:-1]
                i -= 1
                if -i == len(x):
                    keep_stripping = False
            else:
                keep_stripping = False
    x = stem
    if remove_sequential_duplicates:    # remove repeated letters, such as Addam ==> Adam, Sammie ==> Samie, Garry ==> Gary
        # works but only for two cases of duplicate letters, i.e. with a string like addammussa, it isn't fixing the 3rd occurrence and onwards
        for i in range(0, len(x)):
            if i != len(x)-1:
                if x[i] == x[i+1]:
                    stem = stem[:i] + stem[i+1:]        
    return stem


def matching_characters(x: str, y: str):
    '''
    https://rosettacode.org/wiki/Jaro_similarity#:~:text=The%20Jaro%20distance%20is%20a,1%20is%20an%20exact%20match.
    - returns the number of matching characters in the two strings
    - Two characters from x and y are considered matching only if they are the same and not farther apart than  
        ( max(|x|, |y|) / 2 ) - 1   characters where |x| = len(x), |y| = len(y)
    - Example: same and seam have 4 matching characters
    '''
    x = x.upper()
    y = y.upper()
    matches = 0
    for i in range(0, len(x)):
        check_next_letter = False
        j = 0
        while not check_next_letter:
            if x[i] == y[j]:
                if abs(i - j) < max(len(x), len(y)) / 2:
                    matches += 1
                    check_next_letter = True
            else:
                j += 1
                if j == len(y):
                    check_next_letter = True
    return matches

def length_of_common_prefix(x: str, y: str):
    '''
    - returns the length of the common prefix of two strings
    '''
    x = x.upper()
    y = y.upper()
    length = 0
    chars_to_check = min(len(x),len(y))
    terminate = False
    while not terminate:
        if x[length] == y[length]:
            length += 1
        else:
            terminate = True
    return length


def transpositions(x: str, y: str):
    '''
    - Transpositions are the number of matching characters that are not in the same position in both strings divided by 2
    - For each matching character, check if its position in one string is different from its position in the other string
        - Count the number of matching characters that are out of order
        - Divide this count by 2 to get the number of transpositions
    '''
    x = x.upper()
    y = y.upper()
    count = 0
    for i in range(0, len(x)):
        check_next_letter = False
        j = 0
        while not check_next_letter:
            if x[i] == y[j]:
                if abs(i - j) < max(len(x), len(y)) / 2:
                    if i != j:
                        count += 1
                    check_next_letter = True
            else:
                j += 1
                if j == len(y):
                    check_next_letter = True
    return count / 2.0

def jaro_winkler_distance(x: str, y: str, winkler_on: bool = True, scaling_factor: int = 0.1):
    '''
    Jaro distance = 1/3 * (m/|s1| + m/|s2| + (m-t)/m)
    Where:
        m = Number of matching characters
        t = Number of transpositions
        |s1| = Length of string 1
        |s2| = Length of string 2
    Jaro-Winkler distance = Jaro distance + l * p * (1 - Jaro distance)
    Where:
        Jaro distance: Calculated using the Jaro distance formula
        l = Scaling factor (typically 0.1)
        p = Length of common prefix at the start of the strings (max 4)

    Evidently, the parameters of the function allow you to determine whether to use standard Jaro distance 
    or, by default, apply Jaro-Winkler, along with the scaling_factor which is 0.1 by default
    '''
    m = matching_characters(x,y)
    if m == 0:
        return 0
    else:
        t = transpositions(x, y)
        jaro = 1/3 * (m / len(x) + m / len(y) + (m-t)/m)
        if winkler_on:
            return jaro + scaling_factor * min(4, length_of_common_prefix(x,y)) * (1 - jaro)
        else:
            return jaro

#print(stemmatization("marrianna", ['a','e','i','o','u','y'], True))
#print(jaro_winkler_distance("Marie", "Eerie"))

#print(jaro_winkler_distance(stemmatization("jake",  ['a','e','i','o','u','y'], True), stemmatization("jacob",  ['a','e','i','o','u','y'], True)))


