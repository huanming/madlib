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
            description="KMeans on Greenplum", prog = env.prog +
                ' [...] ' + env.benchmark)
        parser.add_argument("--dimensions", type = natural_number,
            required = True)
        parser.add_argument("--rows", type = natural_number,
            required = True)
        parser.add_argument("--centroids", type = natural_number,
            required = True)
        parser.add_argument("--max_iteration", type = natural_number,
            required = True)
        parser.add_argument("--convergence_threshold", type = float,
            required = True)
        parser.add_argument("--distance", type = str,
            required = False, default = 'l2norm')
        parser.add_argument("--init_method", type = str,
            required = True)
        parser.add_argument("--t1", type = str,
            required = False, default = 'NULL')
        parser.add_argument("--t2", type = str,
            required = False, default = 'NULL')
        parser.add_argument("--init_sample_pct", type = float,
            required = False, default = 1)
        parser.parse_args(args = env.args, namespace = self)

class Executor:
    """
    Greenplum k-means test with random data
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
                    position FLOAT[]
                )
                EXECUTE '{theGenerator} --dimensions {dimensions} --rows {rows} --centroids {centroids} --stddev 0.01 -s 10 --table-seed $GP_SEGMENT_ID --table'
                ON ALL
                FORMAT 'TEXT';

                DROP TABLE IF EXISTS {target_base_name}_data CASCADE;
                CREATE TABLE {target_base_name}_data AS
                SELECT row_number() OVER () as pid , pg_temp.data.* FROM pg_temp.data
                DISTRIBUTED RANDOMLY;

                DROP EXTERNAL TABLE pg_temp.data;
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            )
            result = result + self.controller.runSQL(
                '''
                CREATE EXTERNAL WEB TABLE pg_temp.model (
                    centroid FLOAT[]
                )
                EXECUTE '{theGenerator} --dimensions {dimensions} --centroids {centroids} --centroid'
                ON MASTER
                FORMAT 'TEXT';

                DROP TABLE IF EXISTS {target_base_name}_model CASCADE;
                CREATE TABLE {target_base_name}_model AS
                SELECT centroid::{madlib_schema}.svec FROM pg_temp.model;

                DROP EXTERNAL TABLE pg_temp.model;
                '''.format(theGenerator = postgresGenerator,
                    **env.properties_and_attributes())
            )
        self.logger.log(self.env, timer.elapsed, result)

    def run(self):
        timer = Timer()
        env = self.env
        with timer:
            if env.properties_and_attributes()['init_method'] in ('canopy'):
                sql = '''
                    SELECT {madlib_schema}.kmeans
                        ('public.{target_base_name}_data', 'position', 'pid'
                            -- source relation, data_column, id_column
                        , 'canopy', {init_sample_pct}
                            -- init method, init sample pct
                        , {t1}, {t2} , '{distance}'
                            -- t1, t2, distance_metric
                        , {max_iteration}, {convergence_threshold}, True
                            -- max_iteration, convergence_threshold, GOF on
                        , 'public.{target_base_name}_km_points'
                        , 'public.{target_base_name}_km_centroids', True
                            -- output_points, output_centroids, overwrite on
                        , True
                            -- verbose mode
                        );
                    '''

            elif env.properties_and_attributes()['init_method'] in ('random', 'kmeans++'):
                sql = '''
                    SELECT {madlib_schema}.kmeans
                        ('public.{target_base_name}_data', 'position', 'pid'
                            -- source relation, data_column, id_column
                        , '{init_method}', {init_sample_pct}
                            -- init method, init sample pct
                        , {centroids}, '{distance}'
                            -- initial K, distance function
                        , {max_iteration}, {convergence_threshold}, True
                            -- max_iteration, convergence_threshold, GOF on
                        , 'public.{target_base_name}_km_points'
                        , 'public.{target_base_name}_km_centroids', True
                            -- output_points, output_centroids, overwrite on
                        , True
                            -- verbose mode
                        );
                    '''
            else:
                sql = '''
                    SELECT {madlib_schema}.kmeans
                        ('public.{target_base_name}_data', 'position', 'pid'
                            -- source relation, data_column, id_column
                        , 'public.{target_base_name}_model', 'centroid'
                            -- source centroid relation, data_column
                        , '{distance}'
                            --dist_metric
                        , {max_iteration}, {convergence_threshold}, True
                            -- max_iteration, convergence_threshold, GOF test on
                        , 'public.{target_base_name}_km_points'
                        , 'public.{target_base_name}_km_centroids', True
                            -- output_points, output_centroids, overwrite output
                        , True
                            -- verbose mode
                        );
                    '''
        sql = sql.format(**env.properties_and_attributes())
        with timer:
            try:
                result = self.controller.runSQL(sql,['--expanded'])
            except Exception as e:
                result = str(e)
        self.logger.log(self.env, timer.elapsed, result)
