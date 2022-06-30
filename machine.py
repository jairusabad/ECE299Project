from fm import Radio
from machine import Pin, SPI, I2C, ADC
import utime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI  # this is the driver library and the corresponding class
import framebuf  # this is another library for the display.


#VARIABLE INITIALIZATIONS
#When a button has a pull up resistor, unpressed state is 1
#button = machine.Pin(0, Pin.IN, Pin.PULL_UP)
fm_radio = Radio( 100.3, 2, False )

pot = machine.ADC(28)

#------------------------------

radioButton = Pin(2, Pin.IN)
radioDirection = Pin(1, Pin.IN, Pin.PULL_UP)
radioStep = Pin(0, Pin.IN, Pin.PULL_UP)
radioState = 0
previous_value = True

#-----SCREEN INITIALIZATION------------------------------------
# Define columns and rows of the oled display. These numbers are the standard values. 
SCREEN_WIDTH = 128  #number of columns
SCREEN_HEIGHT = 64  #number of rows


# Initialize I/O pins associated with the oled display SPI interface

spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico

#
# SPI Device ID can be 0 or 1. It must match the wiring. 
#
SPI_DEVICE = 0 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

#
# initialize the SPI interface for the OLED display
#
oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )

#
# Initialize the display
#
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )

#--------------------------------Functions-------------------------------------

#for button debounce
def ButtonPressed():
    utime.sleep_ms(200)
    if (radioButton.value()!=0):
        return (True)
    else:
        return (False)
    
#-------------------------------Potentiometer----------------------------------
    
#def map(x,in_min, in_max, out_min, out_max):
    
#    return int((x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min)
    
#Reads the Percentage of the Pot relative to its Output Voltage basically another map

def readPotPercent():
    
    x = rawPot()
    percentage = ((x-288)*(100-0)/(65535-288)+0)
    return int (percentage)

def rawPot():
    
    return (pot.read_u16())

#Basically another map but I need it to output a float, THIS IS ONLY FOR THE VOLTAGE OUTPUT OF THE POT

def mapVolt():
    
    return ((readPotPercent()-0)*(3.3-0)/(100-0)+0)
    
    
    
Voltage = 0
    
    
##########################################################################################################################################################    
    
while True:
    
    oled.fill(0)
    
    Settings = fm_radio.GetSettings()
    volume = Settings[1]
    frequency = Settings[2]    
    
# Volume Adjusment Button--------------------------------------------------------------
   
#    if(ButtonPressed()):
        
#        fm_radio.Volume += 1
        #Settings = fm_radio.GetSettings()
#        CurrentVol = Settings[1]
        
#        if(fm_radio.SetVolume(fm_radio.Volume) == True):
#            fm_radio.ProgramRadio()
#            print(CurrentVol)
#        else:
#            fm_radio.Volume = 0
#            fm_radio.ProgramRadio()
#            CurrentVol = 0
    
#
# Frequency and Volume Encoder Algo---------------------------------------------------------------------
#

#--------NEEDS DEBOUNCE---------------------------

    if radioState == 0:
        if(ButtonPressed()):
            radioState = 1
            print("Frequency Control:")
            
        if previous_value != radioStep.value():
            if radioStep.value() == False:
        
                #If Turned Left
                if radioDirection.value() == False:
                    utime.sleep_ms(200)
                    fm_radio.DecreaseVolume(1) 
                    if( fm_radio.SetVolume(fm_radio.Volume) == True ):
                        fm_radio.ProgramRadio()
                        print( "Volume is: %4d" % Settings[1] )
                
                    else:    
                        fm_radio.Volume = 0
                        fm_radio.ProgramRadio()
                        print( "Volume is: %4d" % Settings[1] )
                
                #If Turned Right
                else:
                    utime.sleep_ms(200)
                    fm_radio.IncreaseVolume(1)
                    if( fm_radio.SetVolume(fm_radio.Volume) == True ):
                        fm_radio.ProgramRadio()
                        print( "Volume is: %4d" % Settings[1])
                        
                    else:
                        fm_radio.Volume = 15
                        fm_radio.ProgramRadio()
                        print( "Volume is: %4d" % Settings[1])
                
            previous_value = radioStep.value()
    
    if radioState == 1:
        if(ButtonPressed()):
            radioState = 0
            print ("Volume Control:")

        if previous_value != radioStep.value():
            if radioStep.value() == False:
                
                #If Turned Left
                if radioDirection.value() == False:
                    utime.sleep_ms(200)
                    fm_radio.DecreaseFrequency(1)
                    if( fm_radio.SetFrequency(fm_radio.Frequency) == True):
                        fm_radio.ProgramRadio()
                        print( "Frequency is: %5.1f" % Settings[2])
                    else:    
                        frequency = 88
                        fm_radio.ProgramRadio()
                        print("Frequency is: %5.1f" % frequency)
                
                #If Turned Right
                else:
                    utime.sleep_ms(200)
                    fm_radio.IncreaseFrequency(0.1)
                    if( fm_radio.SetFrequency(fm_radio.Frequency) == True ):
                        fm_radio.ProgramRadio()
                        print("Frequency is: %5.1f" % Settings[2])
                    else:    
                        fm_radio.frequency = 108
                        fm_radio.ProgramRadio()
                        print("Frequency is: %5.1f"  % frequency)
                
            previous_value = radioStep.value()   

# for the Screen---------------------------------------------------------------
#
# Clear the buffer
#
        
#
# Update the text on the screen
#         
                 
    oled.text("FM: %5.1f" % Settings[2], 15, 0) # Print the text starting from 0th column and 0th row
    oled.text("Volume: %d" % Settings[1], 15, 10) # Print the number starting at 45th column and 10th row
    #oled.text("Volume is: %4d" % Settings[1], 0, 30 ) # Print the value stored in the variable Count.
        
#
# Calculates the Voltage Output of Pot relative to the Percentage of the Pot 
#

    Voltage = mapVolt()
    oled.text("Voltage is: %2f" % Voltage, 0, 50, )        

#
# Transfer the buffer to the screen
#
    oled.show()
        
   