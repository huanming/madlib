from postgres.benchmark.Controller import Controller as PGController

class Controller(PGController):
    """
    @brief Controller class for Greenplum tests
    """

    def __init__(self, env):
        PGController.__init__(self, env)
        
    def setup():
        return PGController.setup().update(
            segments = runSQL(
                """
                SELECT version();
                SELECT count(*) FROM gp_segment_configuration
                WHERE content >= 0 AND role = 'p';
                """
            )
        )
    