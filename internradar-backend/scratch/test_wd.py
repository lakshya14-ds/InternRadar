import sys
sys.path.append(".")
from app.connectors.workday_connector import WorkdayConnector

connector = WorkdayConnector()
url = connector._build_workday_url("https://wipro.wd3.myworkdayjobs.com/wday/cxs/wipro/WiproJobs/jobs")
print("Result URL:", url)
