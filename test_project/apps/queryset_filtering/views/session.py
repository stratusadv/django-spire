from django_spire.contrib.session.base_session import BaseSession


class TaskListFilterSession(BaseSession):
    session_key = 'task_list_filter'