from django.contrib import messages

LEVELS = {
   'W': messages.warning,#  - Warning
   'I': messages.info,   #  - Informational
   'S': messages.success,#  - Success
   'E': messages.error,  #  - Error
   'F': messages.error,  #  - Fatal (code bug)
}

def miner_message(request, mresponse):
    m = mresponse['STATUS'][0]
    msg = m['Msg']
    status = m['STATUS']

    LEVELS[status](request, msg)

    return status in ['S', 'I']
