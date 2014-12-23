# coding=utf-8
from fabric.api import local, abort, settings, env, cd, run
from fabric.colors import *
from fabric.contrib.console import confirm

env.hosts = ["root@tmqdu.com"]
env.password = "Zarpe2014"


def deploy():
    with cd("/mnt/source/tm"):
        print green("将在远程仓库下载代码")
        run("git pull origin master")
        # del pyc
        # run('find /mnt/source/tm/ -name "*.pyc" | xargs rm -rf')

        print green("代码部署成功！！！")