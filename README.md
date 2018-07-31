# pid-server

Online shell for PID-Analyzer (https://github.com/Plasmatree/PID-Analyzer)


You probably need to make some changes in PID-Analyzer.py:

1) PID-analyzer uses Python 3. Often Python 2 is installed as part of the unix system. So PID-analyzer can start with a wrong version of Python. Check:

/usr/bin/env python -V

If you see version 2.xx.xx - you need to change the first line of PID-Analyzer.py:

/usr/bin/env python3

2) probably in Linux after this line it is necessary to add:

import matplotlib
matplotlib.use ('Agg')

Also you need to compile https://github.com/cleanflight/blackbox-tools and specify parameter -B as path to blackbox_decode
