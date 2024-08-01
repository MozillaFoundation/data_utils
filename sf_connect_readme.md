## Using sf_connect
### Required Setup
Before getting started it's important that you have the credentials for an API User in Salesforce. Whether you have Windows or Mac (in .zshrc), you need to setup four global environment variables to enable the connection with Salesforce. The API User must be granted the appropriate permission set(s) with access to the required Salesforce Objects.

1. 'SALESFORCE_INSTANCE_URL': the cloud URL where our Salesforce instance sits, found under "Company Information" in settings.
2. 'SALESFORCE_API_USER': The username associated with the API user.
3. 'SALESFORCE_API_PASS': The password associated with the API user.
4. 'SALESFORCE_API_TOKEN': The token associated with he API user account, typically sent by Saleforce through email.

The sf_connect class has wrapped existing functionality from simple_salesforce and is intended to make things simpler. In doing so, specific environment variables are used to enable consistent functionality and secure, ease of use after the initial setup.

Note that since most use cases are currently ad hoc, we are using API Users rather than an OAuth integrated app, though it's possible that this changes in the future. 


### Get Started
First you need to instantiate the class into an object by calling sf_connect as shown below.

```sf = sf_connect()```

### Get the data from Salesforce
Let's first imagine that you have a query in mind that you want to run against Salesforce which is shown below.

```
query = """SELECT Id
                 ,CreatedDate
                 ,npsp__Do_Not_Contact__c
                 ,Email
           FROM Contact"""
```



```sf.sf_query_object(query)```

