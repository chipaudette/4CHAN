/*
Uses SPI settings:
 use SPI_MODE0 [0,0] or SPI_MODE3 [1,1]  
 "Data is clocked out of the MCP3912 on the falling edge of SCK,
 and data is clocked into the MCP3912 on the rising edge of SCK.
 In these modes, the SCK clock can idle either high (1,1)
 or low (0,0)." [rtds p.42]
 
 First byte is control, defines address to start and R/W function
 Variable register format (16,24,32)
 Has group read mode (??)
 
 First byte of any transaction is the control byte
 <6:5> 01  device address
 <4:0> 32 register adresses
 R|W bit (read 1, write 0)
 
 SATUSCOM register controls how r|w behaves
 READ <1;0> 
 00 = read the same address
 01 = loop on GROUPS
 10 = loop on TYPES (DEFAULT)
 11 = auto increment 
 WRITE 
 1 = auto increment and loop on writeable part of reg map (DEFAULT)
 0 = continually writes on same address
*/

unsigned long regVal; 

void updateMCPdata(){
  int byteCounter = 0;
   digitalWrite(MCP_SS,LOW);
   sendCommand(channelAddress[CHAN_0],MCP_READ);  // send request to read from CHAN_0 address
   for(int i=0; i<4; i++){        
     channelData[i] = readRegister();  // read the 24bit result into the long variable array
     for(int j=16; j>=0; j-=8){
       rawChannelData[byteCounter] = (channelData[i]>>j & 0xFF);  // fill the raw data array for streaming
       byteCounter++;
     }
   }
   digitalWrite(MCP_SS,HIGH);
   // this section corrects the sign on the long array
   for(int i=0; i<4; i++){  
     if ((channelData[i] & 0x00800000) > 0) {
       channelData[i] |= 0xFF000000;
     } else {
       channelData[i] &= 0x00FFFFFF;
     }
   }
}

// SEND THE DATA WITH THE OPENBCI PROTOCOL
void sendMCPdata(byte sampleNumber){
  Serial.write(0xA0);                // send the pre-fix
  Serial.write(sampleNumber);        // send the sample number
  for(int i=0; i<24; i++){    
    Serial.write(rawChannelData[i]); // send the raw data 8 x 24 bits
  }
  byte zero = 0x00;                  // for some reason, this is necessary
  for(int i=0; i<6; i++){
    Serial.write(zero);              // send fake accel data.
  }
    Serial.write(0xC0);              // send the post-fix
}





void sendCommand(byte address, byte rw){
  byte command = DEV_ADD | address | rw;
  SPI.transfer(command);
}


long readRegister(){

  long thisRegister = SPI.transfer(0x00);
  thisRegister <<= 8;
  thisRegister |= SPI.transfer(0x00);
  thisRegister <<= 8;
  thisRegister |= SPI.transfer(0x00);

  return thisRegister;
}

void writeRegister(unsigned long setting){
  byte thisByte = (setting & 0x00FF0000) >> 16;
  SPI.transfer(thisByte);
  thisByte = (setting & 0x0000FF00) >> 8;
  SPI.transfer(thisByte);
  thisByte = setting & 0x000000FF;
  SPI.transfer(thisByte);
}


void turnOnChannels(){
  digitalWrite(MCP_SS,LOW);
  sendCommand(CONFIG_1,MCP_WRITE);
  writeRegister(channelMask);  // turn on selected channels
  digitalWrite(MCP_SS,HIGH);

}

void turnOffAllChannels(){
  digitalWrite(MCP_SS,LOW);
  sendCommand(CONFIG_1,MCP_WRITE);
  writeRegister(0x0F0000);  // turn off all channels
  digitalWrite(MCP_SS,HIGH);
}

void configMCP3912(unsigned long gain){
  digitalWrite(MCP_SS,LOW);
  sendCommand(GAIN,MCP_WRITE);
  writeRegister(gain);  // GAIN_1, _2, _4, _8, _16, _32
  writeRegister(0xA9000F);  // STATUSCOM auto increment TYPES DR in HIZ
  writeRegister(0x38E050);  // CONFIG0 dither on-full, boost 1, PRE 0:0, OSR 1:1:1, tempcomp | was 0x38650
  writeRegister(0x0F0000);  // put the ADCs in reset, turn on the crystal oscillator
  digitalWrite(MCP_SS,HIGH);
}


void printAllRegisters(){
  for (int i=MOD_VAL; i <=GAINCAL_3; i+=2){
    if(i != 0x12){
      digitalWrite(MCP_SS,LOW);
      sendCommand(i,MCP_READ);
      regVal = readRegister();
      digitalWrite(MCP_SS,HIGH);
      printRegisterName(i);
      Serial.print(" 0x");
      Serial.println(regVal,HEX);
    }
  }
  digitalWrite(MCP_SS,LOW);
  sendCommand(LOK_CRC,MCP_READ);
  regVal = readRegister();
  digitalWrite(MCP_SS,HIGH);
  printRegisterName(LOK_CRC);
  Serial.print(" 0x");
  Serial.println(regVal,HEX); 
}


void printRegisterName(byte _address) {

  switch(_address){
  case MOD_VAL:
    Serial.print("MOD_VAL, "); 
    break;
  case GAIN:
    Serial.print("GAIN, "); 
    break;
  case PHASE:
    Serial.print("PHASE, "); 
    break;
  case STATUSCOM:
    Serial.print("STATUSCOM,"); 
    break;
  case CONFIG_0:
    Serial.print("CONFIG_0, "); 
    break;
  case CONFIG_1:
    Serial.print("CONFIG_1, "); 
    break;
  case OFFCAL_0:
    Serial.print("OFFCAL_0, "); 
    break;
  case GAINCAL_0:
    Serial.print("GAINCAL_0,"); 
    break;
  case OFFCAL_1:
    Serial.print("OFFCAL_1, "); 
    break;
  case GAINCAL_1:
    Serial.print("GAINCAL_1,"); 
    break;
  case OFFCAL_2:
    Serial.print("OFFCAL_2, "); 
    break;
  case GAINCAL_2:
    Serial.print("GAINCAL_2,"); 
    break;
  case OFFCAL_3:
    Serial.print("OFFCAL_3, "); 
    break;
  case GAINCAL_3:
    Serial.print("GAINCAL_3,"); 
    break;
  case LOK_CRC:
    Serial.print("LOK_CRC,  "); 
    break;
  default: 
    break;
  }

}


void runTimedTest(int numSamples){
  Serial.println("starting test");
  int sampleNumber = 0;
  unsigned long sampleTimer = millis();
  turnOnChannels();
  
  while(sampleNumber < numSamples){  // 256 samples per second

    while(digitalRead(DR) == HIGH){}  // wait for DR to go low, signaling data is ready
      updateMCPdata();
      sampleNumber++;
    
      for(int i=0; i<4; i++){
        Serial.print(channelData[i]);
        if(i<3){Serial.print("\t");}  // add the separator
      }
      Serial.println();    // or end the line
    }
    
    sampleTimer = millis() - sampleTimer;
    Serial.print("that took "); 
    Serial.println(sampleTimer);
    timingTest = false;
    turnOffAllChannels();
//    channelMask = 0x0F0000;
}
