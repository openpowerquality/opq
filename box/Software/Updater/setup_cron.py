from crontab import CronTab

def main():
    # computer username
    my_cron = CronTab(user='evan')

    for job in my_cron:
        if job.comment == 'run_updater':
            print("hello world")
            my_cron.remove(job)

    command = 'python3 /home/evan/Documents/Code/git/opq/box/Software/Updater/updater.py'
    pipe = ' >> /home/evan/Documents/test.txt'

    job = my_cron.new(command=command+pipe, comment='run_updater')

    job.minute.every(1)

    my_cron.write()

if __name__ == '__main__':
    main()
