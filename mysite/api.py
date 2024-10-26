from ninja import NinjaAPI, Schema
from customer.api import router as customer_router
from business.api import router as business_router
api = NinjaAPI()

api.add_router("customer/", customer_router)
api.add_router("business/", business_router)

# @api.get("/hello")
# def hello(request):
#     return "Hello world"