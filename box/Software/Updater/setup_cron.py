from crontab import CronTab

def main():
    # computer username
    my_cron = CronTab(user='root')

    for job in my_cron:
        if job.comment == 'run_updater':
            my_cron.remove(job)

    command = 'python3 /usr/local/bin/updater.py'
    pipe = ' >> /var/log/opq/updater.log'

    job = my_cron.new(command=command+pipe, comment='run_updater')

    job.day.every(1)

    my_cron.write()

if __name__ == '__main__':
    main()
