cmake_minimum_required(VERSION 3.0.0)
project(opq.elf)

INCLUDE(CMakeForceCompiler)

SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_VERSION 1)

# specify the cross compiler
set(CMAKE_C_COMPILER "arm-none-eabi-gcc")
set(CMAKE_CXX_COMPILER "arm-none-eabi-g++")


SET(COMMON_FLAGS "-mthumb \
        -mcpu=cortex-m4 \
        -mfloat-abi=softfp \
        -mfpu=fpv4-sp-d16 \
        -DSTM32F373xC \
        -DUSE_HAL_DRIVER \
        \"-D__weak=__attribute__((weak)) \" \
        \"-D__packed=__attribute__((__packed__)) \" \
        -I${PROJECT_SOURCE_DIR}/Drivers/CMSIS/Include/ \
        -I${PROJECT_SOURCE_DIR}/Drivers/STM32F3xx_HAL_Driver/Inc/ \
        -I${PROJECT_SOURCE_DIR}/Inc/    \
        -I${PROJECT_SOURCE_DIR}/Drivers/CMSIS/Device/ST/STM32F3xx/Include/ \
        -Wall -fno-common -fno-strict-aliasing -Os")

SET(CMAKE_C_FLAGS ${COMMON_FLAGS})
SET(CMAKE_C_LINK_FLAGS "-Wl,-gc-sections,-Map=opq.map,-cref,-T${PROJECT_SOURCE_DIR}/STM32F373CC_FLASH.ld -mthumb -mcpu=cortex-m4 -mfloat-abi=softfp -mfpu=fpv4-sp-d16 -Os")
SET(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")

set(SOURCE_FILES
        Drivers/CMSIS/Device/ST/STM32F3xx/Include/stm32f373xc.h
        Drivers/CMSIS/Device/ST/STM32F3xx/Include/stm32f3xx.h
        Drivers/CMSIS/Device/ST/STM32F3xx/Include/system_stm32f3xx.h
        Drivers/CMSIS/Device/ST/STM32F3xx/Source/system_stm32f3xx.c
        Drivers/CMSIS/Device/ST/STM32F3xx/Source/startup_stm32f373xc.s
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_cortex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_dma.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_flash.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_flash_ex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_gpio.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_i2c.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_i2c_ex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_pwr.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_pwr_ex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_rcc.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_rcc_ex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_sdadc.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_spi.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_spi_ex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_tim.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_tim_ex.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_uart.c
        Drivers/STM32F3xx_HAL_Driver/Src/stm32f3xx_hal_uart_ex.c
        Src/newlib_stub.c
        Src/stm32f3xx_hal_msp.c
        Src/stm32f3xx_it.c
        Src/runtime_config.c
        Src/peripheral_config.c
        )

set_property(SOURCE Drivers/CMSIS/Device/ST/STM32F3xx/Source/startup_stm32f373xc.s PROPERTY LANGUAGE C)

add_executable(opq.elf Src/opq.c ${SOURCE_FILES})

#add_executable(testUart.elf tests/testUart.c ${SOURCE_FILES})

#add_executable(testGPIO.elf tests/testGPIO.c ${SOURCE_FILES})

add_custom_target(opq.bin
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/
        DEPENDS opq.elf
        COMMAND arm-none-eabi-objcopy -O binary opq.elf opq.bin
        )

set(TESTS tests/testUart.c tests/testGPIO.c)

set(test_bins)
foreach(_file ${TESTS})
    string(REPLACE ".c" ".elf" file_elfed ${_file})
    string(REPLACE "tests/" "" target_name ${file_elfed})
    add_executable(${target_name} tests/testUart.c ${SOURCE_FILES})
    string(REPLACE ".elf" ".bin" target_bin ${target_name})

    add_custom_target( ${target_bin}
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/
            DEPENDS ${target_name}
            COMMAND arm-none-eabi-objcopy -O binary ${target_name} ${target_bin}
            )
    list(APPEND test_bins ${target_bin})
endforeach()

add_custom_target(tests
        DEPENDS ${test_bins}
)

add_custom_target(clean-all
        rm -f opq.map *.bin *.elf
        )
