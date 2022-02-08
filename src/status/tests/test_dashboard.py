# import pytest
# import lib.power_bi_dashboard as power
# import lib.plc as plc
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# import json

# def test_measurements_end_to_end():
#     measurements = []
#     f = open("init.json")
#     data = json.load(f)
#     firefox_options = Options()
#     firefox_options.add_argument("--headless")

#     driver = webdriver.Firefox()
#     driver.get(data["powerbi"]["url"], options=firefox_options)

#     for i in measurements:
#         plc_val = plc.value_at_plc(i)
#         power_bi = power.value_at_dashboard(driver, i)
#         converted = (plc_val * 9 / 5) + 32
#         assert converted == power_bi
