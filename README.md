# EoLPAFT

This code was written for the tool shared in  "An End-ofLife Plastic and Additive Flow Tracker Tool for Scenario Forecasting."

<p align="center">
  <img src=https://github.com/jdchea95/EoLPAFT/blob/main/eolpaft%20diagram.png width="80%">
</p>

## Requirements

This code was written using Python 3.x. The following Python libraries are required for running the code:

1. tkinter (https://docs.python.org/3/library/tkinter.html
2. numpy (https://pypi.org/project/numpy/)
3. PIL (https://pypi.org/project/pillow/)
4. plotly (https://pypi.org/project/plotly/)
5. pandas (https://pypi.org/project/pandas/)
6. datetime (https://pypi.org/project/DateTime/)
7. io (https://docs.python.org/3/library/io.html)
8. html2image (https://pypi.org/project/html2image/)
9. tktooltip (https://pypi.org/project/tkinter-tooltip/)
10. matplotlib (https://pypi.org/project/matplotlib/)
11. xlsxwriter (https://pypi.org/project/XlsxWriter/)

## How to use

The Python Script requires no additional documents. To run the Python script, you need to navigate to the directory containing main.py. Then, you execute the following command either on Windows CMD or Unix terminal:

```
python main.py
```
The GUI will open and allow use of the tool. The data can then be input by the user. 

## Outputs

After running the Python script you will obtain the following files:

| File name | Description |
| ------------- | ------------- |
| temp-plot.html | Sankey Diagram Showing Normalized Flows  |
| Sankey_Diagram.png  | PNG version of Sankey Diagram above  |


Optional documents that can also be generated:
| File name | Description |
| ------------- | ------------- |
|Stream Summary Calculations.xlsx | Shows MSW stream flows for scenario, current data marked by sheet date/time|

## Uncertainty Testing
The EoL_GUI_uncert.py file can be used to carry out the uncertainty analysis described in Section 2.3.3 and 3.3, which tests a range of mass percents in for each additive category. This file can be executed alongside the uncert_testing.xlsx file (both must be saved in the same folder as the environment path at execution). 

## Inputs
| File name | Description |
| ------------- | ------------- |
|uncert_testing.xlsx | Contains mass percents of additive categories to be used in the uncertainty testing|

## Outputs

After running the uncertainty Python script you will obtain the following files:

| File name | Description |
| ------------- | ------------- |
| MonteCarloResults.xlsx | Contains additive releases resulting from uncertainty testing at different additive mass compositions |


## Disclaimer

The views expressed in this article are those of the authors and do not necessarily represent the views or policies of the EPA. Any mention of trade names, products, or services does not imply an endorsement by ORAU/ORISE, the US Government, or the EPA. The EPA does not endorse any commercial products, services, or enterprises.

## Acknowledgement

This research was supported in part by an appointment to the US Environmental Protection Agency (EPA) Research Participation Program administered by the Oak Ridge Institute for Science and Education (ORISE) through an interagency agreement between the US Department of Energy (DOE) and the US EPA. ORISE is managed by ORAU under DOE contract number DE-SC0014664. Partial support for undergraduate student at Rowan University was provided by the US EPA Bipartisan Infrastructure Law (BIL) P2 grant 4U96236522.
