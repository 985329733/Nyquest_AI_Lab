/* NY8B062D: call Key_Scan_10ms from main once per timer tick.
 * Start locked: a key held at reset must be released before use.
 * PRESS is one-shot. SHORT is on release. LONG is one-shot at 1 s.
 * Do not count PRESS and SHORT as two product actions.
 */
#include <ny8.h>
#ifndef KEY_ACTIVE_LEVEL
#define KEY_ACTIVE_LEVEL 0
#endif
#define KEY_EVENT_PRESS  0x01
#define KEY_EVENT_SHORT  0x02
#define KEY_EVENT_LONG   0x04
#define KEY_EVENT_UP     0x08

unsigned char key_stable;
unsigned char key_candidate;
unsigned char key_filter;
unsigned char key_hold;
unsigned char key_locked;

void Key_Reset(void)
{
    key_stable = 1;
    key_candidate = 1;
    key_filter = 0;
    key_hold = 0;
    key_locked = 1;
}

unsigned char Key_Scan_10ms(void)
{
    unsigned char raw;
    unsigned char event;
    event = 0;
    raw = (PORTA & 0x01) ? 1 : 0;
    if (raw != key_candidate) {
        key_candidate = raw;
        key_filter = 1;
    } else if (key_filter < 3) {
        ++key_filter;
    }
    if (key_filter == 3) {
        if (key_locked) {
            key_stable = key_candidate;
            if (key_candidate != KEY_ACTIVE_LEVEL) key_locked = 0;
        } else if (key_stable != key_candidate) {
            key_stable = key_candidate;
            if (key_stable == KEY_ACTIVE_LEVEL) {
                key_hold = 0;
                event = KEY_EVENT_PRESS;
            } else {
                event = KEY_EVENT_UP;
                if (key_hold < 100) event |= KEY_EVENT_SHORT;
            }
        } else if (key_stable == KEY_ACTIVE_LEVEL) {
            if (key_hold < 100) {
                ++key_hold;
                if (key_hold == 100) event = KEY_EVENT_LONG;
            }
        }
    }
    return event;
}
