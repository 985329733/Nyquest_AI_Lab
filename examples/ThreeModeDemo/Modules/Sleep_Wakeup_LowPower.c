/* NY8B062D only. PA0 button to GND, PB0..2 active-low LEDs.
 * Call from main only after a debounced release. Returns on wake.
 * Return value 0 means sleep was skipped because PA0 was already low.
 * Restore the product timer and key state in main after this function.
 * Unused output pins must be unconnected on this reference board.
 */
#include <ny8.h>
#ifndef LED_ON
#define LED_ON 0
#endif
#define LED_OFF (1 - LED_ON)

unsigned char LowPower_Sleep(void)
{
    DISI();
    PORTB = LED_OFF ? 0x07 : 0x00;
    INTE = 0;
    INTE2 = 0;
    T1CR1 = 0;
    T2CR1 = 0;
    T3CR1 = 0;
    PCON1 = 0;
    BZ1CR = 0;
    BZ2CR = 0;
    BZ3CR = 0;
    IRCR = 0;
    ADMD = 0;
    ADR = 0;
    ADCR = 0;
    ADVREFH = 0;
    ANAEN = 0;
    RFC = 0;
    INTEDG = 0;
    PACON = 0;
    BODCON = 0;
    ABPLCON = 0xFF;
    BPHCON = 0xFF;
    APHCON = 0xFE;
    /* Keep LVR active and disable WDT, LVD and PA5 pull-up. */
    PCON = 0x18;
    PORTA = 0;
    IOSTA = 0x21;
    IOSTB = 0;
    BWUCON = 0;
    AWUCON = 0x01;
    OSCCR = 0x01;
    INTE = 0x02;
    UPDATE_REG(PORTA);
    INTF = 0;
    if ((PORTA & 0x01) == 0) {
        INTE = 0;
        AWUCON = 0;
        PCON = 0x98;
        CLRWDT();
        return 0;
    }
    /* GIE stays off: enabled PA0 change resumes after SLEEP. */
    SLEEP();
    INTF = 0;
    INTE = 0;
    AWUCON = 0;
    PCON = 0x98;
    CLRWDT();
    return 1;
}
