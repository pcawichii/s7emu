# This is a function to receive the status
# of the azure services we use in the relayr
# armstrong project


from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options

def azure_status(servers, services):
    # create webdriver object
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    # get geeksforgeeks.org
    driver.get("https://status.azure.com/en-us/status")

    # Output
    out = {}
    try:
        # Get The Places we need
        our_servers = servers
        server_nums = []

        # Get the columns of the Servers
        headers_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//table[@data-zone-name='europe' and contains(@class, 'region-status-table')]//th/span")))

        # Add the columns to look at
        for ind, val in enumerate(headers_elem):
            if val.get_attribute("innerHTML") in our_servers:
                server_nums.append(ind)


        # Which servers are we using
        our_services = services

        # Look for the server rows
        for service in our_services:
            status = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//table[@data-zone-name='europe']//td[contains(text(),'{}')]/../td/span[1]".format(service))
                )
            )

            # Create the Service Object
            out[service] = {}

            # Add the server status
            for ind, server in enumerate(server_nums):
                out[service][our_servers[ind]] = status[server].get_attribute(
                    'data-label')

    except TimeoutException:
        print("Could not reach azure.status")
        return None

    driver.close()
    return out

def powerbi_status():
    # create webdriver object
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    # get geeksforgeeks.org
    driver.get("https://powerbi.microsoft.com/en-us/support/")

    # Output
    out = {}
    try:

        # Europe Outage
        europe_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(),'Europe')]/../div/span")))

        classes = europe_status.get_attribute('class').split(' ')

        out['europe'] = classes[1]

        # Service Outage
        service_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//p[contains(text(),'Service Outage/Degradation')]/../../../div/div/span"
            )))

        classes = service_status.get_attribute('class').split(' ')

        out['service'] = classes[1]

        # Awareness Outage
        awareness_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//p[contains(text(),'Awareness')]/../../../div/div/span")))

        classes = awareness_status.get_attribute('class').split(' ')

        out['awareness'] = classes[1]


    except TimeoutException:
        print("Could not reach powerbi.status")
        return None

    driver.close()
    return out
