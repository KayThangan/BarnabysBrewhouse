"""
This module is a program that simulates sales predictions for a given
month or week from past sales. Last year's sale is stored in
"Barnabys_sales_fabriacted_data.csv". These are the datas that is used
to predict.
"""
import csv
import math
from datetime import datetime
from brew_logger import errorLogger, eventLogger

sales_data = {}
beers = []
sales_summary = {}
months = []
weeks = []

highest_gyle_number_for_beers = {}

SALES_PER_DAY = "sales_per_day"
SALES_PER_YEAR = "sales_last_year"
SALES_PER_WEEK = "Week {wk}"

errorLogger = errorLogger()
eventLogger = eventLogger()

def get_recommended_sales() -> dict:
    """
    Getting the recommended sales.
    :return recommended_sales: a dictionary of the recommended sales.
    """
    errorLogger.info("Getting the recommended sales.")
    recommended_sales = {}
    current_month = datetime.now().strftime('%B')
    current_month_index = months.index(current_month)
    temp = 0
    for x in range(3):
        month_prediction = predict_month_beer_qty(months[current_month_index + x])
        for beer in beers:
            try:
                if recommended_sales[beer]:
                    temp = recommended_sales[beer] + month_prediction[beer]
            except:
                temp = month_prediction[beer]
            recommended_sales.update({beer: temp})
    return recommended_sales

def update_recommended_sales(recommended_sales: dict, beer_name: str, quantity: int):
    """
    Updating recommended sales dictionary.
    :param recommended_sales: a dictionary of the recommended sales.
    :param beer_name: a string representing the name of the beer.
    :param quantity: an integer of the beer quantity.
    """
    errorLogger.info("Updating recommended sales dictionary.")
    recommended_sales.update({beer_name: (recommended_sales[beer_name] - quantity)})
    if recommended_sales[beer_name] <= 0:
        recommended_sales.update({beer_name: 0})
    eventLogger.critical("@recommended : @%s", recommended_sales)

def get_periods() -> list:
    """
    This function gets all the period in the csv file.
    :return periods: a list containing all the periods in the csv file.
    """
    errorLogger.info("Retrieving all the period group(such as months "
                     "and weeks) that was present in the csv file.")
    periods = []
    for month in months:
        periods.append(month)
    for week in weeks:
        periods.append(week)
    return periods

def add_bear_name(beer_name: str):
    """
    This method add new beers to the beers list.
    :param beer_name: a string containing beer's name.
    """
    errorLogger.info("Adding new beer to the beers list.")
    if beers.count(beer_name) == 0:
        beers.append(beer_name)

def get_value_by_key(obj: dict, key: str):
    """
    This function gets the value by the key.
    :param obj: a dictionary object.
    :param key: a string containing a key for dictionary object.
    """
    errorLogger.info("Getting value by a key.")
    try:
        return obj[key]
    except:
        errorLogger.error("The given obj or key doesn't exist.")
        return None

def update_sales_summary(date_obj: datetime, qty: int, beer: str):
    """
    This function updates the sales_summary dictionary.
    :param date_obj: a datetime of the date of the invoice order.
    :param qty: an integer representing number of bottle.
    :param beer: a string representing the beer.
    """
    errorLogger.info("Updating the sales summary list.")
    # Calculate year sales
    sale_qty_year = get_value_by_key(sales_summary, SALES_PER_YEAR)
    if not sale_qty_year:
        sale_qty_year = 0
    sale_qty_year = sale_qty_year + qty
    sales_summary.update({SALES_PER_YEAR: sale_qty_year})

    # Calculate each month sales
    month = date_obj.strftime('%B')
    sale_qty_month = get_value_by_key(sales_summary, month)
    if not sale_qty_month:
        sales_summary.update({month: {}})
        sale_qty_month = sales_summary[month]
        months.append(month)
    sale_beers_qty_month = get_value_by_key(sale_qty_month, beer)
    if beer not in sale_qty_month:
        sale_qty_month.update({beer: 0})
        sale_beers_qty_month = sale_qty_month[beer]
    tmp_qty = sale_beers_qty_month + qty
    sale_qty_month.update({beer: tmp_qty})
    sales_summary.update({month: sale_qty_month})

    # Calculate each week sales
    # gets the week number from the date
    week_no = date_obj.isocalendar()[1]
    # formatting the week string
    week = SALES_PER_WEEK.format(wk=week_no)
    sale_qty_week = get_value_by_key(sales_summary, week)
    if not sale_qty_week:
        sales_summary.update({week: {}})
        sale_qty_week = sales_summary[week]
        weeks.append(week)
    sale_beers_qty_week = get_value_by_key(sale_qty_week, beer)
    if beer not in sale_qty_week:
        sale_qty_week.update({beer: 0})
        sale_beers_qty_week = sale_qty_week[beer]
    tmp_qty = sale_beers_qty_week + qty
    sale_qty_week.update({beer: tmp_qty})
    sales_summary.update({week: sale_qty_week})

