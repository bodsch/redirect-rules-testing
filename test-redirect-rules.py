#!/usr/bin/env python3

from __future__ import print_function

import os
import sys
import json
import yaml
import logging
import pprint

from requests import get
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError

pp = pprint.PrettyPrinter(indent=2)

# -------------------------------------------------------------------------------------------------

STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3
STATE_DEPENDENT=4

# -------------------------------------------------------------------------------------------------

class RedirectTester:
    """
    """

    config_file = "redirect-tests.yml"
    BA_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
    BA_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")

    def run(self):
        """
        """
        self.debug = self._string_to_bool(os.environ.get("REDIRECTS_DEBUG", False))

        logging.captureWarnings(True)

        level = logging.INFO
        if self.debug:
            level = logging.DEBUG
        self._init_logging(level=level)

        data = self._read_tests()
        redirects = data.get("redirects")

        self.test_redirects(redirects)

    def test_redirects(self, redirects):
        """
        """
        result = []

        for redirect in redirects:
            state = True
            source = redirect.get("source")
            expected = redirect.get("expected")
            redirection = expected.get("redirection")

            re = self._request_data(source)

            if re.get("final"):
                final_url = re.get("final").get("url")
                final_code = re.get("final").get("code")
                redirected = len(re.get("redirected"))
                content_type = re.get("content_type", None)

                if expected.get("content_type"):
                    state = expected.get("content_type") == content_type

                if not redirection and redirected > 0:
                    logging.error(f"request '{source}' is redirected (count: {redirected})")
                    logging.error(json.dumps(re, indent=2, sort_keys=False))

                elif int(final_code) == int(expected.get("return_code", 200)) and final_url == expected.get("location", "") and state:
                    logging.info(f"request '{source}' - redirect count {redirected}")
                else:
                    logging.error(f"request '{source}' needs test")
                    if int(final_code) != int(expected.get("return_code", 200)):
                        logging.error(f"   return code {final_code} not excepted")
                    if final_url != expected.get("location", ""):
                        logging.error(f"   location {final_url} not excepted")
                    logging.debug(json.dumps(re, indent=2, sort_keys=False))
            else:
                final_code = int(re.get("code"))
                final_url  = re.get("url")
                content_type = re.get("content_type", None)

                expected_location = expected.get('location', None)
                expected_return_code = int(expected.get('return_code', 200))
                expected_content_type = expected.get("content_type", None)

                if expected_location is None:
                    expected_location = source

                if expected_content_type is not None:
                    state = expected_content_type == content_type

                if final_code == expected_return_code and final_url == expected_location and state:
                    logging.info(f"request '{source}'")
                else:
                    logging.error(f"request '{source}' needs test")
                    if content_type != expected_content_type:
                        logging.error(f"   wrong content_type! get '{content_type}', but expected '{expected_content_type}'")
                    if final_code != expected_return_code:
                        logging.error(f"   wrong return_code! get '{final_code}', but expected '{expected_return_code}'")
                    if final_url != expected_location:
                        logging.error (f"   wrong location! get '{final_url}', but expected '{expected_location}'")

                    logging.debug(json.dumps(re, indent=2, sort_keys=False))

    def _request_data(self, url):
        """
        """
        r = {
            "url": url,
        }
        try:
            # https://realpython.com/python-requests/#the-get-request
            response = get(
                url,
                auth = (
                    self.BA_USERNAME,
                    self.BA_PASSWORD
                )
            )

            content_type = response.headers.get("Content-Type").split(";")[0]

            if response.history:
                redirection = []
                counter = 0
                for resp in response.history:
                    counter = counter+1

                    content_type = resp.headers.get("Content-Type", None)
                    if content_type and ";" in content_type:
                        content_type = content_type.split(";")[0]

                    redirection.append(
                        {
                            "counter": counter,
                            "from_server": resp.headers.get('Server'),
                            "to_url": resp.url,
                            "with_code": resp.status_code,
                            "content_type": content_type,
                            "header": dict(resp.headers)
                        }
                    )
                final = {
                    "url": response.url,
                    "code": response.status_code,
                    "content_type": content_type,
                    "header": dict(response.headers)
                }

                r["redirected"] = redirection
                r["final"] = final
            else:
                r["code"] = response.status_code
                r["content_type"] = content_type

            return r

        except ConnectionRefusedError as e:
            logging.error(f"Failed to establish a new connection: {url}")
            return msg

        except ConnectionError as e:
            msg = f"error fetching data from {url}"
            return msg

        finally:
            logging.captureWarnings(False)

    def _init_logging(self, level):
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            stream=sys.stdout
        )

    def _string_to_bool(self, var):
        """
        """
        if isinstance(var, str) and var == "False":
            return False
        if isinstance(var, int) and var == 0:
            return False

        if isinstance(var, str) and var == "True":
            return True
        if isinstance(var, int) and var == 1:
            return True

    def _read_tests(self):
        """
          Take a list of yaml_files and load them to return back
          to the testing program
        """
        loaded_yaml = []

        try:
            with open(self.config_file, 'r') as fd:
                loaded_yaml.append(yaml.safe_load(fd))
        except IOError as e:
            print('Error reading file', self.config_file)
            raise e
        except yaml.YAMLError as e:
            print('Error parsing file', self.config_file)
            raise e
        except Exception as e:
            print('General error')
            raise e

        return loaded_yaml[0]

q = RedirectTester()

q.run()

