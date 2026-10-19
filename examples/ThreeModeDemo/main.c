/* Three mode LED demo. NY8B062D, IHRC 4 MHz, 4T, 3 V reference board.
 * PA0: button to GND. PB0/PB1/PB2: active-low LEDs with resistors.
 * Unused GPIO pads must be unconnected. PA5 is external reset.
 */
#define LED_ON 0
#define KEY_ACTIVE_LEVEL 0

#include <ny8.h>
#include "Modules/Key_Scan_Debounce.c"
#include "Modules/Sleep_Wakeup_LowPower.c"

volatile unsigned char ticks_pending;
volatile unsigned char tick_fault;
unsigned char mode;
unsigned char idle_ticks;
unsigned char idle_seconds;
unsigned char idle_minutes;
unsigned char key_event;
unsigned char led_shadow;

void isr(void) __interrupt(0)
{
    if (INTF & 0x08) {
        /* W0C: write ones to the other interrupt flags. */
        INTF = 0xF7;
        if (ticks_pending < 255) ++ticks_pending;
        else tick_fault = 1;
    }
}

void Timer_Start(void)
{
    DISI();
    INTE = 0;
    T1CR1 = 0;
    /* 625 counts x 16 / 1000000 Hz = 10 ms, hardware reload. */
    TMRH = 0x20;
    TMR1 = 0x70;
    T1CR2 = 0x03;
    INTF = 0;
    ticks_pending = 0;
    tick_fault = 0;
    INTE = 0x08;
    T1CR1 = 0x03;
    ENI();
}

void main(void)
{
    DISI();
    PORTA = 0;
    PORTB = LED_ON ? 0 : 0x07;
    IOSTA = 0x21;
    IOSTB = 0;
    BODCON = 0;
    ABPLCON = 0xFF;
    BPHCON = 0xFF;
    APHCON = 0xFE;
    PACON = 0;
    ADMD = 0;
    ADR = 0;
    ADCR = 0;
    ADVREFH = 0;
    ANAEN = 0;
    RFC = 0;
    T2CR1 = 0;
    T3CR1 = 0;
    BZ1CR = 0;
    BZ2CR = 0;
    BZ3CR = 0;
    IRCR = 0;
    PCON1 = 0;
    INTE2 = 0;
    INTEDG = 0;
    AWUCON = 0;
    BWUCON = 0;
    PCON = 0x98;
    OSCCR = 0x01;
    mode = 0;
    idle_ticks = 0;
    idle_seconds = 0;
    idle_minutes = 0;
    Key_Reset();
    Timer_Start();

    while (1) {
        CLRWDT();
        if (tick_fault) mode = 0;
        if (ticks_pending) {
            DISI();
            --ticks_pending;
            ENI();
            key_event = Key_Scan_10ms();
            if (mode) {
                if (++idle_ticks >= 100) {
                    idle_ticks = 0;
                    if (++idle_seconds >= 60) {
                        idle_seconds = 0;
                        if (++idle_minutes >= 5) mode = 0;
                    }
                }
            }
            /* A held button is one action; release must debounce too. */
            if (key_event & KEY_EVENT_PRESS) {
                if (++mode > 3) mode = 0;
                idle_ticks = 0;
                idle_seconds = 0;
                idle_minutes = 0;
            }
            led_shadow = 0;
            if (mode == 1) led_shadow = 0x01;
            if (mode == 2) led_shadow = 0x02;
            if (mode == 3) led_shadow = 0x04;
            if (LED_ON == 0) led_shadow ^= 0x07;
            PORTB = led_shadow;

            if (mode == 0 && !key_locked && key_stable == 1 &&
                key_filter == 3 && (PORTA & 0x01)) {
                LowPower_Sleep();
                /* Keep released key state so the wake press gets debounced. */
                idle_ticks = 0;
                idle_seconds = 0;
                idle_minutes = 0;
                Timer_Start();
            }
        }
    }
}
