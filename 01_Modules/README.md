# 小家电代码积木

本目录10份参考代码面向 **NY8B062D + NYC_NY8 2.10**，寄存器依据 `00_Reference/include/ny8b062d.h`。它们是可移植的逻辑起点，接入新芯片前必须重新查头文件、时钟、引脚复用与手册。

| 文件 | 调用方式 | 占用与约束 |
|---|---|---|
| Key_Scan_Debounce.c | 主循环中每10ms调用一次 `Key_Scan_10ms()` | PA0低有效；3次连续采样确认；`PRESS`按下触发一次，`SHORT`松手触发，`LONG`保持约1秒触发一次，`UP`松手触发。上电必须先松手。产品动作只能选择一个事件，不能同时用PRESS和SHORT换档。 |
| Sleep_Wakeup_LowPower.c | 主循环确认按键稳定松开后调用 | PA0唤醒，PB0/1/2低有效灯；关Timer0/1/2/3、PWM/蜂鸣器、IR、ADC、比较器、RFC、LVD及WDT；只保留PA0上拉和LVR。返回后由调用者恢复定时器。 |
| PWM_SoftStart.c | 先 `PWM_Init()`；每10ms调用 `PWM_Ramp_10ms()` | Timer1/PB3；占空计数每10ms变1；0目标立即关断，255约99.61%。示例软升至255需2.55秒。Timer1不能与样板10ms调度器同时占用，需改用Timer0/2/3提供调度。 |

硬件有效电平通过宏管理。PWM软启动只限制占空比变化，不能代替实际电流采样、堵转检测、独立过流/超温保护或驱动器设计。发热负载若是交流过零控制，不能直接套此高频PWM。

休眠示例把未用GPIO设为稳定输出，前提是这些脚在参考板上未接外部信号。PA5保留复位，需工程师安排外部复位上拉。切换到真实产品前必须对照原理图调整，避免与外部输出冲突或给断电器件反向供电。

Key/Sleep已随样板完整编译并参与行为验证；PWM已进行独立编译/汇编与参考工程链接验证，均未做实板验收。

## 扩展参考积木（NY8B062D）

以下7项采用独立参考接口，不会自动加入旧产品。调用均在主循环；ISR只累积调度标志。所有自己写的源码为ASCII、8位变量，GPIO先锁存再开输出。首次集成前按产品需求模板确认电路与参数。

| 文件 | 接口和调用 | 资源、边界及必须配置项 |
|---|---|---|
| ADC_Battery_LowPower.c | `Battery_Init()`后每10ms调用`Battery_10ms()` | 使用内部VDD/4输入、内部2V参考、12位ADC取ADD高8位，约为`count=VDD×32`；只测MCU供电，稳压后的VDD不能代表电池电压。内部参考要求VDD≥2.5V，低于此电压不保证ADC有效。FINST=1MHz、ADC分频16；首次采样等待10ms；正常约20ms一个样本。 |
| Charge_Status.c | `Charge_Init()`；`Charge_10ms()` | PB4低有效插入、PB5低有效充满，外部充电芯片/电源检测器逻辑输入；连续3采样确认；拔出清除充满。不能把充电电压直接接GPIO，也不能凭单个CHRG信号猜测充满。 |
| Motor_MultiSpeed.c | 主循环分别调用`PWM_Init()`、`Motor_SelectMode()`、`PWM_Ramp_10ms()`；`Motor_Timer2Start()`启调度 | PWM占Timer1/PB3，调度占Timer2，每次625×16/1MHz=10ms；三档占空计数80/160/240仅为演示。应用ISR清Timer2标志、加tick，主循环消费tick后直接调用两个函数，ISR不得调用。 |
| LED_Patterns.c | `LED_Init()`；每10ms`LED_10ms()` | PB2/Timer2/PWM2，低有效；off/on/500ms边沿闪烁/约4秒呼吸。PWM周期256/1MHz=256µs，约3906Hz；需要其它定时器供10ms节拍。 |
| Buzzer_Alerts.c | `Buzzer_Init()`；设`buzzer_ticks`后每10ms`Buzzer_10ms()` | PA2/BZ3/Timer3，FINST=1MHz、预分频128、BZ3再除2，约3906Hz；用于无源蜂鸣器外部驱动参考。实际音调、极性与驱动电流须实测。 |
| MultiKey_Combo.c | `MultiKey_Init()`；每10ms`MultiKey_10ms()` | PA0/PA1低有效，3采样消抖；`keys_pressed`、`keys_released`为位掩码，`keys_combo`为组合一次事件。单键延后约50ms给组合窗口，上电需先全部松开；两个键均松开才重新使能组合。已发出的单键事件无法因晚按第二键而撤回。 |
| Protection_Overcurrent.c | `Protection_Reset()`；条件满足后显式`Protection_Arm()`；每10ms`Protection_10ms()` | 上层提供校准后的8位电流计数，每次必须更新fresh；硬阈值/传感器异常/采样失效立即锁定trip，软阈值连续确认；启动屏蔽只屏蔽软阈值。trip锁存，禁止自动反复启动。堵转电流与时间窗需按电机实测设定。 |

ADC的预警、关机、恢复阈值和确认样本数必须由实际电池体系/测量标定填写；`battery_configured=0`时维持无效/关机状态，不能作为已配置产品运行。预警≤、关机≤、恢复≥，且必须`关机阈值<预警阈值<恢复阈值`，迟滞区保持状态。ADC超时也会置关机标志。应用必须消费`battery_shutdown`并真实关负载；积木本身不会替产品决定关哪一个引脚。

过流框架必须由应用收到trip后立即关断实际驱动。它没有硬件比较器级的反应速度，不能代替驱动器限流、保险丝、过温开关等硬件保护；缺传感器/标定参数时只是一份框架。

### 定时器与引脚冲突

| 资源 | 可能使用者 | 集成规则 |
|---|---|---|
| Timer1/PB3 | PWM软启动、电机多档 | 与旧三档灯的Timer1调度冲突；电机示例改用Timer2调度。 |
| Timer2/PB2 | LED呼吸PWM2、Motor_Timer2Start调度 | 两者不能原样同时用；同时需要时把调度迁移到Timer0或Timer3并重新计算验证。 |
| Timer3/PA2 | 蜂鸣器BZ3 | 不得再同时拿Timer3作另一个独立周期调度；注意PA2也是烧录数据输入。 |
| PA0/PA1、PB4/PB5 | 多按键、充电状态输入 | 对照原理图避开模拟采样、复用输出和烧录/复位功能。 |

### 独立编译验证

运行 `python 00_Reference\Scripts\verify_modules.py`，每次创建独立新证据目录，不覆盖上次产物。当前10份积木（原3份+新增7份）分别复制真实母版，以专用SDCC/NYASM进行编译、汇编、链接，扫描全部源码并检查RAM/ROM和调用深度；逐项结果见 `00_Reference/Validation/Module_Builds_*/Module_Compilation_Report.json`。

这些模块夹具没有真实10ms调度，不能烧录为产品，也不应标记整机功能PASS。它们只证明独立编译和静态资源检查通过，模块的电气、时序与组合功能还需对应产品的behavior_tests.py和实板清单验证。母版Modules内补入PWM_SoftStart.c作为备用，不自动接到三档灯代码。
