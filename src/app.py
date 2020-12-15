"""
This module is a program that simulates a remote controlled
user-interfaced web server.
"""
from datetime import datetime
import time
import threading
import json
from flask import Flask, render_template, request, redirect, url_for
from sales_predictor import get_periods, months, sales_data, beers, \
    predict_month_beer_qty, highest_gyle_number_for_beers, \
    predict_week_beer_qty, get_recommended_sales, \
    update_recommended_sales
from brew_process import status_process_for_tank, \
    start_process_for_beers, create_process_for_beer, \
    status_process_for_beer, move_process_to_next_state, \
    remove_process_for_beer, status_process_for_beer_stock, \
    restore_beer_process
from brew_logger import errorLogger, eventLogger
import brew_process_dict

PERIODS = get_periods()
MONTHS = months
SALES_DATA = sales_data
BEERS = beers
current_month = datetime.now().strftime('%B')
predicted_beer = predict_month_beer_qty(current_month)
highest_gyle_number = highest_gyle_number_for_beers

inventory = {}
SALE_PREDICT = {}
recommended_sales = get_recommended_sales()

tab_no = {"tab": ""}
period = {"period": current_month}

errorLogger = errorLogger()
eventLogger = eventLogger()

app = Flask(__name__)

def get_json_from_last_prefix(fname: str, prefix_key: str):
    """
    This gets the last late in a file.
    :param fname: a string informing the file name.
    :param prefix_key: a string containing the prefix key.
    :return:
    """
    errorLogger.debug("GET LAST LINE: %s", fname)
    # check if the file exists
    try:
        file = open(fname, 'r')
    except IOError:
        errorLogger.error("Failed to to read log file %s", fname)
        return None
    else:
        with file:
            lines = file.read().splitlines()
            if lines:
                for line in range(len(lines), 1, -1):
                    # using '@' as a key to split the string
                    split_data = lines[line - 1].split("@")
                    if split_data[1] == (prefix_key + " : "):
                        if len(split_data) <= 1:
                            errorLogger.error("Event(s) has not found "
                                              "in the system log: "
                                              "%s", line)
                            return
                        data_line = split_data[2].replace("\'", "\"")
                        data_line = data_line.replace("True", "true")
                        data_line = data_line.replace("False", "false")
                        return json.loads(data_line)
            return None

def restore_from_log():
    """
    This retrieve the information from log file as json format.
    :return:
    """
    errorLogger.debug("RESTORE FROM LOG")
    log_file_name = "log/system.log"

    tanks = get_json_from_last_prefix(log_file_name, "tanks")
    recommended = get_json_from_last_prefix(log_file_name,
                                            "recommended")
    stock = get_json_from_last_prefix(log_file_name, "stock")
    states = get_json_from_last_prefix(log_file_name, "state")

    # check if the log file is empty
    if tanks:
        brew_process_dict.TANKS = tanks
    else:
        errorLogger.warning("System log doesn't the prefix key: "
                            "tanks.")

    if recommended:
        for beer in recommended:
            recommended_sales.update({beer: recommended[beer]})
    else:
        errorLogger.warning("System log doesn't the prefix key: "
                            "recommended.")

    if stock:
        for beer in stock:
            brew_process_dict.update_beer_stock(beer, stock[beer])
    else:
        errorLogger.warning("System log doesn't the prefix key: "
                            "stock.")

    if states:
        for state_data in states:
            restore_beer_process(state_data["gyle"],
                                 state_data["name"], state_data["qty"],
                                 state_data["state"],
                                 state_data["is_allocate"],
                                 state_data["p_tank"])
    else:
        errorLogger.warning("System log doesn't the prefix key: "
                            "state.")


@app.route('/', methods=['GET'])
def root() -> redirect:
    """
    This function will run at the localhost when it is being started
     up.
    :return: redirect to the home method.
    """
    errorLogger.debug("ROOT")
    return redirect(url_for('home'))

@app.route('/home', methods=['GET'])
def home() -> render_template:
    """
    Initialise the home page for the web sever.
    :return: render_template.
    """
    errorLogger.debug("HOME")
    time.sleep(0.2)
    return render_template("dashboard.html", PERIODS=PERIODS,
                           SALES_DATA=SALES_DATA, BEERS=BEERS,
                           TANKS=status_process_for_tank(),
                           GYLE_NO=highest_gyle_number,
                           PROCESS_MANAGEMENT=status_process_for_beer(),
                           SALES=SALE_PREDICT, TAB_NO=tab_no["tab"],
                           PERIOD=period["period"],
                           RECOMMENDED_SALES=recommended_sales,
                           BEER_STOCK=status_process_for_beer_stock())

@app.route('/salesPredictor', methods=['POST'])
def sales_predictor() -> redirect:
    """
    Initialise the sales predictor page for the web sever.
    :return:
    """
    tab_no.update({"tab": "tab0"})
    errorLogger.debug("SALES PREDICTOR")

    SALE_PREDICT.clear()
    sales_period = request.form.get("sales_period")
    period.update({"period": sales_period})

    if sales_period in MONTHS:
        SALE_PREDICT.update(predict_month_beer_qty(sales_period))
    else:
        SALE_PREDICT.update(predict_week_beer_qty(sales_period))
    return redirect(url_for('home'))

@app.route('/continueProcess/<string:beer_key>', methods=['POST'])
def continue_process(beer_key: str) -> redirect:
    """
    Initialise the continue process page for the web sever.
    :param beer_key:
    :return:
    """
    tab_no.update({"tab": "tab1"})
    errorLogger.debug("CONTROL DASHBOARD")

    beer_name, gyle_no, quantity = beer_key.split(":")
    move_process_to_next_state(int(gyle_no), beer_name, int(quantity))
    return redirect(url_for('home'))

@app.route('/completeProcess/<string:beer_key>', methods=['POST'])
def complete_process(beer_key: str) -> redirect:
    """
    Initialise the complete process page for the web sever.
    :param beer_key:
    :return:
    """
    tab_no.update({"tab": "tab1"})
    errorLogger.debug("CONTROL DASHBOARD")

    beer_name, gyle_no, quantity = beer_key.split(":")
    remove_process_for_beer(int(gyle_no), beer_name, int(quantity))
    return redirect(url_for('home'))

@app.route('/addBrewProcess', methods=['POST'])
def add_brew_process() -> redirect:
    """
    Initialise the add brew process page for the web sever.
    :return:
    """
    tab_no.update({"tab": "tab1"})
    errorLogger.debug("ADD BREW PROCESS")

    beer_name = request.form.get("beer_name")
    qty = int(request.form.get("quantity"))
    highest_gyle_number.update(
        {beer_name: (highest_gyle_number[beer_name] + 1)})
    gyle_number = highest_gyle_number[beer_name]

    update_recommended_sales(recommended_sales, beer_name, qty)
    create_process_for_beer(gyle_number, beer_name, qty)
    return redirect(url_for('home'))

def run_event():
    while True:
        try:
            start_process_for_beers()
            time.sleep(0.1)
        except:
            errorLogger.error("Failed to create a spread thread for "
                              "start_process_for_beers method")


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    restore_from_log()

    # start_process_for_beers()
    thread = threading.Thread(target=run_event)
    thread.setDaemon(True)
    thread.start()

    app.run(debug=True)
