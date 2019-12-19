# Predict: CVE Labeling Tool

Predict is a tool meant for researchers looking to trace vulnerabilities back
through the history of a code base. The tool centers around CVEs as a source
of ground truth and offers many enhancements to the normal vulnerability tracing
workflow. A few of the main attractions are as follows:

1. Easy navigation through git blame
2. Simple creation of mappings from introduction to fix
3. Support for multiple researchers working in parallel
4. Conflict resolution tools for when labels don't agree
5. Data export tools to produce quickly analyzable datasets

## Documentation

Most of Predict's documentation is housed in the `docs` directory. Here is a 
brief overview of the various documents and the topics they cover:

* SETUP: Contains installation instructions for both single users and multiple users.
* CONFIGURATION: Covers the options to consider when configuring Predict.
* RUNNING: Goes over the various command line arguments associated with the command line tool.
* CONTRIBUTING: Details the ins and outs of the code base for new-comer developers.

## Quick Start

All you need to run Predict is a working installation of Python 3.5 or above.
Simply install Predict from your command line using pip (you'll need access
to the subversion repository):

```
$ pip install svn+https://vis.cs.umd.edu/svn/projects/predict/prod#egg=predict
```

Now you can run predict like so:

```
$ predict
```

And if you navigate to `localhost:5000` you should see predict up and running.
