#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <linux/fs.h>
#include <linux/errno.h>
#include <linux/types.h>
#include <linux/cdev.h>
#include <linux/version.h>
#include <linux/uaccess.h>

#include <linux/interrupt.h>
#include <linux/gpio.h>
#include <linux/spi/spi.h>

#include <linux/workqueue.h>

///GPIO IRQ Stuff stuff:
#define OPQ_DATA_READY_GPIO 18
#define OPQ_DATA_READY_GPIO_DESC           "Data ready pin for the STM32f3"
#define OPQ_DATA_READY_GPIO_DEVICE_DESC    "OPQBox2"
///Character device stuff
#define OPQ_CYCLE_BUFFER_SIZE 408
#define OPQ_CYCLE_BUFFER_COUNT 10
///SPI
#define OPQ_SPI_BUS 0
#define OPQ_SPI_CHAN 0
#define OPQ_SPI_MAX_SPEED 1953000       //2mhz ish
#define OPQ_SPI_BITS_PER_WORD 8
///UDEV Names
#define OPQ_UDEV_NAME "opq0"

struct opq_frame_buffer {
    struct mutex * mutex;
    struct  semaphore* sem;
    uint8_t data[OPQ_CYCLE_BUFFER_COUNT][OPQ_CYCLE_BUFFER_SIZE];
    size_t writer_pos;
    size_t reader_pos;
};

struct opq_device
{
    //serialize access
    struct cdev cdev;
    //SPI Handle
    struct spi_device  * spi_device;
    //Irq number for data ready pin
    short int irq_any_gpio;
    struct workqueue_struct *wq;
    struct opq_frame_buffer *cycles;
    int int_cnt;
};

struct opq_device * opq_dev;
//UDEV STUFF
static struct class *cl;

//Chardev
dev_t chardevmajor;
static char *opq_devnode(struct device *dev, umode_t *mode);

loff_t opq_chardev_lseek(struct file *file, loff_t offset, int orig);
int opq_chardev_open(struct inode *inode,struct file *filep);
int opq_chardev_release(struct inode *inode,struct file *filep);
ssize_t opq_chardev_read(struct file *filep,char *buff,size_t count,loff_t *offp );
ssize_t opq_chardev_write(struct file *filep,const char *buff,size_t count,loff_t *offp );
ssize_t opq_chardev_buffered_read(struct file *filep,char *buff,size_t count,loff_t *offp );
ssize_t opq_chardev_buffered_write(struct file *filep,const char *buff,size_t count,loff_t *offp );
int opq_init_chardev(void);


//GPIO IRQw
static irqreturn_t opq_gpio_irq_handler(int irq, void *dev_id, struct pt_regs *regs);
int opq_gpio_int_config(void);
void opq_gpio_int_release(void);
//SPI
int opq_init_spi(void);
void opq_release_spi(void);
static void opq_wq_spi_reader_handler(struct work_struct *w);
static DECLARE_WORK(opq_wq_spi_reader, opq_wq_spi_reader_handler);
//Buffer
void opq_circ_buffer_init(void);

void opq_circ_buffer_remove(void);



//IRQ Handler
static irqreturn_t opq_gpio_irq_handler(int irq, void *dev_id, struct pt_regs *regs) {
    opq_dev->int_cnt++;
    queue_work(opq_dev->wq, &opq_wq_spi_reader);
    return IRQ_HANDLED;
}

