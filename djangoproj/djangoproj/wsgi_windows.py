#activate_this = 'C:/pythonvenv/djangoproj/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read(),dict(__file__=activate_this))

import os
import sys
import site


# Add the site-packages of the chosen virtualenv to work with
#site.addsitedir('C:/pythonvenv/djangoproj/Lib/site-packages')

#sys.path.append('C:/pythonvenv/djangoproj/Scripts')
#^^ is mine

# Add the app's directory to the PYTHONPATH

sys.path.append('C:/ServerRelated/pythonstuff/djangoproj')
sys.path.append('C:/ServerRelated/pythonstuff/djangoproj/djangoproj')

os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoproj.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoprog.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
