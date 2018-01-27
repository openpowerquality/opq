from crontab import CronTab

def main():
    # computer username
    my_cron = CronTab(user='root')

    for job in my_cron:
        if job.comment == 'run_updater':
            my_cron.remove(job)

    command = '/usr/bin/python3 /usr/local/bin/box_updater.py'
    pipe = ' &>> /var/log/opq/box_updater.log'

    job = my_cron.new(command=command+pipe, comment='run_updater')

    job.hour.on(0)
    job.minute.on(0)

    my_cron.write()

if __name__ == '__main__':
    main()
