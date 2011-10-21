import os
import pkgutil
import re
import subprocess
from Benchmark import Environment

class PSQLError(Exception):
    def __init__(self, returnCode):
        self.returnCode = returnCode
    def __str__(self):
        return "psql failed with error %d." % self.returnCode


def parseConnectionStr(connectionStr):
    """
    @brief Parse connection strings of the form
           <tt>[username[/password]@][hostname][:port][/database]</tt>
    
    Separation characters (/@:) and the backslash (\) need to be escaped.
    @returns A tuple (username, password, hostname, port, database). Fields not
             specified will be None.
    """

    def unescape(string):
        """
        Unescape separation characters in connection strings, i.e., remove first
        backslash from "\/", "\@", "\:", and "\\".
        """
        if string is None:
            return None
        else:
            return re.sub(r'\\(?P<char>[/@:\\])', '\g<char>', string)

    match = re.search(
        r'((?P<user>([^/@:\\]|\\/|\\@|\\:|\\\\)+)' +
        r'(/(?P<password>([^/@:\\]|\\/|\\@|\\:|\\\\)*))?@)?' +
        r'(?P<host>([^/@:\\]|\\/|\\@|\\:|\\\\)+)?' +
        r'(:(?P<port>[0-9]+))?' + 
        r'(/(?P<database>([^/@:\\]|\\/|\\@|\\:|\\\\)+))?', connectionStr)
    return (
        unescape(match.group('user')),
        unescape(match.group('password')),
        unescape(match.group('host')),
        match.group('port'),
        unescape(match.group('database')))


class PlatformEnvironment(Environment):
    def __init__(self, env, controller):
        """
        @brief Initialize platform, given the MADlib benchmark environment
        """
        Environment.__init__(self, env)
        self._controller = controller
        
        from argparse import (ArgumentParser, RawTextHelpFormatter)
        parser = ArgumentParser(
            description="MADlib performance testing (" +    
                env.madlib_version + ", benchmark platform: " + env.platform +
                ")",
            prog = env.prog + ' -p ' + env.platform,
            argument_default = False,
            formatter_class = RawTextHelpFormatter,
            epilog=(
                "FIXME"))
        parser.add_argument("--conn", "-c",
            metavar = "CONNSTR",
            default = '',
            dest = 'connection_string')
        parser.add_argument("--madlib_schema", default = 'madlib')
        parser.add_argument("--target_schema", default = 'madlib_benchmark')
        parser.add_argument("--target_base_name")
        parser.add_argument("--benchmark", "-b",
            metavar = "BENCHMARK",
            required = True,
            choices = [name for (_, name, _) in pkgutil.iter_modules(
                [env.madlib_port_executors_dir])])
        (_, self.args) = parser.parse_known_args(args = env.args,
            namespace = self)
        (self.username, self.password, self.hostname, self.port,
            self.database) = parseConnectionStr(self.connection_string)
    
    @property
    def generator_path(self):
        return self.generator_path_for(self.platform, self.benchmark)

    @property
    def data_dir(self):
        if not hasattr(self, '_data_dir'):
            self._data_dir = self._controller._data_dir()
        return self._data_dir
    
    @property
    def platform_long_version(self):
        if not hasattr(self, '_platform_long_version'):
            self._platform_long_version = self._controller._long_version()
        return self._platform_long_version
    
    @property
    def platform_version(self):
        return re.match(
                r'^\w+\s+(?P<version>\d(\.\d)*)\s+',
                self.platform_long_version
            ).group('version')

class Controller:
    """
    @brief Controller class for PostgreSQL tests
    """

    def __init__(self, env, os_tools, logger):
        self.env = PlatformEnvironment(env, self)
        self.os_tools = os_tools
        self.logger=logger
    
    def _data_dir(self):
        return self.runSQL('''SELECT current_setting('data_directory')''',
            ['--no-align', '--tuples-only'])
    
    def _long_version(self):
        return self.runSQL('''SELECT version()''',
            ['--no-align', '--tuples-only'])

    def stopServer(self):
        subprocess.Popen(['pg_ctl', 'stop', '-D', self.env.data_dir]).wait()
        pass

    def startServer(self):
        subprocess.Popen(['pg_ctl', 'start', '-D', self.env.data_dir]).wait()
        import time
        while True:
            try:
                self.runSQL('select version();')
                break
            except PSQLError as e:
                time.sleep(1)
    
    def runSQL(self, sql, psqlArgs = None):
        """
        @brief Run SQL commands with psql and return output
        """
        env = self.env
        
        # See
        # http://petereisentraut.blogspot.com/2010/03/running-sql-scripts-with-psql.html
        # for valuable information on how to call psql
        cmdLine = ['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1']
        if env.has_property_or_attribute('hostname'):
            cmdLine.extend(['-h', env.hostname])
        if env.has_property_or_attribute('port'):
            cmdLine.extend(['-p', env.port])
        if env.has_property_or_attribute('database'):
            cmdLine.extend(['-d', env.database])
        if env.has_property_or_attribute('user'):
            cmdLine.extend(['-U', env.username])

        environ = dict(os.environ)
        environ['PGOPTIONS'] = '--client-min-messages=warning'
        if env.has_property_or_attribute('password'):
            environ['PGPASSWORD'] = env.password
        
        if psqlArgs != None:
            cmdLine.extend(psqlArgs)

        process = subprocess.Popen(cmdLine, env = environ,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE, stderr = None)
        (stdoutdata, _) = process.communicate(sql)
        
        if process.returncode != 0:
            raise PSQLError(process.returncode)
        
        # Strip trailing newline character
        if stdoutdata[-1:] == '\n':
           stdoutdata = stdoutdata[:-1]
        return stdoutdata
    
    def run(self):
        try:
            packageSubset = __import__(self.env.platform + '.benchmark.executors',
                fromlist=[self.env.benchmark])
            module = getattr(packageSubset, self.env.benchmark)
            executor = module.Executor(self, self.logger)
            executor.load()
            self.stopServer()
            self.os_tools.flush_buffer_cache()
            self.startServer()
            executor.run()
        except PSQLError as e:
            print str(e)
        except:
            raise