def load_barnabys_sales_csvfile(file_name: str):
    """
    This functions open and read the csv file and stores to a formatted
     dictionary.
    :param file_name: a string with the csv file name.
    """
    errorLogger.info("Loading the sales csv file.")
    # opening csv file
    try:
        csvfile = open(file_name, 'rt')
    except IOError:
        errorLogger.error("IOError")
        return None
    else:
        with csvfile:
            # reading the csv file
            csvfile_reader = csv.reader(csvfile)
            next(csvfile_reader)
            for row in csvfile_reader:
                recipe = row[3].strip()
                gyle = int(row[4].strip())
                quantity = int(row[5].strip())
                # stores the date from the csv file as a datetime
                # object.
                date_obj = datetime.strptime(row[2].strip(),
                                             "%d-%b-%y")

                beers_obj = get_value_by_key(sales_data, date_obj)
                if not beers_obj:
                    sales_data.update({date_obj: {}})
                    beers_obj = sales_data[date_obj]

                beer_key = recipe
                beer_obj = get_value_by_key(beers_obj, beer_key)
                if not beer_obj:
                    beer = {"gyle_number": gyle, "quantity": 0}
                    beers_obj.update({beer_key: beer})
                    beer_obj = beers_obj[beer_key]
                    highest_gyle_number_for_beers.update({beer_key:
                                                              gyle})

                tmp_qty = beer_obj["quantity"] + quantity
                beer_obj.update({"quantity": tmp_qty})
                beers_obj.update({beer_key: beer_obj})

                # Calculate day sales
                sale_qty_day = get_value_by_key(beers_obj,
                                                SALES_PER_DAY)
                if not sale_qty_day:
                    sale_qty_day = 0

                sale_qty_day = sale_qty_day + quantity
                beers_obj.update({SALES_PER_DAY: sale_qty_day})

                sales_data.update({date_obj: beers_obj})

                # Calculate year sales
                update_sales_summary(date_obj, quantity, beer_key)

                add_bear_name(beer_key)

def calculate_average(array_obj: list) -> float:
    """
    This method finds the average value from the list of elements.
    :param array_obj: a list of elements.
    :return average: a float of the average growth rate.
    """
    errorLogger.info("Calculating the average.")
    average = 0
    for element in array_obj:
        average += element
    average = average / len(array_obj)  # finding the average
    return average

def calculate_growth_rate(array_obj: list) -> dict:
    """
    This calculates the growth rate for each period.
    :param array_obj: a list of periods
    :return beer_growth_rate: a dictionary representing the growth rate
     for each period.
    """
    errorLogger.info("Calculating the growth rates.")
    beer_growth_rate = {}
    for beer in beers:
        growth = []
        for index in range(1, len(array_obj)):
            try:
                growth_rate = (sales_summary[array_obj[index]][beer] -
                               sales_summary[array_obj[index - 1]]
                               [beer]) / \
                              sales_summary[array_obj[index - 1]][beer]
                growth.append(growth_rate)
            except KeyError:
                errorLogger.error("KeyError")
                growth.append(0)
        average_growth = calculate_average(growth)
        beer_growth_rate.update({beer: round(average_growth, 2)})
    return beer_growth_rate

