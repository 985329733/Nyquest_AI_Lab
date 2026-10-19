/* NY8B062D PWM1 on PB3. Call PWM_Ramp_10ms from main every 10 ms.
 * 4 MHz IHRC / 4T = 1 MHz. Timer1 / 1, reload 255: 3906.25 Hz.
 * Duty target is 0..255 out of 256; 255 is not exact 100 percent.
 * Reserve Timer1/PB3. Do not combine with the demo Timer1 scheduler.
 * Use a proper gate driver and hardware overcurrent protection.
 */
#include <ny8.h>
#ifndef MOTOR_ON
#define MOTOR_ON 1
#endif
#define MOTOR_OFF (1 - MOTOR_ON)

unsigned char pwm_level;
unsigned char pwm_target;

void PWM_Init(void)
{
    T1CR1 = 0;
    /* Set the pad latch before enabling its output direction. */
    PORTBbits.PB3 = MOTOR_OFF;
    IOSTB &= 0xF7;
    pwm_level = 0;
    pwm_target = 0;
    /* Preserve Timer2 fields. Clear Timer1 and duty high bits. */
    TMRH &= 0xCC;
    TMR1 = 255;
    PWM1DUTY = 0;
    T1CR2 = 0x08;
}

void PWM_Ramp_10ms(void)
{
    if (pwm_target == 0) {
        /* Stop immediately; do not ramp through a fault shutdown. */
        T1CR1 = 0;
        PORTBbits.PB3 = MOTOR_OFF;
        PWM1DUTY = 0;
        pwm_level = 0;
    } else {
        if (pwm_level < pwm_target) ++pwm_level;
        else if (pwm_level > pwm_target) --pwm_level;
        PWM1DUTY = pwm_level;
        T1CR1 = (MOTOR_ON ? 0x80 : 0xC0) | 0x03;
    }
}
