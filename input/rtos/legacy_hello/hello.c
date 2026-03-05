#include <zephyr/kernel.h>

int legacy_main(void)
{
    printk("LEGACY_HELLO_ARTIFACT\n");
    return 0;
}