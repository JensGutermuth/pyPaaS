#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import subprocess
import sys

from .. import util
from .simpleprocess import SimpleProcess

upstream = "    server {host}:{port};"

nginx_ssl_config = """
upstream backend_{domain} {{
{upstreams}
}}
server {{
    listen 80 {extra_listen_options};
    listen [::]:80 ipv6only=on {extra_listen_options};
    server_name {domain};
    rewrite ^ https://$server_name$request_uri? permanent;
}}
server {{
    listen 443 {extra_listen_options};
    listen [::]:443 ipv6only=on {extra_listen_options};
    server_name {domain};
    ssl_certificate /etc/ssl/private/httpd/{domain}/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/httpd/{domain}/{domain}.key;
    ssl_session_timeout 5m;
    ssl_dhparam /etc/ssl/private/httpd/dhparam.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security max-age=15768000;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/private/httpd/{domain}/trusted_chain.crt;
    resolver 8.8.8.8 8.8.4.4;
    location / {{
        proxy_pass http://backend_{domain};
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }}
}}
"""  # nopep8 (silence pep8 warning about long lines)

nginx_config = """
upstream backend_{domain} {{
{upstreams}
}}
server {{
    listen 80 {extra_listen_options};
    listen [::]:80 ipv6only=on {extra_listen_options};
    server_name {domain};
    location / {{
        proxy_pass http://backend_{domain};
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }}
}}
"""  # nopep8 (silence pep8 warning about long lines)


class NginxBackend(SimpleProcess, util.HooksMixin):
    config_key = 'run_nginxbackend'

    @property
    def nginx_config_path(self):
        return os.path.expanduser(os.path.join(
            '~/nginx.d/', self.config['domain'] + '.conf'
        ))

    @util.HooksMixin.hook('env')
    def env_hook(self, env, idx, **kwargs):
        env['PORT'] = self.config['start_port'] + idx
        return env

    def start(self):
        super().start()

        util.mkdir_p(os.path.expanduser('~/nginx.d/'))
        try:
            # Remove old broken config
            os.unlink(self.nginx_config_path + '.broken')
        except FileNotFoundError:
            pass

        args = dict(
            domain=self.config['domain'],
            extra_listen_options=self.config.get(
                'extra_listen_options', ''
            ),
            upstreams='\n'.join(
                upstream.format(
                    host='127.0.0.1',
                    port=self.config['start_port'] + i
                ) for i in range(self.config.get('process_count', 1))
            )
        )
        if self.config.get('ssl', True):
            util.replace_file(
                self.nginx_config_path,
                nginx_ssl_config.format(**args)
            )
        else:
            util.replace_file(
                self.nginx_config_path,
                nginx_config.format(**args)
            )
        try:
            subprocess.check_call(['sudo', '/usr/sbin/nginx', '-t'])
        except subprocess.CalledProcessError:
            # That file is probably broken => rename it
            os.rename(
                self.nginx_config_path,
                self.nginx_config_path + '.broken'
            )
            raise RuntimeError('nginx configuration failed')

        subprocess.check_call(['sudo', '/usr/sbin/nginx', '-s', 'reload'])

    def stop(self):
        try:
            os.unlink(self.nginx_config_path)
            subprocess.check_call(['sudo', '/usr/sbin/nginx', '-s', 'reload'])
        except FileNotFoundError:
            pass
        super().stop()

    def destroy(self):
        path = os.path.expanduser('~/services/{}'.format(self.name))
        log_path = os.path.expanduser('~/services/{}/log'.format(self.name))
        if os.path.isdir(path):
            for p in [log_path, path]:
                subprocess.check_call(['svc', '-d', p])
                subprocess.check_call(['svc', '-x', p])
            shutil.rmtree(path)
