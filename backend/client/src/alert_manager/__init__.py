from .pipeline import AlertPipeline, ConnectionAlertPipeline

__ALL__ = [
    'AlertPipeline',
    'DesconectionAlertPipeline'
]

""" example:
from alert_manager import AlertPipeline
pipe = AlertPipeline()


pipe.check_hospital(payload)
print(pipe.repo.storage)
"""