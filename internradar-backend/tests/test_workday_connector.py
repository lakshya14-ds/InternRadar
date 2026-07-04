import pytest

from app.connectors.workday_connector import WorkdayConnector


@pytest.fixture()
def connector() -> WorkdayConnector:
    return WorkdayConnector()


class TestWorkdayUrlBuilder:
    def test_builds_url_for_board_only(self, connector: WorkdayConnector):
        assert connector._build_workday_url(
            "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs"
        ) == "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys"

    def test_builds_url_with_external_path(self, connector: WorkdayConnector):
        assert connector._build_workday_url(
            "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs",
            "/en-US/Infosys/details/12345"
        ) == "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys/details/12345"

    def test_builds_url_with_external_path_without_leading_slash(self, connector: WorkdayConnector):
        assert connector._build_workday_url(
            "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs",
            "en-US/Infosys/details/12345"
        ) == "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys/details/12345"

    def test_builds_url_from_api_path(self, connector: WorkdayConnector):
        assert connector._build_workday_url(
            "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs",
            "/wday/cxs/infosys/Infosys/jobs/details/12345"
        ) == "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys/details/12345"

    def test_preserves_absolute_external_path(self, connector: WorkdayConnector):
        assert connector._build_workday_url(
            "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs",
            "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys/details/12345"
        ) == "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys/details/12345"

    def test_builds_url_for_job_with_no_external_path(self, connector: WorkdayConnector):
        assert connector._build_workday_url(
            "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs",
            ""
        ) == "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys"
