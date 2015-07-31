

/*
    Control of MCP3912 AFE IC with data Interpretation and Transmission    
    THIS CODE IS DESIGNED TO TARGET RFduino [Ported from Uno32]
    
 MCP3912 has AD8293G80 with gain 80 (or AD8293G160 gain 160)
 
 
 Made by Joel Murphy, Winter 2015 this was written for Arduino UNO
              Spring 2015 ported to chipKIT Uno32
              Summer 2015 ported to RFduino
             
     Designed to run the OpenBCI V3 protocol

 */

#include <SPI.h>  
#include "Defines.h"


long channelData[4];
byte rawChannelData[24];  // holds raw MCP channel data for sending to program
long channel_0; // 24 bit result is converted to 32bit 2's compliment
long channel_1;
long channel_2;
long channel_3;
byte sampleCounter;


unsigned long channelMask = 0x00000000;  // used to turn on selected channels
unsigned long channelEnable[4] = {ENABLE_0, ENABLE_1, ENABLE_2, ENABLE_3};
unsigned long channelDisable[4] = {DISABLE_0, DISABLE_1, DISABLE_2, DISABLE_3};
byte channelAddress[4] = {CHAN_0,CHAN_1,CHAN_2,CHAN_3};
boolean timingTest = false;  // there is a legacy timied test, check Serial_Stuff for command char trigger

boolean is_running = false;  // is true when streaming data

void setup(){

  Serial.begin(115200);  // works up to 1Mbaud with no radio libraries
  Serial.println("OBCI 4CHAN 03");
  SPI.begin();
  SPI.setFrequency(1000);  // sclk frequency in Kbps MCP max is 20MHz
  SPI.setDataMode(SPI_MODE0);
  pinMode(MCP_SS,OUTPUT);
  digitalWrite(MCP_SS,HIGH);
  pinMode(DR,INPUT);  // DataReady pin goes low when data is ready.

  delay(500);

//  configMCP3912(GAIN_1);
  printAllRegisters();
  for(int i=0; i<24; i++){
    rawChannelData[i] = 0x00;  // seed the raw data array
  }

  sampleCounter = 0x00;
  
}


void loop(){
  
  if(is_running){  
    while(digitalRead(DR) == HIGH){}
    updateMCPdata();
    sendMCPdata(sampleCounter);
    sampleCounter++;
  }

  eventSerial();

}


int changeChannelState_maintainRunningState(int chan, int start){
  boolean is_running_when_called = is_running;
  
  //must stop running to change channel settings
  stopRunning();
  if (start == 1) {
      Serial.print("Activating channel "); Serial.println(chan);
      channelMask &= channelEnable[chan-1];// turn on the channel
  } else {
      Serial.print("Deactivating channel "); Serial.println(chan);
      channelMask |= channelDisable[chan-1];// turn off the channel
  }
  turnOnChannels();  // turn channel on or off
  //restart, if it was running before
  if (is_running_when_called == true) {
    startRunning();
  }
}

boolean stopRunning(void) {
  if(is_running == true){
    turnOffAllChannels();  
    is_running = false;
    }
    return is_running;
  }

boolean startRunning() {
  if(is_running == false){
    turnOnChannels();    
    is_running = true;
  }
    return is_running;
}


void printRegisters(){
  boolean is_running_when_called = is_running;
  stopRunning();
  if(is_running == false){
    printAllRegisters();
  }
  sendEOT();  // end of transmission
  delay(20);
    //restart, if it was running before
  if (is_running_when_called == true) {
    startRunning();
  }
}

void startFromScratch(){
  configMCP3912(GAIN_1);// do the stuff that you do at the start
  printAllRegisters();
  Serial.println("send 'b' to start data stream");
  Serial.println("send 's' to stop data stream");
  Serial.println("use 1,2,3,4 to turn OFF channels");
  Serial.println("use !,@,#,$ to turn ON channels");
  Serial.println("send '?' to print all registers");
  Serial.println("send 'v' to initialize MCP");
  sendEOT();
    
}

void sendEOT(){
  Serial.print("$$$");
}
