import os

import yaml
from jinja2 import Template


def jinja2it(fr, fw, kwargs):
  template = Template(fr.read())
  fw.write(template.render(**kwargs))


def main():
  with open('config.yml') as f:
    config = yaml.load(f)
  jvars = {
    'auth_header': config['auth']['header'],
    'auth_secret': config['auth']['secret'],
    'max_name_length': config['server']['max_name_length'],
    'database': config['server']['database'],
    'url': config['server']['url'],
    'server_name': config['server']['host'],
    'tmpfile_path': config['deploy']['tmpfile_path'],
    'user': config['deploy']['user'],
    'group': config['deploy']['group'],
    'pidfile': '{}/pid'.format(config['deploy']['tmpfile_path']),
    'working_directory': config['deploy']['working_directory'],
    'gunicorn_path': '{}/venv/bin/gunicorn'.format(config['deploy']['working_directory']),
    'socketfile': '{}/socket'.format(config['deploy']['tmpfile_path']),
    'errorlog': '{}/logs/error.log'.format(config['deploy']['working_directory']),
    'stdlog': '{}/logs/stdout.log'.format(config['deploy']['working_directory']),
    'pem_path': config['deploy']['ssl']['pem'],
    'key_path': config['deploy']['ssl']['key']
  }

  for root, dirs, files in os.walk('.'):
    files = [f for f in files if not f.startswith('.') and f.endswith('.j2')]
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']

    for f in files:
      with open(os.path.join(root, f)) as fr, open(os.path.join(root, f[:-3]), 'w') as fw:
        jinja2it(fr, fw, jvars)


if __name__ == '__main__':
  main()
