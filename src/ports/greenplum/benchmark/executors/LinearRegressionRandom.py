from benchmark import Timer, properties_and_attributes

class Executor:
    """
    Greenplum linear-regression test with random data
    """
    
    @staticmethod
    def natural_number(string):
        value = int(string)
        if value <= 0:
            raise argparse.ArgumentTypeError("%r is not a positive integer" %
                string)
        return value
    
    def __init__(self, controller, logger):
        env = controller.env
        from argparse import ArgumentParser
        parser = ArgumentParser(
            description="Linear Regression on Greenplum", prog = env.prog + 
                ' [...] ' + env.benchmark)
        parser.add_argument("--ivariables", type = Executor.natural_number,
            required = True)
        parser.add_argument("--rows", type = Executor.natural_number,
            required = True)
        parser.parse_args(args = env.args, namespace = env)
        self.env = env
        self.controller = controller
        self.logger = logger
        
    
    def generatorPath():
        return postgresGenerator(runParameters.name)
    
    def load(self):
        timer = Timer()
        env = self.env
        postgresGenerator = env.generator_path_for('postgres', env.benchmark)
        with timer:
            result = self.controller.runSQL(
                """
                CREATE READABLE EXTERNAL WEB TABLE pg_temp.data (
                    x DOUBLE PRECISION[],
                    y DOUBLE PRECISION
                )
                EXECUTE '{theGenerator} --ivariables {ivariables} --rows {rows} --table-seed $GP_SEGMENT_ID --table'
                ON ALL
                FORMAT 'TEXT';
                
                DROP TABLE IF EXISTS {target_base_name}_data CASCADE;
                CREATE TABLE {target_base_name}_data AS
                SELECT * FROM pg_temp.data
                DISTRIBUTED RANDOMLY;
                
                DROP EXTERNAL TABLE pg_temp.data;
                """.format(theGenerator = postgresGenerator,
                    **properties_and_attributes(env))
            )
            result = result + self.controller.runSQL(
                """
                CREATE EXTERNAL WEB TABLE pg_temp.model (
                    coef DOUBLE PRECISION[]
                )
                EXECUTE '{theGenerator} --ivariables {ivariables} --coef'
                ON MASTER
                FORMAT 'TEXT';
                
                DROP TABLE IF EXISTS {target_base_name}_model CASCADE;
                CREATE TABLE {target_base_name}_model AS
                SELECT * FROM pg_temp.model;
                
                DROP EXTERNAL TABLE pg_temp.model;
                """.format(theGenerator = postgresGenerator,
                    **properties_and_attributes(env))
            )
        self.logger.log(timer.elapsed, result)
        
    def run(self):
        timer = Timer()
        env = self.env
        with timer:
            result = self.controller.runSQL(
                r"""
                \x
                SELECT (linregr).* FROM (
                    SELECT {madlib_schema}.linregr(y,x)
                    FROM {target_base_name}_data
                ) AS q
                """
                .format(**properties_and_attributes(env))
            )
        self.logger.log(timer.elapsed, result)
