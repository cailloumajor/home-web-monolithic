import multiprocessing

proc_name = 'home_web'
workers = multiprocessing.cpu_count() * 2 + 1
bind = 'unix:/tmp/home_web_gunicorn.sock'
pidfile = '/run/gunicorn/home_web.pid'
errorlog = '-'
