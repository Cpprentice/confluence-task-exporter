# Confluence Task Exporter (CTE)
This Python tool / package is intended to export the basic tasks from a Confluence instance.

The export will contain the task text, status, assigned usernames and the due date.

The available formats for export are CSV, Excel and JSON.

## Command line interface (CLI)

You can directly invoke the Python module to perform an export.


## Configuration file

To run the module you need to create a config file in the TOML syntax.

It should look like the following:

```toml
confluence-url = "https://some.url/of/confluence"
confluence-rest-url = "https://some.url/of/your/confluence/rest/api"
personal-access-token = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
```

The file is searched for in the working directory or can be specified via a command line flag.