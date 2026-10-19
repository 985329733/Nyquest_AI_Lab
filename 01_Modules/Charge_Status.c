/* NY8B062D. PB4: charge input present, PB5: full, both active low.
 * These are external logic status signals, not power inputs.
 * Full is ignored without present. Call every 10 ms.
 */
#include <ny8.h>
unsigned char charge_present;
unsigned char charge_full;
unsigned char charge_candidate;
unsigned char charge_debounce;
void Charge_Init(void)
{
    PORTB |= 0x30;
    IOSTB |= 0x30;
    BPHCON &= 0xCF;
    charge_present = 0;
    charge_full = 0;
    charge_candidate = 0;
    charge_debounce = 0;
}
void Charge_10ms(void)
{
    unsigned char raw;
    raw = 0;
    if (!(PORTB & 0x10)) {
        raw = 1;
        if (!(PORTB & 0x20)) raw |= 2;
    }
    if (raw != charge_candidate) {
        charge_candidate = raw;
        charge_debounce = 1;
    } else if (charge_debounce < 3) ++charge_debounce;
    if (charge_debounce == 3) {
        charge_present = charge_candidate & 1;
        charge_full = (charge_candidate & 2) ? 1 : 0;
    }
}
