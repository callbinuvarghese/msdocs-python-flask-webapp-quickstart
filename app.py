import os
# Added to add azure logging
import logging,sys

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer
from opencensus.trace import config_integration
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

# 
# ...

# SETTING FLASK
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

# SETTING LOGGING
# The following lines to set the logger
# Acquire the logger for a library (azure.mgmt.resource in this example)
logger = logging.getLogger('azure.mgmt.resource')

# Set the desired logging level
logger.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Direct logging output to stdout. Without adding a handler,
# no logging output is visible.
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


print(
    f"Logger enabled for ERROR={logger.isEnabledFor(logging.ERROR)}, "
    f"WARNING={logger.isEnabledFor(logging.WARNING)}, "
    f"INFO={logger.isEnabledFor(logging.INFO)}, "
    f"DEBUG={logger.isEnabledFor(logging.DEBUG)}"
)

# END SETTING LOGGING

# Setting up OpenCensus
APP_NAME="flask-demo"
config_integration.trace_integrations(["requests"])
config_integration.trace_integrations(["logging"])
def callback_add_role_name(envelope):
    """ Callback function for opencensus """
    envelope.tags["ai.cloud.role"] = APP_NAME
    return True
#end 

# Setting up App Insidhts thru OpenCensus
APP_INSIGHTS_KEY=os.environ.get('APP_INSIGHTS_KEY')
if APP_INSIGHTS_KEY:
     print(f'APP_INSIGHTS_KEY={APP_INSIGHTS_KEY}')
else:
    APP_INSIGHTS_KEY="00000000-0000-0000-0000-000000000000"
    print(f'Could not get the environment variable APP_INSIGHTS_KEY; so {APP_INSIGHTS_KEY}')
app_insights_cs = "InstrumentationKey=" + APP_INSIGHTS_KEY
handler = AzureLogHandler(connection_string=app_insights_cs)
handler.add_telemetry_processor(callback_add_role_name)
#logger.setLevel(logging.INFO)
logger.addHandler(handler)
azure_exporter = AzureExporter(connection_string=app_insights_cs)
azure_exporter.add_telemetry_processor(callback_add_role_name)

FlaskMiddleware(
    app, exporter=azure_exporter, sampler=ProbabilitySampler(rate=1.0),
)

tracer = Tracer(exporter=azure_exporter, sampler=ProbabilitySampler(1.0))
# END Setting up OpenCensus 

# Real code starts

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/test1')
def test1():
    print('Request for test1 page received')
    return "My Test App", 200

@app.route('/health')
def health():
    print('Request for health page received')
    return '', 200

@app.route('/ready')
def ready():
    print('Request for ready page received')
    return '', 200

@app.route('/hello', methods=['POST'])
def hello():
   print('hello function called')
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
