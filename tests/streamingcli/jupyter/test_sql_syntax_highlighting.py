import os
from unittest import mock
import pytest
from jupyter_core.paths import jupyter_config_dir

from streamingcli.jupyter.sql_syntax_highlighting import SQLSyntaxHighlighting


class TestSQLSyntaxHighlighting:
    """Test custom js contains highlighting code for SQL cells with a decorator when custom js does not exist"""
    def test_add_syntax_highlighting_js_when_customjs_does_not_exist(self):
        jupyter_config_directory = jupyter_config_dir()
        custom_js_path = os.path.join(jupyter_config_directory, 'custom', 'custom.js')
        sql_highlighting = SQLSyntaxHighlighting(['sql_magic1', 'sql_magic2'])
        if os.path.exists(custom_js_path):
            os.remove(custom_js_path)

        sql_highlighting.add_syntax_highlighting_js()

        assert os.path.exists(custom_js_path)
        with open(custom_js_path) as f:
            custom_js_content = f.read()
        assert 'sql_magic1' in custom_js_content
        assert 'sql_magic2' in custom_js_content

    """Test custom js contains highlighting code for SQL cells with a decorator when custom js exists"""
    def test_add_syntax_highlighting_js_when_customjs_exists(self):
        jupyter_config_directory = jupyter_config_dir()
        custom_js_path = os.path.join(jupyter_config_directory, 'custom', 'custom.js')
        user_customjs_content = 'this should not be removed on changing this file'
        if os.path.exists(custom_js_path):
            os.remove(custom_js_path)
            with open(custom_js_path, 'w+') as f:
                f.write(user_customjs_content)
        sql_highlighting = SQLSyntaxHighlighting(['sql_magic1', 'sql_magic2'])

        sql_highlighting.add_syntax_highlighting_js()

        assert os.path.exists(custom_js_path)
        with open(custom_js_path) as f:
            custom_js_content = f.read()
        assert 'sql_magic1' in custom_js_content
        assert 'sql_magic2' in custom_js_content
        # user content should not be removed
        assert user_customjs_content in custom_js_content
