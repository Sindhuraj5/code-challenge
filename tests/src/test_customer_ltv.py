import unittest
from src.customer_ltv import Datawarehouse, Customer, Order, SiteVisit, Image

class TestDataWareHouse(unittest.TestCase):
    def setUp(self) -> None:
        self.datawarehouse = Datawarehouse()
        self.sample_customer = Customer("CUSTOMER", "NEW", "96f55c7d8f42", "2017-01-06T12:46:46.384Z", "Smith", "Middletown","AK")
        self.sample_order = Order("ORDER", "NEW", "68d84e5d1a43", "2017-01-06T12:46:46.384Z", "96f55c7d8f42", "10.00 USD")
        self.sample_visit = SiteVisit("SITE_VISIT", "NEW", "ac05e815602f", "2017-01-06T12:46:46.384Z", "96f55c7d8f42", [])
        self.sample_image = Image("IMAGE", "UPLOAD", "d8ede43b1d1f", "2017-01-06T12:46:46.384Z", "96f55c7d8f42", "EOS 80D")

    def test_add_customer(self):
        self.datawarehouse.add_customer(self.sample_customer)
        self.assertIn("96f55c7d8f42", self.datawarehouse.Customers)
        self.assertEqual(self.sample_customer, self.datawarehouse.Customers["96f55c7d8f42"])

        assert len(self.datawarehouse.Customers) == 1

    def test_add_order(self):
        self.datawarehouse.add_order(self.sample_order)
        self.assertIn("68d84e5d1a43", self.datawarehouse.Orders)
        self.assertEqual(self.sample_order, self.datawarehouse.Orders["68d84e5d1a43"])

        assert len(self.datawarehouse.Orders) == 1

    def test_add_image(self):
        self.datawarehouse.add_image(self.sample_image)
        self.assertIn("d8ede43b1d1f", self.datawarehouse.Images)
        self.assertEqual(self.sample_image, self.datawarehouse.Images["d8ede43b1d1f"])

        assert len(self.datawarehouse.Images) == 1

    def test_add_visit(self):
        self.datawarehouse.add_visit(self.sample_visit)
        self.assertIn("ac05e815602f", self.datawarehouse.Sitevisits)
        self.assertEqual(self.sample_visit, self.datawarehouse.Sitevisits["ac05e815602f"])

        assert len(self.datawarehouse.Sitevisits) == 1

    def test_calculate_ltv_with_no_orders(self):
        self.datawarehouse.add_customer(self.sample_customer)
        ltv = self.datawarehouse.calculate_ltv()
        self.assertEqual(ltv[self.sample_customer.key],0)