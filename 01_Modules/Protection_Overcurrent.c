/* NY8B062D software protection framework, not hardware protection.
 * Current is a calibrated 8-bit ADC count with a fresh-sample flag.
 * Call every 10 ms. A hard limit or stale sensor trips immediately.
 * Startup blanking masks only the lower sustained-current threshold.
 * Trip stays latched until an explicit safe Arm request in main.
 */
#include <ny8.h>
unsigned char protection_configured;
unsigned char protection_current;
unsigned char protection_fresh;
unsigned char protection_sensor_fault;
unsigned char protection_limit;
unsigned char protection_hard_limit;
unsigned char protection_confirm_ticks;
unsigned char protection_startup_ticks;
unsigned char protection_count;
unsigned char protection_trip;
void Protection_Reset(void)
{
    protection_configured = 0;
    protection_trip = 1;
    protection_fresh = 0;
    protection_sensor_fault = 1;
    protection_count = 0;
    protection_startup_ticks = 0;
}
void Protection_Arm(void)
{
    if (protection_configured && protection_fresh &&
        !protection_sensor_fault && protection_confirm_ticks &&
        protection_limit < protection_hard_limit &&
        protection_current < protection_limit) {
        protection_trip = 0;
        protection_count = 0;
    }
}
void Protection_10ms(void)
{
    if (!protection_configured || !protection_fresh ||
        protection_sensor_fault || !protection_confirm_ticks ||
        protection_limit >= protection_hard_limit) protection_trip = 1;
    protection_fresh = 0;
    if (protection_trip) return;
    if (protection_current >= protection_hard_limit) {
        protection_trip = 1;
        return;
    }
    if (protection_startup_ticks) {
        --protection_startup_ticks;
        protection_count = 0;
        return;
    }
    if (protection_current >= protection_limit) {
        if (protection_count < protection_confirm_ticks) ++protection_count;
        if (protection_count >= protection_confirm_ticks) protection_trip = 1;
    } else protection_count = 0;
}
