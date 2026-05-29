class PipelineError(Exception):
    def __init__(self, node_name: str, message: str, retryable: bool = False):
        self.node_name = node_name
        self.retryable = retryable
        super().__init__(f"[{node_name}] {message}")


class LLMCallError(PipelineError):
    def __init__(self, node_name: str, message: str):
        super().__init__(node_name, message, retryable=True)


class ExternalAPIError(PipelineError):
    def __init__(self, node_name: str, message: str):
        super().__init__(node_name, message, retryable=True)


class ValidationError(PipelineError):
    def __init__(self, node_name: str, message: str):
        super().__init__(node_name, message, retryable=False)
