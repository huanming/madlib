import subprocess
import OSTools as AbstractTools

class Tools(AbstractTools):
    def clearBufferCache():
        subprocess.Popen('sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"',shell=True
            ,stdin=subprocess.PIPE).communicate()
