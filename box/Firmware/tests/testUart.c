#include <stm32f3xx_hal.h>
#include <stdio.h>
#include <string.h>
#include <runtime_config.h>
#include <peripheral_config.h>

int main(void) {

    /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
    HAL_Init();

    /* Configure the system clock */
    SystemClock_Config();

    /* Initialize all configured peripherals */
//    MX_GPIO_Init();
//    MX_SPI3_Init();
    MX_USART1_UART_Init();
//    MX_SDADC2_Init();

    //Set up the runtime and globals
//    init_OPQ_RunTime();
    //Reset the Data ready pin
//    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);
    char buffer;
    while (1) {
        HAL_UART_Receive(&huart1, (uint8_t *) &buffer, 1, 0xFFFF);
        HAL_UART_Transmit(&huart1, (uint8_t *) &buffer, 1, 0xFFFF);
    }
}

#ifdef USE_FULL_ASSERT

/**
   * @brief Reports the name of the source file and the source line number
   * where the assert_param error has occurred.
   * @param file: pointer to the source file name
   * @param line: assert_param error line source number
   * @retval None
   */
void assert_failed(uint8_t* file, uint32_t line)
{

}

#endif