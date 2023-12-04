import json
from datetime import datetime
import pytz

class Customer:
    def __init__(self, type:str, verb:str, key:str, event_time: datetime, last_name: str = '',
                adr_city:str = '', adr_state:str = ''):
        # object for customer
        self.type = type
        self.verb = verb
        self.key = key
        self.event_time = event_time
        self.last_name = last_name
        self.adr_city = adr_city
        self.adr_state = adr_state

class Order:
    def __init__(self, type:str, verb:str, key:str, event_time: datetime, customer_id: str,
                total_amount:str):
        # object for Order
        self.type = type
        self.verb = verb
        self.key = key
        self.event_time = event_time
        self.customer_id = customer_id
        self.total_amount = total_amount

class SiteVisit:
    def __init__(self, type:str, verb:str, key:str, event_time: datetime, customer_id: str,
                tags:list = []):
        # object for visits
        self.type = type
        self.verb = verb
        self.key = key
        self.event_time = event_time
        self.customer_id = customer_id
        self.tags = tags

class Image:
    def __init__(self, type:str, verb:str, key:str, event_time: datetime, customer_id: str,
                camera_make:str = '', camera_model:str = ''):
        # object for image
        self.type = type
        self.verb = verb
        self.key = key
        self.event_time = event_time
        self.customer_id = customer_id
        self.camera_make = camera_make
        self.camera_model = camera_model

