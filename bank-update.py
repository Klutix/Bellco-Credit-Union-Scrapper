import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

#https://myaccounts.bellco.org/MyAccountsV2/Transactions


#Chrome Driver Setup
_chrome_options = webdriver.ChromeOptions()
chromedriver = "/home/oem/Desktop/bellco-feedback/chromedriver"
driver = webdriver.Chrome(chromedriver,chrome_options=_chrome_options)


def login_bellco():
    inputElement = driver.find_element_by_id("UserName")
    inputElement.send_keys('USERNAME')
    inputElement = driver.find_element_by_id("Password")
    inputElement.send_keys('PASSWORD')
    inputElement.send_keys(Keys.ENTER)

def get_body_tag_text(): #this enough of a bank statement to work with
    body = driver.find_element_by_tag_name("body")
    return body.text


def navigate_to_bank():
    driver.get('https://myaccounts.bellco.org/MyAccountsV2/Transactions')
    time.sleep(4)  
    login_bellco()

class Transaction:
    def __init__(self,t_type,date,description,account,ammount,credited = None,balance=None,category=None):
        self.type = t_type
        self.date = date
        self.description = description
        self.account = account
        self.ammount = ammount
        self.category = category
        self.balance = balance
        self.credited = credited

def split_transaction_types_from_data(data):
    return data.split('Posted Transactions')

def split_transaction_data(data):
    return data.split('Date:')

def make_transactions_generator(data_arr,t_type,filters=None):
             
    for t in data_arr[1:]:
        #cleanse variables
        ammount     = None
        balance     = None
        credited    = None           
        date        = None
        description = None
        account     = None
        credited    = None
        ammount     = None

        lines = t.split('\n')
        if t_type == 'Pending':
            balance  = None
            credited = None
            ammount  = lines[4]
        else:
            ammount = None
            balance = lines[5]
            credited = lines[4]           
        date = lines[1]
        description = lines[2]
        account = lines[3]
        
        transaction = Transaction(t_type,date,description,account,ammount,credited,balance)
        

        yield transaction
    yield None
                
                

#print("Type:",mypp.type)
#print('Date:',mypp.date)
#print('Desc:',mypp.description)
#print('Acc:',mypp.account)
#print('Cred:',mypp.credited)
#print('Bal:',mypp.balance)
#print('Amm:',mypp.ammount)
#print('Cat:',mypp.category)

def get_daily_spending(body):  
    gen_pending_transactions_objects = None
    gen_posted_transations_objects = None
    pending_trans_objects = []
    posted_trans_objects =  []
    today = []
    point_of_sales = []
    transactions_data = split_transaction_types_from_data(body)

    dateNow = datetime.datetime.now().strftime("%b %d %Y")
    
    if len(transactions_data) > 1:
        pending_transactions_arr = split_transaction_data(transactions_data[0])
        posted_transations_arr = split_transaction_data(transactions_data[1])
        gen_pending_transactions_objects = make_transactions_generator(pending_transactions_arr,'Pending')
        gen_posted_transations_objects   = make_transactions_generator(posted_transations_arr,'Posted')
        current_pen = next(gen_pending_transactions_objects)
        current_post = next(gen_posted_transations_objects)        
        while current_pen:
            pending_trans_objects.append(current_pen)
            current_pen = next(gen_pending_transactions_objects)
        while current_post:
            posted_trans_objects.append(current_post)
            current_post = next(gen_posted_transations_objects)
        todays = list(filter(lambda x : x.date == dateNow ,posted_trans_objects))
        todays.extend(list(filter(lambda x : x.date == dateNow,pending_trans_objects)))      
    elif len(transactions_data) == 1 :
        posted_transations_arr = split_transaction_data(transactions_data[0])
        gen_posted_transations_objects   = make_transactions_generator(posted_transations_arr,'Posted')
        current_post = next(gen_posted_transations_objects)
        posted_trans_objects =  []
        while current_post:
            posted_trans_objects.append(current_post)
            current_post = next(gen_posted_transations_objects)         
        todays = list(filter(lambda x : x.date == dateNow ,posted_trans_objects))
    point_of_sales = list(filter(lambda x : 'Point Of Sale Withdrawal' in x.description ,todays))
    print("Today we have spent: $",str(sum(map(lambda s: float(s.debited[2:]),point_of_sales))))
    print(len(point_of_sales))
#run            
navigate_to_bank()
time.sleep(2)

get_daily_spending(get_body_tag_text())
driver.close()


