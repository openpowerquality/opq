#include "peripheral_config.h"

///ADC handle
SDADC_HandleTypeDef hsdadc2;

//SPI handle
SPI_HandleTypeDef hspi3;

//Timer handle adc
TIM_HandleTypeDef htim2;

//Timer handle gps
TIM_HandleTypeDef htim4;

//UART handle
UART_HandleTypeDef huart1;


void SystemClock_Config(void) {

    RCC_OscInitTypeDef RCC_OscInitStruct;
    RCC_ClkInitTypeDef RCC_ClkInitStruct;
    RCC_PeriphCLKInitTypeDef PeriphClkInit;

    //Configure the oscillator
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_BYPASS;
    RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
    //Configure PLL
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }

    //Configure system clock
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                  | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    //
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
        Error_Handler();
    }

    //Configure Peripheral clocks
    PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USART1 | RCC_PERIPHCLK_SDADC;
    PeriphClkInit.Usart1ClockSelection = RCC_USART1CLKSOURCE_SYSCLK;
    PeriphClkInit.SdadcClockSelection = RCC_SDADCSYSCLK_DIV12;
    if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK) {
        Error_Handler();
    }

    //Enable SDADC
    HAL_PWREx_EnableSDADC(PWR_SDADC_ANALOG2);

    //HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq() / 1000);

    //HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);

    /* SysTick_IRQn interrupt configuration */
    //HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);
}

void Error_Handler(void) {
    while (1) {
        HAL_UART_Transmit(&huart1, (uint8_t *) "E", 1, 0xFFFF);
    }
}


void MX_SDADC2_Init(void) {

    SDADC_ConfParamTypeDef confParam;

    /**Configure the SDADC low power mode, fast conversion mode,
    slow clock mode and SDADC2 reference voltage
    */
    hsdadc2.Instance = SDADC2;
    hsdadc2.Init.IdleLowPowerMode = SDADC_LOWPOWER_NONE;
    hsdadc2.Init.FastConversionMode = SDADC_FAST_CONV_DISABLE;
    hsdadc2.Init.SlowClockMode = SDADC_SLOW_CLOCK_DISABLE;
    hsdadc2.Init.ReferenceVoltage = SDADC_VREF_EXT;
    hsdadc2.RegularContMode = SDADC_CONTINUOUS_CONV_OFF;
    hsdadc2.InjectedContMode = SDADC_CONTINUOUS_CONV_OFF;

    if (HAL_SDADC_Init(&hsdadc2) != HAL_OK)
        Error_Handler();

    /* Prepare the channel configuration */
    confParam.CommonMode = SDADC_COMMON_MODE_VDDA_2;
    confParam.Gain = SDADC_GAIN_1;
    confParam.InputMode = SDADC_INPUT_MODE_DIFF;
    confParam.Offset = 0x00000000;

    if (HAL_SDADC_PrepareChannelConfig(&hsdadc2, SDADC_CONF_INDEX_0, &confParam) != HAL_OK)
        Error_Handler();

    /* associate channel 8 to the configuration 0 */
    if (HAL_SDADC_AssociateChannelConfig(&hsdadc2, SDADC_CHANNEL_8, SDADC_CONF_INDEX_0) != HAL_OK)
        Error_Handler();

    /* select channel 8 for injected conversion and not for continuous mode */
    if (HAL_SDADC_InjectedConfigChannel(&hsdadc2, SDADC_CHANNEL_8, SDADC_CONTINUOUS_CONV_OFF) != HAL_OK)
        Error_Handler();

    /* Select external trigger for injected conversion */
    if (HAL_SDADC_SelectInjectedTrigger(&hsdadc2, SDADC_EXTERNAL_TRIGGER) != HAL_OK)
        /* An error occurs during the selection of the trigger */
        Error_Handler();

    /* Select timer 2 channel 3 as external trigger and rising edge */
    if (HAL_SDADC_SelectInjectedExtTrigger(&hsdadc2, SDADC_EXT_TRIG_TIM2_CC3, SDADC_EXT_TRIG_RISING_EDGE) !=
        HAL_OK) {
        /* An error occurs during the selection of the trigger */
        Error_Handler();
    }

    /* Start Calibration in polling mode */
    if (HAL_SDADC_CalibrationStart(&hsdadc2, SDADC_CALIBRATION_SEQ_1) != HAL_OK)
        /* An error occurs during the starting phase of the calibration */
        Error_Handler();

    /* Pool for the end of calibration */
    if (HAL_SDADC_PollForCalibEvent(&hsdadc2, HAL_MAX_DELAY) != HAL_OK)
        /* An error occurs while waiting for the end of the calibration */
        Error_Handler();

    /* Start injected conversion in interrupt mode */
    if (HAL_SDADC_InjectedStart_IT(&hsdadc2) != HAL_OK) {
        /* An error occurs during the configuration of the injected conversion in interrupt mode */
        Error_Handler();
    }

    /* Start the TIMER's Channel */
    if (HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3) != HAL_OK) {
        /* An error occurs during the configuration of the timer in PWM mode */
        Error_Handler();
    }

}

void MX_SPI3_Init(void) {
    hspi3.Instance = SPI3;
    hspi3.Init.Mode = SPI_MODE_SLAVE;
    hspi3.Init.Direction = SPI_DIRECTION_2LINES;
    hspi3.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi3.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi3.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi3.Init.NSS = SPI_NSS_HARD_INPUT;
    hspi3.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi3.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi3.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi3.Init.CRCPolynomial = 7;
    hspi3.Init.CRCLength = SPI_CRC_LENGTH_DATASIZE;
    hspi3.Init.NSSPMode = SPI_NSS_PULSE_DISABLE;
    if (HAL_SPI_Init(&hspi3) != HAL_OK) {
        Error_Handler();
    }

}

void MX_USART1_UART_Init(void) {

    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
    huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
    if (HAL_UART_Init(&huart1) != HAL_OK) {
        Error_Handler();
    }
}

/**
 * @brief Initialize GPIO
 */
void MX_GPIO_Init(void) {

    GPIO_InitTypeDef GPIO_InitStruct;

    /* GPIO Ports Clock Enable */
    __HAL_RCC_GPIOF_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /*Configure GPIO pin Output Level */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);

    /*Configure GPIO pin Output Level */
    HAL_GPIO_WritePin(GPIOF, GPIO_PIN_6 | GPIO_PIN_7, GPIO_PIN_RESET);

    /*Configure GPIO pin : PA0 */
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /*Configure GPIO pins : PF6 PF7 */
    GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

    /*Configure GPIO pin : PB6 */
    GPIO_InitStruct.Pin = GPIO_PIN_6;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

void MX_GPS_Init(void){
    htim4.Instance = TIM4;
    /* Initialize TIMx peripheral as follows:
         + Period = 0xFFFF
         + Prescaler = 0
         + ClockDivision = 0
         + Counter direction = Up
    */
    htim4.Init.Period        = 60000 -1;
    htim4.Init.Prescaler     = 1200 -1;
    htim4.Init.ClockDivision = 0;
    htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
    HAL_TIM_IC_Init(&htim4);

    //Timer input capture for GPS
    TIM_IC_InitTypeDef     sICConfig;
    sICConfig.ICPolarity  = TIM_ICPOLARITY_RISING;
    sICConfig.ICSelection = TIM_ICSELECTION_DIRECTTI;
    sICConfig.ICPrescaler = TIM_ICPSC_DIV1;
    sICConfig.ICFilter    = 0;
    HAL_TIM_IC_ConfigChannel(&htim4, &sICConfig, TIM_CHANNEL_1);

    HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_1);
}