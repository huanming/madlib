import os
import pkgutil
import re
import subprocess

from benchmark import has_property_or_attribute

class PSQLError(Exception):
    def __init__(self, returnCode):
        self.returnCode = returnCode
    def __str__(self):
        return "psql failed with error %d." % self.returnCode
        

class Controller:
    """
    @brief Controller class for PostgreSQL tests
    """

    def __init__(self, env):
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
        (_, env.args) = parser.parse_known_args(args = env.args,
            namespace = env)
        (env.username, env.password, env.hostname, env.port,
            env.database) = Controller.parseConnectionStr(env.connection_string)
        self.env = env

    @staticmethod
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
        
    def runSQL(self, sql, psqlArgs = None):
        """
        @brief Run SQL commands with psql and return output
        """
        env = self.env
        
        # See
        # http://petereisentraut.blogspot.com/2010/03/running-sql-scripts-with-psql.html
        # for valuable information on how to call psql
        cmdLine = ['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1']
        if has_property_or_attribute(env, 'hostname'):
            cmdLine.extend(['-h', env.hostname])
        if has_property_or_attribute(env, 'port'):
            cmdLine.extend(['-p', env.port])
        if has_property_or_attribute(env, 'database'):
            cmdLine.extend(['-d', env.database])
        if has_property_or_attribute(env, 'user'):
            cmdLine.extend(['-U', env.username])

        environ = dict(os.environ)
        environ['PGOPTIONS'] = '--client-min-messages=warning'
        if has_property_or_attribute(env, 'password'):
            environ['PGPASSWORD'] = env.password
        
        if psqlArgs != None:
            cmdLine.extend(psqlArgs)

        process = subprocess.Popen(cmdLine, env = environ,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE, stderr = None)
        (stdoutdata, _) = process.communicate(sql)
        
        if process.returncode != 0:
            raise PSQLError(process.returncode)
        return stdoutdata
    
    def setup(self):
        theVersion = self.runSQL(
            """
            SELECT version();
            """
        )
        return dict(version = theVersion)
        
    def run(self, logger):
        try:
            packageSubset = __import__(self.env.platform + '.benchmark.executors',
                fromlist=[self.env.benchmark])
            module = getattr(packageSubset, self.env.benchmark)
            executor = module.Executor(self, logger)
            executor.load()
            executor.run()
        except PSQLError as e:
            print str(e)
        except:
            raise
