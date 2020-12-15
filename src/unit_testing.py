"""
This module is a program carries out unit testing.
"""
import unittest
from datetime import datetime
from time import strptime

import brew_process
import sales_predictor


class TestSalesPredictor(unittest.TestCase):
    """
    TestSalesPredictor
    """
    def test_months_list(self):
        """
        test_months_list
        :return:
        """
        self.assertLessEqual(len(sales_predictor.months), 12)
        for month in sales_predictor.months:
            self.assertIn(strptime(month, '%B').tm_mon, range(0, 13))

    def test_weeks_list(self):
        """
        test_weeks_list
        :return:
        """
        self.assertLessEqual(len(sales_predictor.weeks), 52)
        for week in sales_predictor.weeks:
            week_no = week.split(" ", 1)[1]
            self.assertIn(int(week_no), range(0, 53))

    def test_beers_list(self):
        """
        test_beers_list
        :return:
        """
        self.assertGreater(len(sales_predictor.beers), 0)
        for beer in sales_predictor.beers:
            beer_key_word = beer.split(" ", 1)[0]
            self.assertEqual(beer_key_word, "Organic")

    def test_sales_data_dict(self):
        """
        test_sales_data_dict
        :return:
        """
        sales_data = sales_predictor.sales_data
        self.assertTrue(sales_data, dict)
        for date in sales_data:
            self.assertTrue(date, datetime)
            self.assertTrue(sales_data[date]["sales_per_day"], int)
            for beer in sales_predictor.beers:
                try:
                    self.assertTrue(
                        sales_data[date][beer]["gyle_number"], int)
                    self.assertTrue(sales_data[date][beer]["quantity"],
                                    int)
                # when the beer doesn't exist for a set date.
                except KeyError:
                    pass

    def test_sales_summary_dict(self):
        """
        test_sales_summary_dict
        :return:
        """
        sales_summary = sales_predictor.sales_summary
        self.assertTrue(sales_summary, dict)
        self.assertTrue(sales_summary["sales_last_year"], int)
        for period in sales_summary:
            if period != "sales_last_year":
                for beer in sales_predictor.beers:
                    try:
                        self.assertTrue(sales_summary[period][beer],
                                        int)
                    except KeyError:
                        pass

    def test_increasing_growth_rate(self):
        """
        test_increasing_growth_rate
        :return:
        """
        monthly_growth_rate = sales_predictor.calculate_growth_rate(
            sales_predictor.months)
        weekly_growth_rate = sales_predictor.calculate_growth_rate(
            sales_predictor.weeks)
        for beer in sales_predictor.beers:
            self.assertGreater(monthly_growth_rate[beer], 0)
            self.assertGreater(weekly_growth_rate[beer], 0)


    def test_sales_predictions(self):
        """
        test_sales_predictions
        :return:
        """
        for month in sales_predictor.months:
            current_month = sales_predictor.total_month_beers_qty(
                month)
            predict_month = sales_predictor.predict_month_beer_qty(
                month)
            for element in current_month:
                self.assertGreaterEqual(predict_month[element],
                                        current_month[element])


class TestBrewProcess(unittest.TestCase):
    """
    TestBrewProcess
    """
    def test_tank(self):
        """
        test_tank
        :return:
        """
        tanks = brew_process.tank_status()
        for tank in tanks:
            self.assertTrue(tank, str)
            self.assertTrue(tanks[tank]["volume"], int)
            try:
                self.assertTrue(tanks[tank]["used_capacity"], int)
            except AssertionError:
                pass
            self.assertTrue(tanks[tank]["capability"], list)
            for element in tanks[tank]["capability"]:
                self.assertTrue(element, str)

    def test_tank_allocation(self):
        """
        test_tank_allocation
        :return:
        """
        brew_process.create_process_for_beer(200, "Organic Red Helles",
                                             2000)
        brew_process.start_process_for_beers()
        brew_process.move_process_to_next_state(200,
                                                "Organic Red Helles",
                                                2000)
        brew_process.start_process_for_beers()
        brew_process.start_process_for_beers()
        beer_process_status = brew_process.status_process_for_beer()
        for beer_key in beer_process_status:
            tanks = brew_process.tank_status()
            self.assertEqual(
                tanks[beer_process_status[beer_key]["process_tank"]
                      ["fermentation"]["tank_name"]]["used_capacity"],
                1000)
        brew_process.move_process_to_next_state(200,
                                                "Organic Red Helles",
                                                2000)
        brew_process.start_process_for_beers()
        brew_process.start_process_for_beers()
        beer_process_status = brew_process.status_process_for_beer()
        for beer_key in beer_process_status:
            tanks = brew_process.tank_status()
            self.assertEqual(
                tanks[beer_process_status[beer_key]["process_tank"]
                      ["conditioning"]["tank_name"]]["used_capacity"],
                1000)
        brew_process.move_process_to_next_state(200,
                                                "Organic Red Helles",
                                                2000)
        brew_process.start_process_for_beers()
        brew_process.start_process_for_beers()
        beer_process_status = brew_process.status_process_for_beer()
        for beer_key in beer_process_status:
            self.assertEqual(beer_process_status[beer_key]["gyle_no"],
                             200)
            self.assertEqual(beer_process_status[beer_key]
                             ["beer_name"], "Organic Red Helles")
            self.assertEqual(beer_process_status[beer_key]
                             ["quantity"], 2000)
            self.assertTrue(beer_process_status[beer_key]
                            ["process_tank"], dict)
            self.assertEqual(beer_process_status[beer_key]
                             ["process_tank"]["hot_brew"]["tank_name"],
                             "Kettle")
            self.assertEqual(beer_process_status[beer_key]
                             ["process_tank"]["fermentation"]
                             ["tank_name"], "Albert")
            self.assertEqual(beer_process_status[beer_key]
                             ["process_tank"]["conditioning"]
                             ["tank_name"], "Albert")
            self.assertEqual(beer_process_status[beer_key]
                             ["process_tank"]["bottling"]["tank_name"],
                             "bottling")


if __name__ == '__main__':
    unittest.main()
