from imsms_analysis.events.event import Event


# Useful for logging, debugging, grabbing data for external tools,
# or making plots across multiple configurations
class AnalysisCallbacks:
    # These events are called by the framework while an analysis is in progress
    # To link these events, call Event.register() with a function matching the
    # corresponding prototype.
    def __init__(self):
        # f(configs: AnalysisConfig[])
        self.batch_info = Event()
        # f(config: AnalysisConfig)
        self.start_analysis = Event()
        # f(config: AnalysisConfig,
        #   next_step: NamedFunctor,
        #   state: PipelineState,
        #   mode: str)
        self.before_preprocess_step = Event()
        # f(config: AnalysisConfig,
        #   last_step: NamedFunctor,
        #   state: PipelineState,
        #   mode: str)
        self.after_preprocess_step = Event()
