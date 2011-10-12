#!/usr/bin/env python
import os
import pkgutil
import sys
import yaml
import time

# Initialization

class Environment(object):
    def __init__(self, parent = None):
        self._parent = parent
    
    def __getattr__(self, attr):
        if self._parent is None:
            raise AttributeError, attr
        else:
            return getattr(self._parent, attr)
    
    def has_property_or_attribute(self, name, isNoneAllowed = False):
        if name in self.__dict__ and (
                isNoneAllowed or self.__dict__[name] is not None):
            return True
        elif name in object.__class__.__dict__:
            if isinstance(object.__class__.__dict__[name], property) and (
                    isNoneAllowed or getattr(object, name) is not None):
                return True
        elif self._parent is None:
            return False
        else:
            return self._parent.has_property_or_attribute(name, isNoneAllowed)        
    
    def properties_and_attributes(self, hidePrivate = True):
        if self._parent is not None:
            theDict = self._parent.properties_and_attributes(hidePrivate)
        else:
            theDict = dict()
       
        # Attributes
        theDict.update((attr, getattr(self, attr))
            for attr in self.__dict__
                if not hidePrivate or attr[0] != '_')
        
        # Properties of superclasses
        for cls in self.__class__.__bases__:
            theDict.update((prop, getattr(self, prop))
                for prop in cls.__dict__
                    if isinstance(cls.__dict__[prop], property))
        
        # Properties
        theDict.update((prop, getattr(self, prop))
            for prop in self.__class__.__dict__
                if isinstance(self.__class__.__dict__[prop], property))
        return theDict


class MADEnvironment(Environment):
    def __init__(self):
        Environment.__init__(self)
        
        self._madlib_benchmark_dir = os.path.dirname(
            os.path.realpath(__file__))
        self._madlib_root_dir = os.path.abspath(
            os.path.join(self.madlib_benchmark_dir, os.pardir))
        config_version = yaml.load(open(
            os.path.join(self.madlib_config_dir, 'Version.yml')))
        self._madlib_version = config_version['version']
        self._all_platforms = [name
            for name in os.listdir(self.madlib_ports_dir)
                if os.path.isfile(os.path.join(
                    self.madlib_ports_dir, name, 'benchmark', 'Controller.py'))]
        
        # Find out operating system for which we have specific code
        # The folder in the ports directory that is the longest prefix of
        # sys.platform will be considered the best match
        os_matches = [name
            for name in os.listdir(self.madlib_ports_dir)
                if sys.platform.startswith(name)]
        os_matches.sort(reverse = True)
        self._os = os_matches[0] if os_matches else None
        
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
    def madlib_os_dir(self):
        return os.path.join(self.madlib_ports_dir, self.os)
    
    @property
    def benchmark_logger_dir(self):
        return os.path.join(self.madlib_benchmark_dir, 'loggers')
        
    def generator_path_for(self, platform, generator):
        if not platform in self._all_platforms:
            raise NameError("'%s' is not a valid platform." % platform)
        return os.path.join(self.madlib_ports_dir, platform, 'benchmark',
            'generators', generator)
    
    @property
    def madlib_version(self):
        return self._madlib_version
       
    @property
    def os(self):
        return self._os

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
    
    @property
    def elapsed(self):
        return self.end - self.start

class Benchmark:
    def __init__(self):
        env = MADEnvironment()

        sys.path.append(env.madlib_ports_dir)
        if env.os:
            package = __import__(env.os + '.benchmark.Tools')
            module = package.benchmark.Tools
        else:
            import OSTools as module
        os_tools = module.Tools()
        
        package = __import__('loggers.' + env.logger)
        module = getattr(package, env.logger)
        logger = module.Logger()
        
        package = __import__(env.platform + '.benchmark.Controller')
        module = package.benchmark.Controller
        self.benchmarkController = module.Controller(env, os_tools, logger)
        
    def run(self):
        self.benchmarkController.run()


def main():
    benchmark = Benchmark()
    benchmark.run()


if __name__ == '__main__':
    main()
