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
            description="Logistic Regression on Postgres", prog = env.prog +
                ' [...] ' + env.benchmark)
        parser.add_argument("--ivariables", type = natural_number,
            required = True)
        parser.add_argument("--rows", type = natural_number,
            required = True)
        parser.add_argument("--iterations", type = natural_number,
            required = True)
        parser.add_argument("--iterative_algorithm", type = str,
            required = True)

        parser.parse_args(args = env.args, namespace = self)

class Executor:
    """
    Postgres logistic-regression test with random data
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
            cmdCreateData = '''{theGenerator} --ivariables {ivariables} --rows {rows} --table '''\
                .format(theGenerator = postgresGenerator, **env.properties_and_attributes())
            result = self.controller.runSQL(
                '''
                DROP TABLE IF EXISTS {target_base_name}_data CASCADE;
                CREATE  TABLE {target_base_name}_data (
                    x DOUBLE PRECISION[],
                    y BOOLEAN
                );

                COPY {target_base_name}_data from stdin;
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
                , stdinCmd=cmdCreateData
            )
            cmdCreateModel = '''{theGenerator} --ivariables {ivariables} --coef '''\
                .format(theGenerator = postgresGenerator, **env.properties_and_attributes())
            result = result + self.controller.runSQL(
                '''
                DROP TABLE IF EXISTS {target_base_name}_model CASCADE;
                CREATE TABLE {target_base_name}_model (
                    coef DOUBLE PRECISION[]
                );
                COPY {target_base_name}_model from stdin;
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
                , stdinCmd=cmdCreateModel
            )

        self.logger.log(self.env, timer.elapsed, result)

    def run(self):
        timer = Timer()
        env = self.env
        with timer:
            try:
                result = self.controller.runSQL(
                    '''
                    SELECT * FROM {madlib_schema}.logregr('{target_base_name}_data',
                    'y', 'x', {iterations}, '{iterative_algorithm}', 0.001) AS q;'''
                    .format(**env.properties_and_attributes()),
                    ['--expanded']
                )
            except Exception as e:
                result = str(e)
        self.logger.log(self.env, timer.elapsed, result)
