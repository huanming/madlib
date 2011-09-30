#!/usr/bin/env python
import os
import pkgutil
import sys
import yaml
import time

# Initialization

class MADEnvironment(object):
    def __init__(self):
        self._madlib_benchmark_dir = os.path.dirname(
            os.path.realpath(__file__))
        self._madlib_root_dir = os.path.abspath(
            os.path.join(self.madlib_benchmark_dir, os.pardir))
        config_version = yaml.load(open(
            os.path.join(self.madlib_config_dir, 'Version.yml')))
        self._madlib_version = config_version['version']
        self._all_platforms = [name
            for name in os.listdir(self.madlib_ports_dir)
                if os.path.isdir(os.path.join(self.madlib_ports_dir, name))]
        
        sys.path.append(os.path.join(self.madlib_root_dir, 'madpack'))
        from argparse import (ArgumentParser, RawTextHelpFormatter)
        
        parser = ArgumentParser(
            description="MADlib performance testing (" +    
                self.madlib_version + ")",
            argument_default = False,
            formatter_class = RawTextHelpFormatter,
            epilog=(
                "Example:\n"
                "madtest -p greenplum -c user@localhost/database -m linear \n\n"
                "madtest performs benchmarks for the specified platform. The "
                "list of options is platform and test-specific."))
        parser.add_argument("--platform", "-p",
            metavar = "PLATFORM",
            choices = [name for (_, name, _) in pkgutil.iter_modules(
                [self.madlib_ports_dir])],
            dest = 'platform')
        parser.add_argument("--logger", "-l",
            metavar = "LOGGER",
            choices = [name for (_, name, _) in pkgutil.iter_modules(
                [self.benchmark_logger_dir])],
            default = 'StdOut',
            dest = 'logger'
            )
        parser.add_argument("--verbose", "-v",
            dest='verbose',
            action='store_true')

        (_, self.args) = parser.parse_known_args(namespace = self)

    @property
    def madlib_root_dir(self):
        return self._madlib_root_dir
        
    @property
    def prog(self):
        return sys.argv[0]
    
    @property
    def madlib_benchmark_dir(self):
        return self._madlib_benchmark_dir
    
    @property
    def madlib_config_dir(self):
        return os.path.join(self.madlib_root_dir, 'config')

    @property
    def madlib_ports_dir(self):
        return os.path.join(self.madlib_root_dir, 'ports')
        
    @property
    def madlib_port_executors_dir(self):
        return os.path.join(self.madlib_ports_dir, self.platform, 'benchmark',
            'executors')
    
    @property
    def benchmark_logger_dir(self):
        return os.path.join(self.madlib_benchmark_dir, 'loggers')
    
    @property
    def generator_path(self):
        return self.generator_path_for(self.platform, self.benchmark)
    
    def generator_path_for(self, platform, generator):
        if not platform in self._all_platforms:
            raise NameError("'%s' is not a valid platform." % platform)
        return os.path.join(self.madlib_ports_dir, platform, 'benchmark',
            'generators', generator)
    
    @property
    def madlib_version(self):
        return self._madlib_version

def has_property_or_attribute(object, name, isNoneAllowed = False):
    if name in object.__dict__ and (
        isNoneAllowed == True or object.__dict__[name] != None):
        return True
    if name in object.__class__.__dict__:
        if isinstance(object.__class__.__dict__[name], property) and (
            isNoneAllowed == True or getattr(object, name) != None):
            return True
    return False
    
def properties_and_attributes(object, hidePrivate = False):
    theDict = dict((attr, getattr(object, attr))
        for attr in object.__dict__
            if hidePrivate == False or attr[0] != '_')
    theDict.update((prop, getattr(object, prop))
        for prop in object.__class__.__dict__
            if isinstance(object.__class__.__dict__[prop], property))
    return theDict

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
    
    @property
    def elapsed(self):
        return self.end - self.start

def main():
    env = MADEnvironment()

    sys.path.append(env.madlib_ports_dir)
    package = __import__(env.platform + '.benchmark.Controller')
    module = package.benchmark.Controller
    benchmarkController = module.Controller(env)
    
    package = __import__('loggers.' + env.logger)
    module = getattr(package, env.logger)
    benchmarkLogger = module.Logger(env)
    
    benchmarkController.run(benchmarkLogger)


if __name__ == '__main__':
    main()