//This will set up the irq
int opq_init_gpio_int(void) {

    if (gpio_request(OPQ_DATA_READY_GPIO, OPQ_DATA_READY_GPIO_DESC)) {
        printk("OPQ: GPIO request faiure: %s\n", OPQ_DATA_READY_GPIO_DESC);
        return -ENODEV;
    }
    if(gpio_direction_input(OPQ_DATA_READY_GPIO)) {
        printk("OPQ: GPIO configuration faiure: %s\n", OPQ_DATA_READY_GPIO_DESC);
        return -ENODEV;
    }
    if ((opq_dev->irq_any_gpio = gpio_to_irq(OPQ_DATA_READY_GPIO)) < 0 ) {
        printk("OPQ: GPIO to IRQ mapping faiure %s\n", OPQ_DATA_READY_GPIO_DESC);
        return-ENODEV;
    }
    opq_dev->wq = create_workqueue("opq_queue");

    if (request_irq(opq_dev->irq_any_gpio,
                    (irq_handler_t ) opq_gpio_irq_handler,
                    IRQF_TRIGGER_RISING,
                    OPQ_DATA_READY_GPIO_DESC,
                    OPQ_DATA_READY_GPIO_DEVICE_DESC)) {
        printk("OPQ: Irq Request failure\n");
        return -ENODEV;
    }
    printk(KERN_NOTICE "OPQ: interrupt %d ready\n", (int)opq_dev->irq_any_gpio);
    return 0;
}

//This will release the IRQ
void opq_release_gpio_int(void) {
    free_irq(opq_dev->irq_any_gpio, OPQ_DATA_READY_GPIO_DEVICE_DESC);
    gpio_free(OPQ_DATA_READY_GPIO);
    cancel_work_sync(&opq_wq_spi_reader);
    destroy_workqueue(opq_dev->wq);
    return;
}

///SPI stuff

int opq_init_spi(void) {
    struct spi_board_info spi_device_info = {
        .modalias = "opq",
        .max_speed_hz = OPQ_SPI_MAX_SPEED,
        .bus_num = OPQ_SPI_BUS,
        .chip_select = OPQ_SPI_CHAN,
        .mode = 0x0,
    };
    int ret;
    struct spi_master *master;
    master = spi_busnum_to_master( spi_device_info.bus_num );
    if( !master ) {
        printk("OPQ: could not allocate SPI master\n");
        return -ENODEV;
    }

    opq_dev->spi_device = spi_new_device( master, &spi_device_info );
    if( !opq_dev->spi_device ) {
        printk("OPQ: could not allocate SPI device\n");
        return -ENODEV;
    }
    opq_dev->spi_device->bits_per_word = OPQ_SPI_BITS_PER_WORD;
    ret = spi_setup( opq_dev->spi_device );
    printk(KERN_NOTICE "OPQ: spi %d:%d ready\n",OPQ_SPI_BUS,OPQ_SPI_CHAN);
    return 0;
}

void opq_release_spi(void) {
    spi_unregister_device( opq_dev->spi_device );
}

//Bottom half og the IRQ Handler
static void opq_wq_spi_reader_handler(struct work_struct *w) {
    mutex_lock(opq_dev->cycles->mutex);
    spi_read(opq_dev->spi_device, opq_dev->cycles->data[opq_dev->cycles->writer_pos], OPQ_CYCLE_BUFFER_SIZE);
    opq_dev->cycles->writer_pos++;
    if(opq_dev->cycles->writer_pos >= OPQ_CYCLE_BUFFER_COUNT)
        opq_dev->cycles->writer_pos  = 0;
    if(opq_dev->cycles->writer_pos  == opq_dev->cycles->reader_pos) {
        //Reader is not keeping up. Have to evict an item.
        //Note we are not touching the semaphore in this case
        //since number of items has not changed.
        opq_dev->cycles->reader_pos++;
        if(opq_dev->cycles->reader_pos >= OPQ_CYCLE_BUFFER_COUNT)
            opq_dev->cycles->reader_pos  = 0;

    }
    else {
        up(opq_dev->cycles->sem);
    }
    mutex_unlock(opq_dev->cycles->mutex);
    //printk("hello\n");
}
//Chardev

static int opq_chardev_major=-1;
static struct file_operations opq_chardev_fops;

