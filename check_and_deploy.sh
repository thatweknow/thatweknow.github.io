##!/bin/bash
#0 */6 * * * /bin/bash -c 'if [ "$(ls -A /Users/admin/my-project/biturd-gp/data/blog)" ]; then if ! myhexo d; then /usr/bin/python3 /Users/admin/script-tool/bin/send_email.py; fi; fi'  >> /Users/admin/my-project/biturd-gp/crontab.log 2>&1