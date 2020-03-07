from django.shortcuts import render
from django.views.decorators.http import require_POST
from utilities.jwt import decode_jwt, extract_user_from_header
from json import loads, dumps
from utilities import errors, responses
from reports.models import CitizenReport
from users.models import CustomUser
# Create your views here.


@require_POST
def add_report(request):
    user_id = extract_user_from_header(request)
    latitude = request.POST.get('latitude', None)
    longitude = request.POST.get('longitude', None)
    images = request.POST.get('images', None)
    if not user_id:
        return responses.StandardResponse(error_code=(errors.NOT_AUTHORIZED[0], 'The JWT authorization is missing, please provide JWT in the headers as per the docs')).json()

    if not latitude or not longitude:
        return responses.StandardResponse(error_code=(errors.INVALID_PARAMS[0], 'The latitude or longitude are missing')).json()
    try:
        images = loads(images)
    except Exception:
        return responses.StandardResponse(error_code=(errors.INVALID_PARAMS[0], 'The images are missing or not formatted properly. Please send a JSON-encoded string of array of URLs')).json()
    try:
        report = CitizenReport(
            citizen=CustomUser.objects.get(pk=int(user_id)),
            latitude=latitude,
            longitude=longitude,
            images=dumps(images),
            status='unread'
        )
        report.save()
    except Exception:
        return responses.StandardResponse(error_code=errors.SOMETHING_WENT_WRONG).json()
    return responses.SuccessResponse(action_name='ADD_REPORT').json()
