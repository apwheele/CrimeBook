# CrimeBook

This is a code example for the an end-to-end project example for my [*Data Science for Crime Analysis with Python*](https://crimede-coder.com/blogposts/2024/PythonDataScience) book. It shows creating data manipulation functions, as well as an automated CompStat report that updates with the newest data available.

The components are:

 - `/src/prep.py`, functions to download and prepare Cary crime data including, monthly counts, YTD metrics, and apartment complex stats
 - `/src/viz.py`, functions to create tables and graphs in the automated report
 - `CaryReport.ipynb`, jupyter notebook that is automated to calculate updated metrics

Contact: [Andrew Wheeler](https://crimede-coder.com/)

## Executing the notebook

To create the report from the command line, you can run:

    jupyter nbconvert --execute --no-input --allow-chromium-download --to webpdf CaryReport.ipynb

## Creating the python environment

To create the python environment to run this code, I use conda:

    conda create --name pybook python=3.10 pip
    conda activate pybook
    pip install -r requirements.txt
