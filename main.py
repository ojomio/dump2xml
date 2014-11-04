from datetime import datetime
import re
import sys
from time import mktime

header = '''
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<?xml-stylesheet type="text/xsl" href="sms.xsl"?>
'''
smses = []
template = '''
<sms protocol="0"
     address="{tel}"
     date="{timestamp}"
     type="{type}"
     subject="null"
     body="{body}"
     toa="null"
     sc_toa="null"
     service_center="null"
     read="1"
     status="-1"
     locked="0"
     readable_date="{readable_date}"
     contact_name="(Unknown)"
/>'''
with open(sys.argv[1]) as input:
    message_in_progress = False
    accum_text = date = direction = from_ = to_ = ''
    for line in input:
        line = line.strip(' ')
        if not re.search(r'\+$', line):
            if message_in_progress:
                message_in_progress = False
                # print('date=%s dir=%s from=%s to=%s' % (date, direction, from_, to_))
                # print(accum_text)

                smses.append(
                    template.format(
                        body=accum_text,
                        type=1 if direction == 'INBOX' else 2,
                        readable_date=date,
                        tel=from_ if direction == 'INBOX' else to_,
                        timestamp=int(mktime(datetime.strptime(re.sub('\..*$', '', date), '%Y-%m-%d %H:%M:%S').timetuple())*1000)
                    )
                )
            continue

        data = re.split(r'\s*\|\s*', line)

        if not data:
            continue

        if data[0] and not message_in_progress:
            message_in_progress = True
            date, direction, from_, to_ = data[:-1]
            accum_text = ''
        if message_in_progress:
            text = data[-1]
            accum_text += re.sub(r'(\\r)?\s*\+$', '', text)

with open(sys.argv[2], 'w') as output:
    output.write(header)
    output.write('<smses count="%d">' % len(smses))
    for sms in smses:
        output.write(sms)
    output.write('</smses>')
