# import pytest
# from xprocess import ProcessStarter
#
#
# @pytest.fixture
# def api_server(xprocess):
#     class Starter(ProcessStarter):
#         pattern = "startup complete"
#         args = ['uvicorn', 'main:app']
#         max_read_lines = 12
#
#     logfile = xprocess.ensure("api_server", Starter)
#     conn = "http://localhost:8000"
#     yield conn
#
#     xprocess.getinfo("api_server").terminate()
#
#
# @pytest.fixture
# def setup_api(api_server, scope='session'):
#     pass
