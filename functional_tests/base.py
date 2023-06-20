import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.firefox.options import Options

MAX_WAIT = 10


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self) -> None:
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options)
        self.staging_server = os.environ.get("STAGING_SERVER")
        if self.staging_server:
            self.live_server_url = "http://" + self.staging_server

    def tearDown(self) -> None:
        self.browser.quit()

    def get_item_input_box(self):
        return self.browser.find_element(by="id", value="id_text")

    @wait
    def wait_for(self, fn):
        return fn()

    @wait
    def wait_for_row_in_list_table(self, row_text):
        table = self.browser.find_element(by="id", value="id_list_table")
        rows = table.find_elements(by="tag name", value="tr")
        self.assertIn(row_text, [row.text for row in rows])

    @wait
    def wait_to_be_logged_in(self, email):
        self.browser.find_element("link text", "Log out")
        navbar = self.browser.find_element("css selector", ".navbar")
        self.assertIn(email, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element(by="name", value="email")
        navbar = self.browser.find_element(by="css selector", value=".navbar")
        self.assertNotIn(email, navbar.text)
