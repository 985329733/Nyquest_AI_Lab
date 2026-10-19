/* NY8B062D. Timer1/PB3 PWM, Timer2 10 ms scheduler at 4 MHz/4T.
 * Main calls PWM_Init, Motor_Timer2Start, Motor_SelectMode and
 * PWM_Ramp_10ms directly. No wrapper calls the ramp from an ISR.
 * Mode levels are demonstration duty counts, not measured speeds.
 */
#include <ny8.h>
#include "PWM_SoftStart.c"
unsigned char motor_mode;
void Motor_SelectMode(void)
{
    pwm_target = 0;
    if (motor_mode == 1) pwm_target = 80;
    if (motor_mode == 2) pwm_target = 160;
    if (motor_mode == 3) pwm_target = 240;
}
void Motor_Timer2Start(void)
{
    T2CR1 = 0;
    TMRH = (TMRH & 0x3F) | 0x80;
    TMR2 = 0x70;
    T2CR2 = 0x03;
    INTF = 0xDF;
    INTE |= 0x20;
    T2CR1 = 0x03;
}
