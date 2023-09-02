# Car Price Analyzer Telegram Bot

## Introduction

This is a recommendation system for determining the price of a car based on existing offers on online ukrainian marketplaces. It important for someone who heed to short sale his car. So far system is only working with fuel cars.

## Methods explanation

In this project I get data from autoria.com - the biggest ukrainian marketplace for selling used cars. Every user request is processed and service parse data from site that are analyzed by service.

To get the final result I analyze data and use linear regression.

Linear regression is a data analysis method used to identify a linear relationship between one or more independent variables and a dependent variable. It constructs a mathematical model, represented by a linear equation, to predict the values of the dependent variable based on input data. This method finds widespread application in various fields, including economics, physics, and machine learning, for data prediction and analysis purposes.

## Installation

<pre>
git clone https://github.com/car_prices_bot.git
</pre>

Required libraries: requests, bs4, pandas, scikit-learn, json, aiogram.

## Running 

Here you can see example of work
Running with:
<pre>
cd car_prices

python bot.py
</pre>

![Typing characteristic](readmeimages/firstscree.png)

![Get result](readmeimages/secondscreen.png)

## Developing project

In next patches I plan to add oportunity work with electrocars and other vehicles. Also in next versions I try to switch on autoria.com API and minimize worktime.
