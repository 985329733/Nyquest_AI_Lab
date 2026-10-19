/* NY8B062D. Passive buzzer driver on PA2, BZ3/Timer3.
 * FINST 1 MHz, prescaler /128, BZ3 source PS3/2: about 3.906 kHz.
 * Set buzzer_ticks in main, then call Buzzer_10ms every 10 ms.
 * Use an appropriate external driver for the actual transducer.
 */
#include <ny8.h>
#ifndef BUZZER_ON
#define BUZZER_ON 1
#endif
unsigned char buzzer_ticks;
void Buzzer_Init(void)
{
    BZ3CR = 0;
    T3CR1 = 0;
    PORTAbits.PA2 = 1 - BUZZER_ON;
    IOSTA &= 0xFB;
    TM3RH &= 0xCC;
    TMR3 = 255;
    T3CR2 = 0x06;
    buzzer_ticks = 0;
}
void Buzzer_10ms(void)
{
    if (buzzer_ticks) {
        --buzzer_ticks;
        T3CR1 = 0x03;
        BZ3CR = 0x80;
    } else {
        BZ3CR = 0;
        T3CR1 = 0;
        PORTAbits.PA2 = 1 - BUZZER_ON;
    }
}
