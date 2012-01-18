import subprocess
from OSTools import Tools as AbstractTools

class Tools(AbstractTools):
    def flush_buffer_cache(self):
        print "*** Flushing and emptying Mac OS X disk caches ***"
        subprocess.Popen(['purge']).wait()
