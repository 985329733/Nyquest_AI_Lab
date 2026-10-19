/* NY8B062D. PB2 active-low LED, Timer2/PWM2 for breathing.
 * Call every 10 ms from another timer. Modes: 0 off, 1 on,
 * 2 flash at 500 ms per edge, 3 breathe in a 4 second cycle.
 */
#include <ny8.h>
#ifndef LED_ON
#define LED_ON 0
#endif
unsigned char led_mode;
unsigned char led_level;
unsigned char led_down;
unsigned char led_phase;
unsigned char led_ticks;
void LED_Init(void)
{
    T2CR1 = 0;
    PORTBbits.PB2 = 1 - LED_ON;
    IOSTB &= 0xFB;
    TMRH &= 0x33;
    TMR2 = 255;
    PWM2DUTY = 0;
    T2CR2 = 0x08;
    led_mode = 0;
    led_level = 0;
    led_down = 0;
    led_phase = 0;
    led_ticks = 0;
}
void LED_10ms(void)
{
    if (led_mode == 3) {
        if (led_down) {
            if (led_level) --led_level;
            if (!led_level) led_down = 0;
        } else {
            if (led_level < 200) ++led_level;
            if (led_level == 200) led_down = 1;
        }
        PWM2DUTY = led_level;
        T2CR1 = (LED_ON ? 0x80 : 0xC0) | 0x03;
    } else {
        T2CR1 = 0;
        if (led_mode == 2) {
            if (++led_ticks >= 50) {
                led_ticks = 0;
                led_phase ^= 1;
            }
            PORTBbits.PB2 = led_phase ? LED_ON : 1 - LED_ON;
        } else {
            led_ticks = 0;
            led_phase = 0;
            PORTBbits.PB2 = (led_mode == 1) ? LED_ON : 1 - LED_ON;
        }
    }
}
