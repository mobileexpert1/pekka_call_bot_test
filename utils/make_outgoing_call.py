from twilio.rest import Client
import os
from datetime import datetime


def make_outgoing_call(phone_number):
    ng_url = os.getenv('HOST')
    account_sid = os.getenv('SID')
    auth_token = os.getenv('TOKEN')
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url=f"{ng_url}/handler-outgoing-call",
        to=f"+{phone_number}",
        from_=os.getenv('NUMBER'),
        status_callback=f'{ng_url}/call-status',
        status_callback_event=['completed', 'busy', 'no-answer', 'failed']
    )

    create_data = {
        "phone_number": f"+{phone_number}",
        "sid": call.sid,
        "call_on": str(datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))
    }
    print(create_data)


