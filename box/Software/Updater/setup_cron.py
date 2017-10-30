from crontab import CronTab

def main():
    # computer username
    my_cron = CronTab(user='evan')

    for job in my_cron:
        if job.comment == 'run_updater':
            my_cron.remove(job)

    command = 'python3 /usr/local/bin/updater.py'
    pipe = ' >> /var/log/opq/updater.log'

    job = my_cron.new(command=command+pipe, comment='run_updater')

    job.hour.on(0)
    job.minute.on(0)

    my_cron.write()

if __name__ == '__main__':
    main()
