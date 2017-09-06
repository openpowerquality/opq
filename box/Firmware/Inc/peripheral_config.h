#ifndef OPQ_PERIPHERAL_CONFIG_H
#define OPQ_PERIPHERAL_CONFIG_H
#include <stm32f3xx_hal.h>

///ADC handle
extern SDADC_HandleTypeDef hsdadc2;

//SPI handle
extern SPI_HandleTypeDef hspi3;

//Timer handle for ADC
extern TIM_HandleTypeDef htim2;

//Timer handle for GPS
extern TIM_HandleTypeDef htim4;

//UART handle
extern UART_HandleTypeDef huart1;

/**
 * @brief System Clock Configuration.
 */
void SystemClock_Config(void);

/**
 * @brief This is called in case of an error.
 */
void Error_Handler(void);

/**
 * Initialize the GPIO Flags and LEDs.
 */
void MX_GPIO_Init(void);

/**
 * @brief initializes internal the 16 bit adc
 */
void MX_SDADC2_Init(void);

/**
 * @brief Initialize SPI3 as slave.
 */
void MX_SPI3_Init(void);

/**
 * @brief Initialize uart.
 */
void MX_USART1_UART_Init(void);

/**
 * @brief Initialize GPS Capture timer.
 */
void MX_GPS_Init(void);

#endif //OPQ_PERIPHERAL_CONFIG_H