class Datawarehouse:
    def __init__(self):
        # holds dictionary of customers, orders, images and visits
        self.Customers = {}
        self.Orders = {}
        self.Sitevisits = {}
        self.Images = {}

    def ingest(self,records):
        #loop through each event and create the corresponding object depending on type
        #and add the object to the datawarehouse dictionary

        for record in records:
            if 'type' in record: 
                if record['type'] == "CUSTOMER": 
                    if 'verb' in record and 'key' in record and 'event_time' in record:
                        customer = Customer(record['type'], record['verb'], record['key'],
                                            record['event_time'], record.get('last_name',''),
                                            record.get('adr_city',''),
                                            record.get('adr_state',''))
                        datawarehouse.add_customer(customer)
                    else:
                        print("Event doesn't have required fields and hence ignored")
                elif record['type'] == "ORDER":
                    if 'verb' in record and 'key' in record and 'event_time' in record and 'customer_id' in record and 'total_amount' in record:
                        order = Order(record['type'], record['verb'], record['key'],
                                            record['event_time'], record['customer_id'],
                                            record['total_amount'])
                        datawarehouse.add_order(order)
                    else:
                        print("Event doesn't have required fields and hence ignored")
                elif record['type'] == "SITE_VISIT":
                    if 'verb' in record and 'key' in record and 'event_time' in record and 'customer_id' in record:
                        visit = SiteVisit(record['type'], record['verb'], record['key'],
                                            record['event_time'], record['customer_id'],
                                            record.get('tags',[]))
                        datawarehouse.add_visit(visit)
                    else:
                        print("Event doesn't have required fields and hence ignored")
                elif record['type'] == "IMAGE":
                    if 'verb' in record and 'key' in record and 'event_time' in record and 'customer_id' in record:
                        image = Image(record['type'], record['verb'], record['key'],
                                            record['event_time'], record['customer_id'],
                                            record.get('camera_make',''), record.get('camera_model',''))
                        datawarehouse.add_image(image)
                    else:
                        print("Event doesn't have required fields and hence ignored")
                else:
                    print(f"Event Type {record['type']} not recognizable. Skipping record")
            else: # event dict doesn't have key 'type'
                print(f" Event json doesn't have key 'type'")
                break

    def add_customer(self, customer):
        # add customer to datawarehouse customer dictionary with customer id as dict key
        # if type == "UPDATE", all values will be automatically replaced on dictionary
        self.Customers[customer.key] = customer

    def add_order(self, order):
        # add order to datawarehouse order dictionary with order id as dict key
        # if type == "UPDATE", all values will be automatically replaced on dictionary
        self.Orders[order.key] = order

    def add_visit(self, visit):
        # add visit to datawarehouse visit dictionary with visit id as dict key
        self.Sitevisits[visit.key] = visit

    def add_image(self, image):
        # add image to datawarehouse customer dictionary with image id as dict key
        self.Images[image.key] = image

    def get_customer_orders(self, cust_key):
        # get all orders for a customer in list
        cust_order_list = []
        for order_key, order in self.Orders.items():
            if order.customer_id == cust_key:
                cust_order_list.append(order)
        return cust_order_list
    
    def get_customer_visits(self, cust_key):
        #get all visits for a customer in list
        cust_visit_list = []
        for visit_key, visit in self.Sitevisits.items():
            if visit.customer_id == cust_key:
                cust_visit_list.append(visit)
        return cust_visit_list
    
    def calculate_total_amount(self, cust_order_list):
        # calculate total amount for all orders for a customer
        total_amount = 0
        for cust_order in cust_order_list:
            # amount is in the format "10 USD". split and check if first part is float or integer
            amount = cust_order.total_amount.split()
            if amount[0]:
                if float(amount[0]) or int(amount[0]):
                    total_amount+= float(amount[0])
    
        return total_amount
    
    def get_weekly_visits(self, cust_visit_list):
        # get count of weekly visits for a customer
        weekly_visits = {}
        for cust_visit in cust_visit_list:
            customer_id = cust_visit.customer_id

            try:
                #to convert event time in string to datetime object
                datetime_object = datetime.strptime(cust_visit.event_time,"%Y-%m-%dT%H:%M:%S.%fZ")
                #get week number and year of the event
                week_number = datetime_object.strftime("%U")
                year = datetime_object.year

                # create a dict with count of weekly visits with key as a tuple of customer id,week and year
                week_key = (customer_id,week_number,year )
                if week_key in weekly_visits:
                    weekly_visits[week_key] += 1
                else:
                    weekly_visits[week_key] = 1
            except:
                pass
            
        return weekly_visits

    def calculate_ltv(self):
        customers_ltv = {}
        #iterate over customers in customer dictionary to calculate ltv for each customer
        for cust_key, cust_value in self.Customers.items():
            # get orders and visits for the customer
            cust_order_list = self.get_customer_orders(cust_key)
            cust_visit_list = self.get_customer_visits(cust_key)

            # calculate total order for each customer
            cust_total_amount = self.calculate_total_amount(cust_order_list)
            
            # get visits by each week for each customer
            cust_weekly_visits = self.get_weekly_visits(cust_visit_list)
            
            #get total visit count
            total_visit_count = sum(cust_weekly_visits.values())

            #get total visit count
            total_visit_count = sum(cust_weekly_visits.values())

            #calculate ltv
            t = 10
            ltv = 0
            try:
                ltv = 52*t*((cust_total_amount/total_visit_count))*(total_visit_count/len(cust_weekly_visits))
            except ZeroDivisionError:
                pass

            customers_ltv[cust_key] = ltv
        return customers_ltv
    
    def TopXSimpleLTVCustomers(self, n, customers_ltv):
        # sort dictionary by ltv value and return top n
        sorted_ltv = sorted(customers_ltv, key = customers_ltv.get, reverse=True)
        return {k: customers_ltv[k] for k in sorted_ltv[:n] if k in customers_ltv}
    


if __name__ == '__main__':

    #create object for datawarehouse class
    datawarehouse = Datawarehouse()

    input_dir = './input/input.txt'
    try:
        with open(input_dir,'r') as f:
            data = f.read()
            # load data into a list of dictionaries
            records = json.loads(data)
    except FileNotFoundError:
        raise FileNotFoundError("Input File not found")
    
    #ingest events into datawarehouse class with dictionaries for each type
    datawarehouse.ingest(records)

    customers_ltv = datawarehouse.calculate_ltv()
    n = 10
    print(datawarehouse.TopXSimpleLTVCustomers(n, customers_ltv))

    #with open('../../output/output.txt', 'w') as output_file:
    try:
        with open('./output/output.txt', 'w') as output_file:
            output = json.dumps(
                customers_ltv,
                indent=2,
                separators=(',', ': '))
            output_file.write(output)
    except:
        print("Output error")

