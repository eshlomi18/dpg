"""
created by: Evyatar Shlomi
last updated by: Evyatar Shlomi
date: 30.8.23
clone a python virtualenv to an offline server

pip freeze > installation/requirements.txt       #Creates a file with all required libraries
pip download -r installation/requirements.txt -d installation/wheelfiles      #Downloads all required libraries to offline mode
pip install -r installation/requirements.txt --no-index --find-links installation/wheelfiles      #Downloads the required libraries for in the project
# the last line is the line you need to do in the offline project