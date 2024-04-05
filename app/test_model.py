# Ravi Patel
# Add basic tests for the Model class


import unittest
from .model import Model


class TestModel(unittest.TestCase):
    def test_from_crowdstrike(self):
        payload = {
            "body": [
                {
                    "_id": "123",
                    "bios_manufacturer": "Manufacturer",
                    "bios_version": "1.0",
                    "hostname": "test-host",
                    'modified_timestamp':{'$date':'2020-01-01T00:00:00.000Z'},
                    'device_policies':[]
                }
            ]
        }
        models = Model.from_crowdstrike(payload)
        self.assertEqual(len(models), 1)
        model = models[0]
        self.assertEqual(model.data_source, "crowdstrike")
        self.assertEqual(model.identifier, "123")
        self.assertEqual(model.bios_info, "Manufacturer 1.0")
        self.assertEqual(model.host_name, "test-host")

    def test_from_qualys(self):
        payload = {
            "body": [
                {
                    "id": "123",
                    "biosDescription": "Manufacturer 1.0",
                    "dnsHostName": "test-host",
                    'lastVulnScan':{'$date':'2020-01-01T00:00:00.000Z'},
                }
            ]
        }
        models = Model.from_qualys(payload)
        self.assertEqual(len(models), 1)
        model = models[0]
        self.assertEqual(model.data_source, "qualys")
        self.assertEqual(model.identifier, "123")
        self.assertEqual(model.bios_info, "Manufacturer 1.0")
        self.assertEqual(model.host_name, "test-host")

if __name__ == "__main__":
    unittest.main()