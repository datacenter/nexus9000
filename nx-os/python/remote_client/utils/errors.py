class cli_syntax_error(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)

class cmd_exec_error(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)

class structured_output_not_supported_error(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)

class data_type_error(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)