/* NY8B062D. PA0/PA1 active-low keys, 3-sample debounce.
 * Main calls every 10 ms. Individual presses wait 50 ms for a combo.
 * A combo is reported once until both keys are released.
 * A second key after the single event cannot retract that old event.
 */
#include <ny8.h>
unsigned char keys_stable;
unsigned char keys_candidate;
unsigned char keys_filter;
unsigned char keys_locked;
unsigned char keys_pending;
unsigned char keys_wait;
unsigned char keys_pressed;
unsigned char keys_released;
unsigned char keys_combo;
unsigned char keys_combo_held;
void MultiKey_Init(void)
{
    PORTA |= 0x03;
    IOSTA |= 0x03;
    PACON &= 0xFC;
    APHCON &= 0xFC;
    ABPLCON |= 0x03;
    keys_stable = 0;
    keys_candidate = 0;
    keys_filter = 0;
    keys_locked = 1;
    keys_pending = 0;
    keys_wait = 0;
    keys_pressed = 0;
    keys_released = 0;
    keys_combo = 0;
    keys_combo_held = 0;
}
void MultiKey_10ms(void)
{
    unsigned char raw;
    raw = (unsigned char)(~PORTA) & 3;
    keys_pressed = 0;
    keys_released = 0;
    keys_combo = 0;
    if (raw != keys_candidate) {
        keys_candidate = raw;
        keys_filter = 1;
    } else if (keys_filter < 3) ++keys_filter;
    if (keys_filter != 3) return;
    if (keys_locked) {
        if (!raw) keys_locked = 0;
        keys_stable = raw;
        return;
    }
    if (raw != keys_stable) {
        keys_released = keys_stable & (unsigned char)(~raw);
        keys_pending |= raw & (unsigned char)(~keys_stable);
        if (!keys_combo_held) keys_pressed = keys_pending & keys_released;
        keys_pending &= raw;
        keys_wait = 0;
        keys_stable = raw;
    }
    if (keys_stable == 3 && !keys_combo_held) {
        keys_combo = 1;
        keys_combo_held = 1;
        keys_pending = 0;
        keys_pressed = 0;
    }
    if (!keys_stable) keys_combo_held = 0;
    if (keys_pending && !keys_combo_held) {
        if (++keys_wait >= 5) {
            keys_pressed |= keys_pending;
            keys_pending = 0;
        }
    }
}
