# coding=utf-8
from fabric.api import local, abort, settings, env, cd, run
from fabric.colors import *
from fabric.contrib.console import confirm

env.hosts = ["root@tmqdu.com"]
env.password = "Zarpe092122302"


def deploy():
    with cd("/mnt/source/tm"):
        print green("将在远程仓库下载代码")
        run("git pull origin master")
        r = raw_input("Rebuild db?")
        if r == "y":
            run("sh tools/restore.sh")
        # del pyc
        # run('find /mnt/source/tm/ -name "*.pyc" | xargs rm -rf')

        print green("代码部署成功！！！")