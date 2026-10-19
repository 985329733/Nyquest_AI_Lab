/* NY8B062D. Sample internal VDD/4 against the internal 2 V reference.
 * FINST must be 1 MHz. ADC clock FINST/16, 12 bit, 8-clock sample.
 * Call every 10 ms. ADD is the high 8 bits: count is about VDD * 32.
 * VDD must stay at least 2.5 V for the internal 2 V reference.
 * This measures MCU VDD only, not a battery behind a regulator.
 * Thresholds must be calibrated for the actual supply and chemistry.
 */
#include <ny8.h>
unsigned char battery_warning;
unsigned char battery_shutdown;
unsigned char battery_valid;
unsigned char battery_configured;
unsigned char battery_low_count;
unsigned char battery_cut_count;
unsigned char battery_warn_limit;
unsigned char battery_cut_limit;
unsigned char battery_recover_limit;
unsigned char battery_confirm_samples;
unsigned char battery_sample;
unsigned char battery_adc_state;
unsigned char battery_adc_wait;
void Battery_Init(void)
{
    battery_warning = 1;
    battery_shutdown = 1;
    battery_valid = 0;
    battery_configured = 0;
    battery_low_count = 0;
    battery_cut_count = 0;
    battery_adc_state = 0;
    battery_adc_wait = 0;
    ADVREFH = 0;
    ADR = 0;
    ADCR = (ADCR & 0x70) | 0x0F;
    ADMD = 0x9B;
}
void Battery_10ms(void)
{
    if (!battery_configured || !battery_confirm_samples ||
        battery_cut_limit >= battery_warn_limit ||
        battery_warn_limit >= battery_recover_limit) {
        battery_valid = 0;
        battery_warning = 1;
        battery_shutdown = 1;
        return;
    }
    if (!battery_adc_state) {
        /* First call is at least 10 ms after ADC power-on. */
        ADMD = 0xDB;
        battery_adc_state = 1;
        battery_adc_wait = 0;
        return;
    }
    if (!(ADMD & 0x20)) {
        if (++battery_adc_wait >= 5) {
            battery_valid = 0;
            battery_shutdown = 1;
            battery_warning = 1;
            battery_adc_state = 0;
        }
        return;
    }
    battery_sample = ADD;
    battery_valid = 1;
    battery_adc_state = 0;
    if (battery_sample <= battery_warn_limit) {
        if (battery_low_count < battery_confirm_samples) ++battery_low_count;
        if (battery_low_count >= battery_confirm_samples) battery_warning = 1;
    } else battery_low_count = 0;
    if (battery_sample <= battery_cut_limit) {
        if (battery_cut_count < battery_confirm_samples) ++battery_cut_count;
        if (battery_cut_count >= battery_confirm_samples) battery_shutdown = 1;
    } else battery_cut_count = 0;
    if (battery_sample >= battery_recover_limit) {
        battery_warning = 0;
        battery_shutdown = 0;
        battery_low_count = 0;
        battery_cut_count = 0;
    }
}
