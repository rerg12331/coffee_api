from sqlalchemy import MetaData

# Общий объект metadata для всех таблиц
metadata = MetaData()

from auth.models import * 
from categories_management.models import *  
from product_management.models import *  
from cart.models import *  
from order_management.models import *  
from users_management.models import *