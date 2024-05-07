import pandas as pd
import os
from simple_salesforce import Salesforce
from simple_salesforce import bulk2
from simple_salesforce.format import format_soql
import requests
import re
import csv
from datetime import date, datetime
from numpy import float64, int64, dtype

#Salesforce reference of data types and the corresponding pandas dtype
#https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/field_types.htm
DTYPE_MAPPER = {'objecting': 'object'
                ,'double': 'float64'
                ,'boolean': 'bool'
                ,'textarea': 'object'
                ,'date': 'date'
                ,'datetime': 'datetime'
                ,'id': 'object'
                ,'masterrecord': 'object'
                ,'reference': 'object'
                ,'email': 'object'
                ,'picklist': 'object'
                ,'phone': 'object'
                ,'percent': 'float64'
                ,'location': 'object'
                ,'currency': 'object'
                ,'address': 'object'
                ,'string': 'object'}

class sf_connect:
    def __init__(self):
        
        #Create the tuple of environment variables to search for
        env_vars = ('SALESFORCE_INSTANCE_URL'
                    ,'SALESFORCE_API_USER'
                    ,'SALESFORCE_API_PASS'
                    ,'SALESFORCE_API_TOKEN')
        
        #Create an empty dict for the credentials
        credentials = {}
        
        #Loop through the evironment variables and add them to the credential dict if they exist
        #otherwise raise an exception.
        for e in env_vars:
            try:
                credentials.update({e: os.environ[e]})
            except:
                raise Exception('Environment Variable {} does not exist, please set this value.'.format(e))
        
        #Set the credentials of the class
        self.__credentials = credentials
        
        #Connect to Salesforce using the credentials from above
        self.salesforce = Salesforce(instance = self.__credentials.get('SALESFORCE_INSTANCE_URL')
                                    ,username = self.__credentials.get('SALESFORCE_API_USER')
                                    ,password = self.__credentials.get('SALESFORCE_API_PASS')
                                    ,security_token = self.__credentials.get('SALESFORCE_API_TOKEN')
                                    ,session_id = requests.Session())
        
    def get_sf_object(self, query):
        if query:
            self.query = format_soql(query)

            #Create the search expression: the "from" statement, with spaces and at least one of any letter or digit.
            #The purpose is to extract the Salesforce Object
            search_object = re.compile('from\s{1,}\w{1,}(\s{0,}|$)', re.IGNORECASE)
            
            #Create the replacement expression, we want to replace the from and any space characters
            replace = re.compile('(from|\s)', re.IGNORECASE)

            #Search the input query
            result = re.search(search_object, self.query)

            try:
                #Replace the objectings to only get the object.
                self.sf_object = re.sub(replace, '', result[0])
                #Return the salesforce object.
                #return sf_object
            except:
                raise Exception('No salesforce object found in query. The result is empty, please check your query')
            
    def sf_query_object(self, query):

        #Add the salesforce object attribute from the query
        self.get_sf_object(query)
        
        try:
            #Create the connections to the appropriate endpoints
            self.api_object = self.salesforce.__getattr__(self.sf_object)
            self.bulk2_object = self.salesforce.bulk2.__getattr__(self.sf_object)

            #Create a dict of column names and the salesforce data types
            from_dtypes = {c.get('name'): c.get('type') for c in self.api_object.describe().get('fields')}
    
            #Connect to the object via bulk2
            print('Querying data from Salesforce for the {} object...'.format(self.sf_object))
            results = self.bulk2_object.query(self.query)
            print('Query completed.')
        #Otherwise raise any exceptions from the Salesforce class or otherwise
        except Exception as e:
            raise(e)

        print('Parsing query results...')    
        csv_data = [r for r in results]

        df_list = []

        #Iterate through the list of lists
        for c in csv_data:
            #Split each list by the newline characters
            newline_split = c.split('\n')
            #Create a csv reader for all rows except the header, explicitly delimit by a comma
            reader = csv.reader(newline_split[1:], delimiter = ',')
            #Create a csv reader for only the header, explicitly delimit by a comma
            col_reader = csv.reader([newline_split[0]], delimiter = ',')
            #Append a dataframe with the values and columns to the df_list
            df_list.append(pd.DataFrame([row for row in reader if row], columns = [c for c in col_reader]))
        
        if df_list:
            print('Converting results to dataframe...')
            #Concatenate the df_list
            self.data = pd.concat(df_list)
            #In some cases the columns may end up as a multi-index, reset them to just an index
            self.data.columns = self.data.columns.get_level_values(0)
            #Map these data types to the appropriate pandas data types
            self.to_dtypes = {k: DTYPE_MAPPER.get(v) for k,v in from_dtypes.items() if k in self.data.columns}

            #Create a dictionary of the existing dtypes
            dtypes_dict = self.data.dtypes.apply(lambda x: x.name).to_dict()

            #Loop through each column, compare the dtypes and change them if appropriate
            print('Converting data types...')
            for c in self.data.columns:               
                to_dtype = self.to_dtypes.get(c)
                #If the datatypes are not equal follow the specified procedures
                if to_dtype != dtypes_dict.get(c):
                    print('Converting column {} to {}...'.format(c, to_dtype))   
                    #If the to_dtype is a date then convert the column to a datetime.date
                    if to_dtype == 'date':
                        self.data[c] = self.data.apply(lambda x: datetime.strptime(x[c], '%Y-%m-%d').date(), axis = 1)
                    #Else if the to_dtype is a datetime then convert the column to a datetime.datetime
                    elif to_dtype == 'datetime':
                        self.data[c] = self.data.apply(lambda x: datetime.strptime(x[c], '%Y-%m-%dT%H:%M:%S.%f%z'), axis = 1)
                    #Else use the astype method for conversion as it functions the same for the other dtypes
                    else:
                        self.data[c] = self.data[c].astype(dtype(to_dtype))

                else:
                    pass