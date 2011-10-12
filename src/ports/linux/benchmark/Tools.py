import subprocess
import OSTools as AbstractTools

class Tools(AbstractTools):
    def clearBufferCache():
        subprocess.Popen(['/proc/sys/vm/drop_caches'],
            stdin=subprocess.PIPE).communicate('3\n')
