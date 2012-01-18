from Benchmark import Timer, Environment

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
        self.env.rows = self.env.rows / self.controller._num_segments()
        timer = Timer()
        env = self.env
        postgresGenerator = env.generator_path_for('postgres', env.benchmark)
        with timer:
            result = self.controller.runSQL(
                '''
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
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            )
            result = result + self.controller.runSQL(
                '''
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
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            )
        self.logger.log(self.env, timer.elapsed, result)

    def run(self):
        timer = Timer()
        env = self.env
        with timer:
            try:
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
            except Exception as e:
                result = str(e)
        self.logger.log(self.env, timer.elapsed, result)
