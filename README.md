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

## Crawling mode

With version 0.0.2 a crawling mode was introduced. It can be started with the launch files or the `cte.crawler` module.

You can specify a target space and a regular expression that shall be used to search.
The tool has a built-in cache so it will only process a fixed number of pages each run (defaults to 50).
It will continue with the next unchecked page on the next invocation.


Example
```sh
python -m cte.crawler --space Test --search "TODO|DONE"
```

This might produce an output like
```text
Matched term in "lorem ipsum TODO dolor sit": https://my.confluence/pages/viewpage.action?pageId=1234567
Processed 50 pages this run
```

Depending on your terminal the links are clickable to directly access the respective pages.
