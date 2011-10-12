import re
import subprocess
from postgres.benchmark.Controller import Controller as PGController
from postgres.benchmark.Controller import PlatformEnvironment \
    as PGPlatformEnvironment

class PlatformEnvironment(PGPlatformEnvironment):
    def __init__(self, env, controller):
        PGPlatformEnvironment.__init__(self, env, controller)

    @property
    def platform_version(self):
        return re.search(r'\(Greenplum\s+Database\s+(?P<version>\d(\.\d)*)[^\d.]',
                self.platform_long_version
            ).group('version')
    
    @property
    def num_segments(self):
        if not hasattr(self, '_num_segments'):
            self._num_segments = self._controller._num_segments()
        return self._num_segments

class Controller(PGController):
    """
    @brief Controller class for Greenplum tests
    """

    def __init__(self, env, os_tools, logger):
        # Note: We do not call the super constructor here because we use our own
        # PlatformEnvironment
        self.env = PlatformEnvironment(env, self)
        self.os_tools = os_tools
        self.logger = logger
    
    def _num_segments(self):
        return int(self.runSQL('''
                SELECT count(*) FROM gp_segment_configuration
                WHERE content >= 0 AND role = 'p';
            ''',
            ['--no-align', '--tuples-only']))
    
    def stopServer(self):
        print "\n\n*** Stopping Greenplum server ***\n\n"
        if subprocess.Popen(['gpstop', '-a', '-d', self.env.data_dir]).wait() != 0:
            raise EnvironmentError, "Greenplum server could not be stopped"
        print "\n\n*** Greenplum server successfully stopped ***\n\n"

    def startServer(self):
        print "\n\n*** Starting Greenplum server ***\n\n"
        if subprocess.Popen(['gpstart', '-a', '-d', self.env.data_dir]).wait() != 0:
            raise EnvironmentError, "Greenplum server could not be restarted"
        print "\n\n*** Greenplum successfuly restarted ***\n\n"

