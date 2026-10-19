/* Chip qualification idle probe only. Not a finished product. */
#define LED_ON 0
#include <ny8.h>
volatile unsigned char qualification_counter;
void main(void)
{
    DISI();
    PORTB = 0;
    IOSTB = 0;
    BPHCON = 255;
    BPLCON = 255;
    PCONbits.WDTEN = 1;
    qualification_counter = 0;
    while (1) {
        CLRWDT();
        ++qualification_counter;
    }
}
