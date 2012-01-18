import inspect
import time

class Logger:
    def log(self, env, elapsed, result):
        callingFunction = inspect.stack()[1][3]
        print ("{timestamp}: {operation} completed after {seconds:.3f} seconds "
            "with the following result:").format(
            timestamp = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()),
            operation = env.benchmark + '.' + callingFunction,
            seconds = elapsed
        )
        print result