int opq_init_chardev()
{
    opq_chardev_fops.open =  opq_chardev_open;
    opq_chardev_fops.read = opq_chardev_read;
    opq_chardev_fops.write = opq_chardev_write;
    opq_chardev_fops.release = opq_chardev_release;
    opq_chardev_fops.llseek = opq_chardev_lseek;
    if(alloc_chrdev_region (&chardevmajor,0,1,"opq")<0)
    {
        printk("OPQ: couldnt get major/minor number.\n");
        return -1;
    }
    opq_chardev_major=MAJOR(chardevmajor);
    cdev_init ( &opq_dev->cdev, &opq_chardev_fops);
    opq_dev->cdev.owner = THIS_MODULE;
    opq_dev->cdev.ops = &opq_chardev_fops;
    if(cdev_add(&opq_dev->cdev, MKDEV(opq_chardev_major, 0), 1) < 0)
    {
        printk("OPQ: Failed to initialize character device\n");
        return -1;
    }
    printk("OPQ: Initialized character device with major number %d\n", opq_chardev_major);
    return 0;
}

void opq_release_chardev(void)
{
    cdev_del(&opq_dev->cdev);
    unregister_chrdev_region (MKDEV(opq_chardev_major, 0),1);
}

int opq_chardev_open(struct inode *inode,struct file *filep)
{
    printk(KERN_INFO "OPQ: %d opened the pci driver' chr dev\n", current->pid);
    return 0;
}

int opq_chardev_release(struct inode *inode,struct file *filep)
{
    return 0;
}



ssize_t opq_chardev_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos)
{
    if (down_interruptible(opq_dev->cycles->sem))
        return -ERESTARTSYS;
    mutex_lock(opq_dev->cycles->mutex);
    if(count > OPQ_CYCLE_BUFFER_SIZE)
        count = OPQ_CYCLE_BUFFER_SIZE;

    //Read SPI here
    if(copy_to_user(buf, opq_dev->cycles->data[opq_dev->cycles->reader_pos], count) != 0)
    {
        printk("KERN_ERROR" "OPQ: copy to user failed\n");
    }
    opq_dev->cycles->reader_pos++;
    if(opq_dev->cycles->reader_pos >= OPQ_CYCLE_BUFFER_COUNT)
        opq_dev->cycles->reader_pos = 0;
    mutex_unlock(opq_dev->cycles->mutex);
    return count;
}


ssize_t opq_chardev_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos)
{
    return 0;
}

loff_t opq_chardev_lseek(struct file *file, loff_t offset, int orig)
{
    return 0;
}

//Circular buffer stuff
void opq_circ_buffer_init()
{
    opq_dev->cycles = kmalloc(sizeof(struct opq_frame_buffer), GFP_KERNEL);
    opq_dev->cycles->mutex = kmalloc(sizeof(struct mutex), GFP_KERNEL);
    opq_dev->cycles->sem = kmalloc(sizeof(struct semaphore), GFP_KERNEL);
    mutex_init(opq_dev->cycles->mutex);
    sema_init(opq_dev->cycles->sem, 0);
    opq_dev->cycles->writer_pos = 1;
    opq_dev->cycles->reader_pos = 0;
}

void opq_circ_buffer_remove()
{
    kfree(opq_dev->cycles->mutex);
    kfree(opq_dev->cycles->sem);
    kfree(opq_dev->cycles);
}

static char *opq_devnode(struct device *dev, umode_t *mode)
{
	if (!mode)
		return NULL;
	*mode = 0666;
	return NULL;
}

static int __init opq_module_init(void)
{
    opq_dev = kmalloc(sizeof(struct opq_device), GFP_KERNEL);
    opq_dev->int_cnt = 0;
    cl = class_create(THIS_MODULE, "chardrv");
    cl->devnode = opq_devnode;
    opq_circ_buffer_init();
    opq_init_chardev();
    
    device_create(cl, NULL, chardevmajor, NULL, OPQ_UDEV_NAME);
    opq_init_spi();
    opq_init_gpio_int();
    printk (KERN_NOTICE "OPQ: OPQ driver loaded!\n");
    return 0;
}

static void __exit opq_module_exit(void)
{
	device_destroy(cl, chardevmajor);
	class_destroy(cl);
    opq_release_chardev();
    opq_release_spi();
    opq_release_gpio_int();
    opq_circ_buffer_remove();
    printk (KERN_NOTICE "OPQ: OPQ driver exiting.\n");
    kfree(opq_dev);
    return;
}


module_init(opq_module_init);
module_exit(opq_module_exit);

MODULE_LICENSE("GPL");
MODULE_ALIAS("opq");