def total_beers_qty(period: datetime, beer_qty: dict) -> dict:
    """
    This gets the total quantity of beer depending on the date.
    :param period: a datetime containing the date at which the beers
     were ordered in the csv file.
    :param beer_qty: a dictionary where the quantity of beer is stored
     to.
    :return beer_qty: a dictionary with the quantity of beer.
    """
    errorLogger.info("Calculating the current total quantity of beer "
                     "for a given period.")
    for beer in beers:
        if beer not in beer_qty:
            beer_qty.update({beer: 0})
        try:
            tmp_qty = beer_qty[beer] + \
                      sales_data[period][beer]["quantity"]
            temp_total = beer_qty["total"] + \
                         sales_data[period][beer]["quantity"]
        except KeyError:
            errorLogger.error("KeyError")
            tmp_qty = beer_qty[beer] + 0
            temp_total = beer_qty["total"] + 0
        beer_qty.update({beer: tmp_qty})
        beer_qty.update({"total": temp_total})
    return beer_qty

def total_month_beers_qty(month_name: str) -> dict:
    """
    This gets the total quantity of beers for a given month.
    :param month_name: a string of the given month.
    :return month_beer_qty: a dictionary all beers for a given month.
    """
    errorLogger.info("Retrieving the current total quantity of beer "
                     "for given month.")
    month_beer_qty = {}
    month_beer_qty.update({"total": 0})
    for element in sales_data:
        if element.strftime('%B') == month_name:
            month_beer_qty = total_beers_qty(element, month_beer_qty)
    return month_beer_qty

def total_week_beers_qty(week_name: str) -> dict:
    """
    This gets the total quantity of beers for a given week.
    :param week_name: a string of the given week.
    :return week_beer_qty: a dictionary all beers for a given week.
    """
    errorLogger.info("Retrieving the current total quantity of beer "
                     "for given week.")
    week_beer_qty = {}
    week_beer_qty.update({"total": 0})
    for element in sales_data:
        if SALES_PER_WEEK.format(wk=element.isocalendar()[1]) == \
                week_name:
            week_beer_qty = total_beers_qty(element, week_beer_qty)
    return week_beer_qty

def predict_month_beer_qty(month_name: str) -> dict:
    """
    This predicts the quantity of beers for a given month.
    :param month_name: a string of the given month.
    :return month_beer_qty: a dictionary all beers for a given month.
    """
    errorLogger.info("Retrieving the predicted total quantity of beer "
                     "for given month.")
    month_beer_qty = total_month_beers_qty(month_name)
    beer_month_growth_rate = calculate_growth_rate(months)
    total = 0
    for beer in beers:
        temp_qty = math.ceil(month_beer_qty[beer] *
                             (1 + beer_month_growth_rate[beer]))
        total += temp_qty
        month_beer_qty.update({beer: temp_qty})
    month_beer_qty.update({"total": total})
    return month_beer_qty

def predict_week_beer_qty(week_name: str) -> dict:
    """
    This predicts the quantity of beers for a given week.
    :param week_name: a string of the given week.
    :return month_beer_qty: a dictionary all beers for a given week.
    """
    errorLogger.info("Retrieving the predicted total quantity of beer "
                     "for given week.")
    week_beer_qty = total_week_beers_qty(week_name)
    beer_week_growth_rate = calculate_growth_rate(weeks)
    total = 0
    for beer in beers:
        temp_qty = math.ceil(week_beer_qty[beer] *
                             (1 + beer_week_growth_rate[beer]))
        total += temp_qty
        week_beer_qty.update({beer: math.ceil(temp_qty)})
    week_beer_qty.update({"total": total})
    return week_beer_qty

# loading a csv file
load_barnabys_sales_csvfile("Barnabys_sales_fabriacted_data.csv")
