from ninja import NinjaAPI, Schema
from ninja_jwt.authentication import JWTAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from business.api import EntryController, QueueController, BusinessController
from customer.api import router as customer_router

# api = NinjaAPI(auth=JWTAuth())
api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


api.add_router("customer/", customer_router)

# register controller in the business
api.register_controllers(EntryController,
                         QueueController,
                         BusinessController)


class UserSchema(Schema):
    username: str
    is_authenticated: bool


@api.get("me/", response=UserSchema)
def who(request):
    return request.user
