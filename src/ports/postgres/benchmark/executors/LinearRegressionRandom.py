from Benchmark import Timer, Environment
import os

def natural_number(string):
    value = int(string)
    if value <= 0:
        raise argparse.ArgumentTypeError("%r is not a positive integer" %
            string)
    return value


class ModuleEnvironment(Environment):
    def __init__(self, env):
        Environment.__init__(self, env)
    
        from argparse import ArgumentParser
        parser = ArgumentParser(
            description="Linear Regression on Greenplum", prog = env.prog + 
                ' [...] ' + env.benchmark)
        parser.add_argument("--ivariables", type = natural_number,
            required = True)
        parser.add_argument("--rows", type = natural_number,
            required = True)
        parser.parse_args(args = env.args, namespace = self)

class Executor:
    """
    Greenplum linear-regression test with random data
    """    
    def __init__(self, controller, logger):
        self.env = ModuleEnvironment(controller.env)
        self.controller = controller
        self.logger = logger
        
    def load(self):
        timer = Timer()
        env = self.env
        postgresGenerator = env.generator_path_for('postgres', env.benchmark)
        with timer:
            cmdCreateData = '''{theGenerator} --ivariables {ivariables} --rows {rows} --table > /tmp/{target_base_name}_data'''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            os.system(cmdCreateData)

            result = self.controller.runSQL(
                '''
                DROP TABLE IF EXISTS {target_base_name}_data CASCADE;
                CREATE  TABLE {target_base_name}_data (
                    x DOUBLE PRECISION[],
                    y DOUBLE PRECISION
                );

                COPY {target_base_name}_data from '/tmp/{target_base_name}_data';
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            )
            cmdCreateModel='''{theGenerator} --ivariables {ivariables} --coef > /tmp/{target_base_name}_model'''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            os.system(cmdCreateModel)
            result = result + self.controller.runSQL(
                '''
                DROP TABLE IF EXISTS {target_base_name}_model CASCADE;
                CREATE TABLE {target_base_name}_model (
                    coef DOUBLE PRECISION[]
                );
	
                COPY {target_base_name}_model from '/tmp/{target_base_name}_model';
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            )

        self.logger.log(self.env, timer.elapsed, result)
        
    def run(self):
        timer = Timer()
        env = self.env
        with timer:
            result = self.controller.runSQL(
                '''
                SELECT (linregr).* FROM (
                    SELECT {madlib_schema}.linregr(y,x)
                    FROM {target_base_name}_data
                ) AS q
                '''
                .format(**env.properties_and_attributes()),
                ['--expanded']
            )
        self.logger.log(self.env, timer.elapsed, result)
