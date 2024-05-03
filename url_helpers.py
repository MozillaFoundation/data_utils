from pandas import notnull
from numpy import nan
import re
from urllib.parse import urlparse

def fix_front_trunc_url(url):
    """
    This function will fix a url if it's front truncated and missing the url schema (https or http)
    """
    if url:
        trunc_search = re.compile('^://')
        trunc_url = re.search(trunc_search, url)
        
        #Make the url correct if it's been truncated in the front
        if trunc_url:
            #Since it really only matters for validation, just append https (rather than http) in front
            new_url = 'https' + url
            return new_url
        
        else:
            return url


def url_valid(url):
    """
    This function checks if a url is valid in having both a schema and a net location.
    """
    if (notnull(url)) & (url != ''):
        #Use try/except in case unexpected issues with url occur
        try:
            parsed = urlparse(url)

            if parsed.scheme and parsed.netloc:
                return True
            else:
                return False
        #If there is an exception return False (as in, the URL is invalid)
        except:
            return False
    else:
        return nan

def split_url(url):
    """
    This functions splits a url into pieces if it's valid.
    """
    if url_valid(url) == True:
        return urlparse(url)
    else:
        return nan

def split_utms(query):
    """
    This function is used to split out the individual UTM parameters from the query portion of a given URL.
    """
    if (notnull(query)) & (query != ''):
        ampersand = re.compile('(&){1}')
        ampersand_split = re.split(ampersand, query)

        equal = re.compile('(=){1}')

        result = {e[0]:e[2] 
                  for e in [re.split(equal, a) for a in ampersand_split if (a != '&')]
                  if len(e) == 3}

        if result:
            return result
        else:
            return nan
    else:
        return nan
    
def get_url_lang(path):
    """
    This function is used to split out the langauge or locale from the URL path.
    """
    
    if (notnull(path)) & (path != ''):
        #Compile the regex expression to remove the language from the URL Path, we want find between 2 and 6 an 
        #non-numeric character surrounded by a "/" at the start of string. 
        #There should ALWAYS be a language is this works on that assumption
        lang_search = re.compile('^/\D{2,6}/')
        lang= re.match(lang_search, path)
        
        if lang: 
            return lang.group(0).replace('/','')
        else:
            return nan
    else:
        return nan
    
def get_utm_tag(utm_dict, utm_key):
    """
    This function is used to get a specific UTM tag, if it exists in the parsed url query which is subsquently turned
    into a dictionary.
    """
    
    if (notnull(utm_dict)) & (isinstance(utm_dict, dict)):
        utm = utm_dict.get(utm_key)
        if utm:
            return utm
        else:
            return nan
    else:
        return nan