from ninja import NinjaAPI, Schema
from ninja_jwt.authentication import JWTAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from customer.api import router as customer_router
from business.api import router as business_router

# api = NinjaAPI(auth=JWTAuth())
api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)

api.add_router("customer/", customer_router)
api.add_router("business/", business_router)


class UserSchema(Schema):
    username: str
    is_authenticated: bool


@api.get("me/", response=UserSchema)
def who(request):
    return request.user
