from app import config
from app import app

#make sure database is most recent version!
from subprocess import call
call(["python", "manage.py", "db", "upgrade"])

app.run(host="0.0.0.0", port=config.PORT, debug=False)


