from .pipeline import AlertPipeline, ConnectionAlertPipeline
from .entities import Fault

__ALL__ = [
    'AlertPipeline',
    'DesconectionAlertPipeline',
    'Fault'
]

""" example:
from alert_manager import AlertPipeline
pipe = AlertPipeline()


pipe.check_hospital(payload)
print(pipe.repo.storage)
"""