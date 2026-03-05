#include <zephyr/kernel.h>

K_THREAD_STACK_DEFINE(stack1, 1024);
K_THREAD_STACK_DEFINE(stack2, 1024);

struct k_thread thread1;
struct k_thread thread2;

void thread_a(void *a, void *b, void *c)
{
    printk("THREAD_A_RUNNING\n");
}

void thread_b(void *a, void *b, void *c)
{
    printk("THREAD_B_RUNNING\n");
}

int legacy_main(void)
{
    printk("THREAD_TEST_START\n");

    k_thread_create(&thread1, stack1, 1024,
                    thread_a,
                    NULL, NULL, NULL,
                    5, 0, K_NO_WAIT);

    k_thread_create(&thread2, stack2, 1024,
                    thread_b,
                    NULL, NULL, NULL,
                    5, 0, K_NO_WAIT);

    k_sleep(K_MSEC(50));

    return 0;
}