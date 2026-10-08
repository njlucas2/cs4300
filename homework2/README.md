# Movie Theater App
A Django app for browsing and booking movies.

You can view the live site at https://cs4300-sdw7.onrender.com.
Render takes some time to redeploy after a time of inactivity. When it does this, the database restarts completely blank each time.

You can log in using the demo account. The credentials are:
username: demo
password: 1234

If you want to run the project locally, you can run
```bash
python3 -m venv myenv --system-site-packages
source myenv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 0.0.0.0:3000
```

## AI Disclosure
For this assignment, I conferred with Claude AI via claude.ai.

I ran into many challenges while setting up this assignment and used Claude to help quickly figure out the source of my bugs/errors and understand why they happen. I also used Claude to generate the data shown for the demo, as well as the data used in the tests, so that they could accurately match real-world movie data. 

At no point did Claude or other AI agent have direct access to the codebase. I used Claude to write me code snippets which I added to my project one at a time, only some of which were actually included in the final assignment.