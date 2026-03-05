#include <zephyr/kernel.h>

int legacy_main(void)
{
    int sum = 0;

    for (int i = 0; i < 10000; i++)
        sum += i;

    printk("SUM=%d\n", sum);

    return 0;
}